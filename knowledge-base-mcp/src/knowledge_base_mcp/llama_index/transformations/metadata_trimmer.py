from collections.abc import Sequence

from llama_index.core.schema import (
    BaseNode,
    RelatedNodeInfo,
    TransformComponent,
)
from pydantic import Field

from knowledge_base_mcp.utils.logging import BASE_LOGGER

logger = BASE_LOGGER.getChild(__name__)


class MetadataTrimmer(TransformComponent):
    remove_metadata: list[str] = Field(default_factory=list, description="List of metadata keys to remove from the node.")
    exclude_metadata_keys: list[str] = Field(default_factory=list, description="List of metadata keys to exclude from the node.")
    exclude_embed_metadata_keys: list[str] = Field(default_factory=list, description="List of metadata keys to exclude from the node.")
    exclude_llm_metadata_keys: list[str] = Field(default_factory=list, description="List of metadata keys to exclude from the node.")
    rename_metadata_keys: dict[str, str] = Field(default_factory=dict, description="Dictionary of metadata keys to rename.")
    flatten_list_metadata_keys: list[str] = Field(
        default_factory=list, description="List of metadata keys to flatten into the node content."
    )
    remove_metadata_in_relationships: bool = Field(
        default=True, description="Whether to remove metadata from the RelatedNodeInfo object in relationships."
    )

    def __call__(self, nodes: Sequence[BaseNode], **kwargs):  # noqa: ARG002
        for node in nodes:
            self._remove_metadata_from_node(node)

            if self.remove_metadata_in_relationships:
                self._remove_metadata_from_relationships(node)

            self._rename_metadata_keys(node)

            self._flatten_list_metadata(node)

            self._add_metadata_exclusions(node)

        return nodes

    def _rename_metadata_keys(self, node: BaseNode) -> None:
        for old_key, new_key in self.rename_metadata_keys.items():
            if old_key not in node.metadata:
                continue
            node.metadata[new_key] = node.metadata.pop(old_key)

    def _remove_metadata_from_node(self, node: BaseNode) -> None:
        for key in self.remove_metadata:
            if key not in node.metadata:
                continue
            node.metadata.pop(key, None)

    def _remove_metadata_from_relationships(self, node: BaseNode) -> None:
        for relationship in node.relationships.values():
            if isinstance(relationship, RelatedNodeInfo):
                for key in self.remove_metadata:
                    relationship.metadata.pop(key, None)

    def _add_metadata_exclusions(self, node: BaseNode) -> None:
        for key in self.exclude_metadata_keys:
            # if key not in node.metadata:
            #     continue
            node.excluded_embed_metadata_keys.append(key)
            node.excluded_llm_metadata_keys.append(key)

        for key in self.exclude_embed_metadata_keys:
            # if key not in node.metadata:
            #     continue
            node.excluded_embed_metadata_keys.append(key)

        for key in self.exclude_llm_metadata_keys:
            # if key not in node.metadata:
            #     continue
            node.excluded_llm_metadata_keys.append(key)

    def _flatten_list_metadata(self, node: BaseNode) -> None:
        for key in self.flatten_list_metadata_keys:
            if key not in node.metadata:
                continue
            if isinstance(node.metadata[key], list):
                node.metadata[key] = ", ".join(node.metadata[key])
