from collections.abc import Sequence
from logging import Logger
from typing import Any, ClassVar, override

from llama_index.core.embeddings import BaseEmbedding
from llama_index.core.schema import (
    BaseNode,
    Document,
    TransformComponent,
)
from pydantic import ConfigDict, Field

from knowledge_base_mcp.utils.logging import BASE_LOGGER

logger: Logger = BASE_LOGGER.getChild(__name__)

LARGE_BATCH_SIZE_THRESHOLD = 1000


class BatchedNodeEmbedding(TransformComponent):
    """Embeds nodes in sequential batches."""

    model_config: ClassVar[ConfigDict] = ConfigDict(use_attribute_docstrings=True, arbitrary_types_allowed=True)

    batch_size: int = Field(default=64, description="The number of nodes to embed in each batch.")

    leaf_node_only: bool = Field(default=False, description="Whether to only embed leaf nodes.")

    embed_model: BaseEmbedding

    def _get_batches(self, nodes: Sequence[BaseNode]) -> list[Sequence[BaseNode]]:
        """Get batches of nodes."""

        if self.leaf_node_only:
            leaf_nodes: list[BaseNode] = [node for node in nodes if node.child_nodes is None and not isinstance(node, Document)]
        else:
            leaf_nodes = list(nodes)

        if len(leaf_nodes) > LARGE_BATCH_SIZE_THRESHOLD:
            logger.warning(f"Large batch of {len(leaf_nodes)} leaf nodes, embedding in batches of {self.batch_size}")

        return [leaf_nodes[i : i + self.batch_size] for i in range(0, len(leaf_nodes), self.batch_size)]

    @override
    def __call__(self, nodes: Sequence[BaseNode], **kwargs: Any) -> Sequence[BaseNode]:  # pyright: ignore[reportAny]
        """Embed the leaf nodes."""

        for batch in self._get_batches(nodes=nodes):
            _ = self.embed_model(nodes=batch)

        return nodes

    @override
    async def acall(self, nodes: Sequence[BaseNode], **kwargs: Any) -> Sequence[BaseNode]:  # pyright: ignore[reportAny]
        """Async embed the leaf nodes."""

        for batch in self._get_batches(nodes=nodes):
            _ = await self.embed_model.acall(nodes=batch)

        return nodes


class LeafNodeOnlyFilter(TransformComponent):
    """Filters out non-leaf nodes."""

    model_config: ClassVar[ConfigDict] = ConfigDict(use_attribute_docstrings=True, arbitrary_types_allowed=True)

    @override
    def __call__(self, nodes: Sequence[BaseNode], **kwargs: Any) -> Sequence[BaseNode]:  # pyright: ignore[reportAny]
        """Filter out non-leaf nodes."""

        leaf_nodes: list[BaseNode] = [node for node in nodes if node.child_nodes is None]

        return leaf_nodes


class NonLeafNodeOnlyFilter(TransformComponent):
    """Filters out non-leaf nodes."""

    model_config: ClassVar[ConfigDict] = ConfigDict(use_attribute_docstrings=True, arbitrary_types_allowed=True)

    @override
    def __call__(self, nodes: Sequence[BaseNode], **kwargs: Any) -> Sequence[BaseNode]:  # pyright: ignore[reportAny]
        """Filter out leaf nodes."""

        non_leaf_nodes: list[BaseNode] = [node for node in nodes if node.child_nodes is not None]

        return non_leaf_nodes
