from llama_index.core.schema import (
    TransformComponent,
)
from pydantic import ConfigDict, Field

from knowledge_base_mcp.utils.logging import BASE_LOGGER

logger = BASE_LOGGER.getChild(__name__)


class DoclingLargeItemRemoval(TransformComponent):
    """Removes large items from the node metadata."""

    model_config = ConfigDict(use_attribute_docstrings=True, arbitrary_types_allowed=True)

    types_to_remove: list[str] = Field(default=["table", "code"])
    """The types to remove."""

    max_text_size: int = Field(default=10000)
    """The maximum text size to allow for a node."""

    def __call__(self, nodes, **kwargs):  # noqa: ARG002

        nodes_to_keep = []

        for node in nodes:

            label = node.metadata.get("docling_item_label")
            if label is None or label not in self.types_to_remove:
                nodes_to_keep.append(node)
                continue

            content = node.get_content()
            content_size = len(content)

            if content_size > self.max_text_size:
                logger.warning(f"Removing very large {label} node {node.id_} -- text size of {content_size} > {self.max_text_size}: {content[:100]}...")
                continue

            node.excluded_embed_metadata_keys.append("docling_item_label")
            node.excluded_llm_metadata_keys.append("docling_item_label")

            nodes_to_keep.append(node)

        return nodes_to_keep
