from llama_index.core.schema import (
    MetadataMode,
    TransformComponent,
)
from pydantic import ConfigDict, Field

from knowledge_base_mcp.utils.logging import BASE_LOGGER

logger = BASE_LOGGER.getChild(__name__)


class LargeNodeWarning(TransformComponent):
    """Warns about large nodes."""

    model_config = ConfigDict(use_attribute_docstrings=True, arbitrary_types_allowed=True)

    max_text_size: int = Field(default=1000)
    """The maximum text size to allow for a node."""

    def __call__(self, nodes, **kwargs):  # noqa: ARG002

        for node in nodes:
            content = node.get_content(metadata_mode=MetadataMode.EMBED)
            content_size = len(content)

            if content_size > self.max_text_size:
                logger.warning(f"Node {node.id_} -- size {content_size} > max size {self.max_text_size}: {content[:100]}...")

        return nodes
