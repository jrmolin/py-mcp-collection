from llama_index.core.schema import (
    TransformComponent,
)
from pydantic import ConfigDict, Field

from knowledge_base_mcp.utils.logging import BASE_LOGGER

logger = BASE_LOGGER.getChild(__name__)


class DoclingTagging(TransformComponent):
    """Copies additional metadata from the doc item to the node metadata."""

    model_config = ConfigDict(use_attribute_docstrings=True, arbitrary_types_allowed=True)

    # types_to_tag: list[str] | None = Field(default=None)
    # """The types to tag. If None, all types will be tagged."""

    def __call__(self, nodes, **kwargs):  # noqa: ARG002
        for node in nodes:
            if "doc_items" not in node.metadata or len(node.metadata["doc_items"]) == 0:
                continue

            doc_items = node.metadata["doc_items"]

            if len(doc_items) > 1:
                continue

            doc_item = doc_items[0]

            if label := doc_item.get("label"):
                new_key = "docling_item_label"

                if label in ["table", "code", "text"]:
                    node.metadata[new_key] = label
                    node.excluded_embed_metadata_keys.append(new_key)
                    node.excluded_llm_metadata_keys.append(new_key)

        return nodes