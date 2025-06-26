from collections.abc import Callable, Sequence
from functools import cached_property
from typing import Any, Literal

from llama_index.core.base.embeddings.base import BaseEmbedding, Embedding, mean_agg
from llama_index.core.bridge.pydantic import ConfigDict, Field, SerializeAsAny
from llama_index.core.callbacks.base import CallbackManager
from llama_index.core.node_parser import NodeParser
from llama_index.core.node_parser.node_utils import (
    default_id_func,
)
from llama_index.core.schema import BaseNode, Document, MediaResource, MetadataMode, Node, NodeRelationship

from knowledge_base_mcp.utils.window import PeekableWindow


class SemanticMergerNodeParser(NodeParser):
    """Semantic node parser.

    Merges nodes together, with each merged node being a group of semantically related nodes."""

    model_config = ConfigDict(arbitrary_types_allowed=True, use_attribute_docstrings=True)

    embed_model: SerializeAsAny[BaseEmbedding] = Field(...)
    """The embedding model to use to for semantic comparison"""

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

    metadata_matching: list[str] = Field(default_factory=list)
    """The metadata keys which must match for nodes to be merged"""

    merge_similarity_threshold: float = Field(default=0.60)
    """The percentile of cosine dissimilarity that must be exceeded between a
    node and the next node to form a node.  The smaller this
    number is, the more nodes will be generated"""

    max_dissimilar_nodes: int = Field(default=3)
    """The number of dissimilar nodes in a row before starting a new node. For example
    if this is 3, and we have 3 dissimilar nodes in a row, we will start a new node."""

    def model_post_init(self, __context: Any) -> None:
        if self.max_token_count is not None:
            return

        model_as_dict = self.embed_model.to_dict()

        if "max_tokens" in model_as_dict:
            self.max_token_count = model_as_dict["max_tokens"]
            return

        self.max_token_count = 256

    @classmethod
    def class_name(cls) -> str:
        return "SemanticMergerNodeParser"

    @classmethod
    def from_defaults(
        cls,
        embed_model: BaseEmbedding,
        metadata_matching: list[str],
        merge_similarity_threshold: float,
        max_dissimilar_nodes: int,
        callback_manager: CallbackManager | None = None,
        id_func: Callable[[int, Document], str] | None = None,
    ) -> "SemanticMergerNodeParser":
        callback_manager = callback_manager or CallbackManager([])

        id_func = id_func or default_id_func

        return cls(
            embed_model=embed_model,
            metadata_matching=metadata_matching,
            merge_similarity_threshold=merge_similarity_threshold,
            max_dissimilar_nodes=max_dissimilar_nodes,
            callback_manager=callback_manager,
            id_func=id_func,
        )

    def _parse_nodes(
        self,
        nodes: Sequence[BaseNode],
        show_progress: bool = False,  # noqa: ARG002
        **kwargs: Any,  # noqa: ARG002
    ) -> list[BaseNode]:
        """Asynchronously parse document into nodes."""

        all_nodes: Sequence[BaseNode] = self._group_nodes_semantically(nodes)

        if self.embedding_strategy == "recalculate":
            nodes_with_missing_embeddings = [node for node in all_nodes if node.embedding is None]

            self._recalculate_embeddings(nodes_with_missing_embeddings)

        return list(all_nodes)

    async def _aparse_nodes(
        self,
        nodes: Sequence[BaseNode],
        show_progress: bool = False,  # noqa: ARG002
        **kwargs: Any,  # noqa: ARG002
    ) -> list[BaseNode]:
        """Asynchronously parse document into nodes."""

        all_nodes: Sequence[BaseNode] = self._group_nodes_semantically(nodes)

        if self.embedding_strategy == "recalculate":
            nodes_with_missing_embeddings = [node for node in all_nodes if node.embedding is None]

            await self._arecalculate_embeddings(nodes_with_missing_embeddings)

        return list(all_nodes)

    def _group_nodes_semantically(self, nodes: Sequence[BaseNode]) -> Sequence[BaseNode]:
        """Takes a list of candidate nodes, which have already been evaluated that they match our merging conditions (metadata keys)
        and merges them together into a series of semantically related nodes.

        We do this by:
        1. Calculating the cosine similarity between each node and the next node
        2. If the similarity is greater than the threshold, we add the nodes to the accumulated nodes list
           a. If the token count of the accumulated nodes is greater than the threshold, we build a merged node.
        3. If the similarity is less than the threshold, we add the nodes to the dissimilar nodes list
           a. If the number of dissimilar nodes is greater than the threshold count, we build a merged node
           without the dissimilar nodes and start accumulating nodes again
        4. We repeat this process until we have no more nodes to process

        Args:
            nodes (list[BaseNode]): The nodes to merge

        Returns:
            list[BaseNode]: The merged nodes
        """
        new_nodes: list[BaseNode] = []

        for window in PeekableWindow[BaseNode](items=nodes):
            node = window.look_one()

            node_metadata = {key: node.metadata[key] for key in self.metadata_matching if node.metadata.get(key) is not None}

            similar_nodes: list[BaseNode] = [node]

            window_token_count: int = self._count_text_tokens(text=node.get_content(metadata_mode=MetadataMode.EMBED))

            while peek_node := window.peek_right():
                # Make sure we don't have too many dissimilar nodes in a row
                if window.pright > self.max_dissimilar_nodes:
                    break

                # Make sure we don't have too many tokens in the window
                _, right_peek = window.peek()
                if window_token_count + self._count_nodes_tokens(right_peek) > self._max_token_count:
                    break

                # Make sure the new node has the same metadata as the previous nodes
                if not all(node_metadata.get(key) == peek_node.metadata.get(key) for key in self.metadata_matching):
                    break

                #Make sure the nodes are similar to either the previous node or the mean of the previous nodes
                #previous_node_similarity = self._node_similarity(peek_node, similar_nodes[-1])
                #mean_node_similarity = self._node_embeddings_similarity(peek_node, self._combine_embeddings(nodes=similar_nodes))

                # print("--------------------------------")
                # print(f"Node: {node.node_id}")
                # print(f"Peek node: {peek_node.get_content()[:100]}")
                # print(f"Previous node similarity: {previous_node_similarity}")
                # print(f"Mean node similarity: {mean_node_similarity}")
                # print("--------------------------------")

                if (
                    # Check for similarity to our previous similar node
                    self._node_similarity(peek_node, similar_nodes[-1]) < self.merge_similarity_threshold
                    # Check for similarity to the mean of our previous similar nodes
                    and self._node_embeddings_similarity(peek_node, self._combine_embeddings(nodes=similar_nodes)) < self.merge_similarity_threshold
                ):
                    continue

                similar_nodes.append(peek_node)

                # We have found a similar node! Grow the window to include the new node and any in between nodes.
                window_token_count += self._count_nodes_tokens(right_peek)
                window.grow_to_peek()

            new_node = self._merge_nodes(node_metadata, window.look(), [node.get_embedding() for node in similar_nodes])

            new_nodes.append(new_node)

        # for new_node in new_nodes:
        #     none = new_node.get_content(metadata_mode=MetadataMode.NONE)
        #     llm = new_node.get_content(metadata_mode=MetadataMode.LLM)
        #     embed = new_node.get_content(metadata_mode=MetadataMode.EMBED)
        #     if any(len(content) > 1000 for content in [none, llm, embed]):
        #         print(f"{new_node.id_}: none: {len(none)} llm: {len(llm)} embed: {len(embed)}")

        return new_nodes

    # def _score_above_threshold(self, *scores: float) -> bool:
    #     """Check if any scores are above a threshold."""
    #     return any(score > self.merge_similarity_threshold for score in scores)

    def _node_similarity(self, node: BaseNode, other_node: BaseNode) -> float:
        """Calculate the similarity between two nodes."""

        return self.embed_model.similarity(node.get_embedding(), other_node.get_embedding())

    def _node_embeddings_similarity(self, node: BaseNode, embedding: Embedding) -> float:
        """Calculate the similarity between two nodes."""

        return self.embed_model.similarity(node.get_embedding(), embedding)

    def _merge_nodes(self, metadata: dict[str, Any], nodes: Sequence[BaseNode], use_embeddings: list[Embedding]) -> BaseNode:
        """Merge nodes together into a common node. Inlining any embeddable metadata that is not common to all nodes."""

        reference_node = nodes[0]

        if len(nodes) == 1:
            return reference_node

        # for key in self.metadata_matching:
        #     new_node_metadata[key] = reference_node.metadata[key]

        all_content: list[str] = [self._get_embeddable_content(node=node) for node in nodes]

        # for node in nodes:
        #     original_metadata = node.metadata.copy()

        #     for key in self.metadata_matching:
        #         node.metadata.pop(key, None)

        #     all_content.append(node.get_content(metadata_mode=MetadataMode.EMBED))

        #     node.metadata = original_metadata

        new_node = Node(
            text_resource=MediaResource(text="\n\n".join(all_content)),
        )

        if reference_node.source_node is not None:
            new_node.relationships[NodeRelationship.SOURCE] = reference_node.source_node

        if self.embedding_strategy != "recalculate":
            new_node.embedding = self._combine_embeddings(embeddings=use_embeddings)

        new_node.metadata = metadata

        return new_node

    def _count_nodes_tokens(self, nodes: Sequence[BaseNode]) -> int:
        """Count the number of tokens in a node."""
        return sum(self._count_node_tokens(node=node) for node in nodes)

    def _count_node_tokens(self, node: BaseNode) -> int:
        """Count the number of tokens in a node."""
        embeddable_content = self._get_embeddable_content(node=node)

        return self._count_text_tokens(text=embeddable_content)

    def _count_text_tokens(self, text: str) -> int:
        """Count the number of tokens in a text."""

        if self.estimate_token_count:
            return len(text) // 4

        msg = "Non-estimated token counting is not implemented yet"
        raise NotImplementedError(msg)

    def _get_embeddable_content(self, node: BaseNode) -> str:
        """Get the embeddable content of a node."""
        original_exclude = node.excluded_embed_metadata_keys

        # These metadata keys will be on the new node, so we don't want to include them in the embeddable content
        node.excluded_embed_metadata_keys.extend(self.metadata_matching)

        embeddable_content = node.get_content(metadata_mode=MetadataMode.EMBED)

        node.excluded_embed_metadata_keys = original_exclude

        return embeddable_content

    @cached_property
    def _max_token_count(self) -> int:
        """Get the maximum number of tokens to allow in a merged node."""
        if self.max_token_count is not None:
            return self.max_token_count

        model_as_dict = self.embed_model.to_dict()

        if "max_tokens" in model_as_dict:
            return model_as_dict["max_tokens"]

        return 256

    def _combine_embeddings(self, embeddings: list[Embedding] | None = None, nodes: Sequence[BaseNode] | None = None) -> Embedding:
        """Combine a list of embeddings into a single embedding."""

        all_embeddings = []

        if embeddings is not None:
            all_embeddings.extend(embeddings)

        if nodes is not None:
            all_embeddings.extend([node.get_embedding() for node in nodes])

        if self.embedding_strategy == "average":
            return mean_agg(all_embeddings)

        return [max(embedding) for embedding in zip(*all_embeddings, strict=True)]

    async def _arecalculate_embeddings(self, nodes: Sequence[BaseNode]) -> None:
        """Recalculate the embeddings for a list of nodes."""

        await self.embed_model.acall(nodes=nodes)

    def _recalculate_embeddings(self, nodes: Sequence[BaseNode]) -> None:
        """Recalculate the embeddings for a list of nodes."""

        self.embed_model(nodes=nodes)
