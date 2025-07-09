from collections.abc import Sequence
from functools import cached_property
from logging import Logger
from typing import Any, ClassVar, Literal, override

from llama_index.core.base.embeddings.base import BaseEmbedding, Embedding, mean_agg
from llama_index.core.bridge.pydantic import ConfigDict, Field, SerializeAsAny
from llama_index.core.schema import BaseNode, MediaResource, MetadataMode, Node

from knowledge_base_mcp.llama_index.hierarchical_node_parsers.hierarchical_node_parser import HierarchicalNodeParser
from knowledge_base_mcp.llama_index.utils.node_registry import NodeRegistry
from knowledge_base_mcp.utils.logging import BASE_LOGGER
from knowledge_base_mcp.utils.window import PeekableIterator

logger: Logger = BASE_LOGGER.getChild(suffix=__name__)


class LeafSemanticMergerNodeParser(HierarchicalNodeParser):
    """Semantic node parser.

    Merges nodes together, with each merged node being a group of semantically related nodes."""

    model_config: ClassVar[ConfigDict] = ConfigDict(arbitrary_types_allowed=True, use_attribute_docstrings=True)

    embed_model: SerializeAsAny[BaseEmbedding] = Field(...)
    """The embedding model to use to for semantic comparison"""

    verification_level: Literal["none", "simple", "full"] = Field(default="none")

    # TODO: Implement tokenizer-based token counting
    # tokenizer: Tokenizer = Field(
    #     default=None,
    #     description="The tokenizer to use to count tokens. If None, the tokenizer will be retrieved from the embed_model.",
    # )

    max_token_count: int | None = Field(default=None)
    """The maximum number of tokens to allow in a merged node.
        If None, the limit is retrieved from the embed_model.
        If the embed_model does not have a max_tokens limit, the default is 256."""

    estimate_token_count: bool = Field(default=True)
    """If True, the token count of the accumulated nodes will be estimated by dividing
    the character count by 4. This is significantly faster than calculating the token count
    for each node."""

    embedding_strategy: Literal["average", "max", "recalculate"] = Field(default="average")

    merge_similarity_threshold: float = Field(default=0.60)
    """The percentile of cosine dissimilarity that must be exceeded between a
    node and the next node to form a node.  The smaller this
    number is, the more nodes will be generated"""

    max_dissimilar_nodes: int = Field(default=3)
    """The number of dissimilar nodes in a row before starting a new node. For example
    if this is 3, and we have 3 dissimilar nodes in a row, we will start a new node."""

    @override
    def model_post_init(self, __context: Any) -> None:  # pyright: ignore[reportAny]
        if self.max_token_count is not None:
            return

        model_as_dict = self.embed_model.to_dict()

        if "max_tokens" in model_as_dict:
            self.max_token_count = model_as_dict["max_tokens"]
            return

        self.max_token_count = 256

    @classmethod
    @override
    def class_name(cls) -> str:
        return "LeafSemanticMerger"

    @override
    async def _aparse_nodes(
        self,
        nodes: Sequence[BaseNode],
        show_progress: bool = False,
        **kwargs: Any,  # pyright: ignore[reportAny]
    ) -> list[BaseNode]:
        return self._parse_nodes(nodes=nodes, show_progress=show_progress, **kwargs)

    @override
    def _parse_nodes(
        self,
        nodes: Sequence[BaseNode],
        show_progress: bool = False,
        **kwargs: Any,  # pyright: ignore[reportAny]
    ) -> list[BaseNode]:
        """Asynchronously parse document into nodes."""

        node_registry: NodeRegistry = NodeRegistry(verification_level=self.verification_level, verification_issue_action="warn")

        node_registry.add(nodes=list(nodes))

        for _, children in node_registry.get_leaf_families():
            # We cannot merge if there is only one child node
            if len(children) == 1:
                continue
            # We will use a peekable iterator to iterate over the children
            # A peekable iterator lets us look ahead without consuming so we can determine if we want the node or not
            peekable_iterator: PeekableIterator[BaseNode] = PeekableIterator(items=children)

            for node in peekable_iterator:
                nodes_to_merge: list[BaseNode] = [node]
                nodes_to_merge_size: int = self._count_nodes_tokens(nodes=nodes_to_merge)

                # We will use a list of embeddings to track the embeddings of the nodes we are merging
                similar_node_embeddings: list[Embedding] = [node.get_embedding()]

                # Time to start peeking
                while peek_node := peekable_iterator.peek():
                    # We can use the size of the peek window as our # of dissimilar nodes so far
                    # If we hit our threshold, we'll break out of the iterator
                    # and any peeked nodes will be automatically "returned" to the iterator
                    if len(peekable_iterator.repeek()) > self.max_dissimilar_nodes:
                        break

                    # We need to make sure we aren't going to exceed the max token count by adding more nodes
                    pending_nodes_size: int = self._count_nodes_tokens(nodes=peekable_iterator.repeek())

                    if nodes_to_merge_size + pending_nodes_size > self._max_token_count:
                        break

                    # First check the similarity to the first node in the window
                    similarity_to_first_node: float = self._node_embeddings_similarity(node=peek_node, embedding=similar_node_embeddings[0])

                    if similarity_to_first_node < self.merge_similarity_threshold:
                        # Then check the similarity to the last similar node in the window
                        similarity_to_last_node: float = self._embeddings_similarity(
                            embedding=peek_node.get_embedding(),
                            other_embedding=similar_node_embeddings[-1],
                        )

                        if similarity_to_last_node < self.merge_similarity_threshold:
                            # This is a dissimilar node, but we'll check more nodes before deciding whether to keep it
                            continue

                    # We have a similar node! Add it to the list of nodes to merge
                    similar_node_embeddings.append(peek_node.get_embedding())

                    # Also add any dissimilar nodes that we encountered along the way
                    nodes_to_merge.extend(peekable_iterator.repeek())

                    # Update the size of the nodes to merge
                    nodes_to_merge_size += self._count_nodes_tokens(nodes=peekable_iterator.repeek())

                    # Tell the iterator to consume any peeked nodes that we are keeping
                    # So that the next iteration starts at at the first node after the peeked nodes
                    _ = peekable_iterator.commit_to_peek()

                # If we only have one node to merge, we can't merge it
                if len(nodes_to_merge) == 1:
                    continue

                reference_node: BaseNode = nodes_to_merge[0]
                other_nodes: list[BaseNode] = nodes_to_merge[1:]

                new_node = self._merge_nodes(reference_node=reference_node, other_nodes=other_nodes, use_embeddings=similar_node_embeddings)

                node_registry.replace_node(node=reference_node, replacement_node=new_node)

                node_registry.remove(nodes=other_nodes)

        return list(node_registry.get())

    def _node_similarity(self, node: BaseNode, other_node: BaseNode) -> float:
        """Calculate the similarity between two nodes."""

        return self.embed_model.similarity(node.get_embedding(), other_node.get_embedding())

    def _node_embeddings_similarity(self, node: BaseNode, embedding: Embedding) -> float:
        """Calculate the similarity between two nodes."""

        return self.embed_model.similarity(node.get_embedding(), embedding)

    def _embeddings_similarity(self, embedding: Embedding, other_embedding: Embedding) -> float:
        """Calculate the similarity between a list of embeddings."""
        return self.embed_model.similarity(embedding, other_embedding)

    def _merge_nodes(self, reference_node: BaseNode, other_nodes: Sequence[BaseNode], use_embeddings: list[Embedding]) -> BaseNode:
        """Merge nodes together into a common node. Inlining any embeddable metadata that is not common to all nodes."""

        all_nodes: list[BaseNode] = [reference_node, *other_nodes]

        new_content: str = "\n\n".join([self._get_embeddable_content(node=node) for node in all_nodes])

        new_metadata: dict[str, Any] = reference_node.metadata.copy()

        return Node(
            text_resource=MediaResource(text=new_content),
            extra_info=new_metadata,
            embedding=self._combine_embeddings(embeddings=use_embeddings),
        )

    def _count_nodes_tokens(self, nodes: Sequence[BaseNode]) -> int:
        """Count the number of tokens in a node."""

        if not self.estimate_token_count:
            msg = "Non-estimated token counting is not implemented yet"
            raise NotImplementedError(msg)

        token_counts: list[int] = [len(self._get_embeddable_content(node=node)) for node in nodes]

        return sum(token_counts) // 4

    def _get_embeddable_content(self, node: BaseNode) -> str:
        """Get the embeddable content of a node."""
        return node.get_content(metadata_mode=MetadataMode.NONE)

    @cached_property
    def _max_token_count(self) -> int:
        """Get the maximum number of tokens to allow in a merged node."""
        if self.max_token_count is not None:
            return self.max_token_count

        model_as_dict: dict[str, Any] = self.embed_model.to_dict()

        if "max_tokens" in model_as_dict and isinstance(model_as_dict["max_tokens"], int):
            return model_as_dict["max_tokens"]

        return 256

    def _combine_embeddings(self, embeddings: list[Embedding] | None = None, nodes: Sequence[BaseNode] | None = None) -> Embedding:
        """Combine a list of embeddings into a single embedding."""

        all_embeddings: list[Embedding] = []

        if embeddings is not None:
            all_embeddings.extend(embeddings)

        if nodes is not None:
            all_embeddings.extend([node.get_embedding() for node in nodes])

        if self.embedding_strategy == "average":
            return mean_agg(all_embeddings)

        return [max(embedding) for embedding in zip(*all_embeddings, strict=True)]

    async def _arecalculate_embeddings(self, nodes: Sequence[BaseNode]) -> None:
        """Recalculate the embeddings for a list of nodes."""

        _ = await self.embed_model.acall(nodes=nodes)

    def _recalculate_embeddings(self, nodes: Sequence[BaseNode]) -> None:
        """Recalculate the embeddings for a list of nodes."""

        _ = self.embed_model(nodes=nodes)
