from collections.abc import Sequence
from logging import Logger
from typing import Any, ClassVar, override

from llama_index.core.embeddings import BaseEmbedding
from llama_index.core.schema import (
    BaseNode,
    Document,
    TransformComponent,
)
from pydantic import ConfigDict

from knowledge_base_mcp.utils.logging import BASE_LOGGER

logger: Logger = BASE_LOGGER.getChild(__name__)


class LeafNodeEmbedding(TransformComponent):
    """Embeds leaf nodes."""

    model_config: ClassVar[ConfigDict] = ConfigDict(use_attribute_docstrings=True, arbitrary_types_allowed=True)

    embed_model: BaseEmbedding

    @override
    def __call__(self, nodes: Sequence[BaseNode], **kwargs: Any) -> Sequence[BaseNode]:  # pyright: ignore[reportAny]
        """Embed the leaf nodes."""

        leaf_nodes: list[BaseNode] = [node for node in nodes if node.child_nodes is None and not isinstance(node, Document)]

        logger.info(f"Sync embedding {len(leaf_nodes)} leaf nodes")
        _ = self.embed_model(nodes=leaf_nodes)
        logger.info(f"Sync embedded {len(leaf_nodes)} leaf nodes")

        return nodes

    @override
    async def acall(self, nodes: Sequence[BaseNode], **kwargs: Any) -> Sequence[BaseNode]:  # pyright: ignore[reportAny]
        """Async embed the leaf nodes."""

        leaf_nodes: list[BaseNode] = [node for node in nodes if (node.child_nodes is None or len(node.child_nodes) == 0) and not isinstance(node, Document)]

        if len(leaf_nodes) > 1000:
            logger.warning(f"Async embedding {len(leaf_nodes)} leaf nodes")

        #logger.info(f"Async embedding {len(leaf_nodes)} leaf nodes")
        # Create batches of 128 nodes so we can do them sequentially vs llama doing them in parallel
        batches = [leaf_nodes[i:i + 256] for i in range(0, len(leaf_nodes), 256)]
        for batch in batches:
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
