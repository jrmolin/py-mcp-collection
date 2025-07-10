import json
from collections.abc import Sequence
from typing import Any, override

from llama_index.core.schema import (
    BaseNode,
    RelatedNodeInfo,
    TransformComponent,
)
from pydantic import ConfigDict, Field


class AddMetadata(TransformComponent):
    """Adds metadata to the node."""

    metadata: dict[str, Any] = Field(default_factory=dict)
    """Metadata to add to the node."""

    include_related_nodes: bool = Field(default=False)
    """Whether to also add metadata to the RelatedNodeInfo object in relationships."""

    @override
    def __call__(self, nodes: Sequence[BaseNode], **kwargs: Any) -> Sequence[BaseNode]:  # pyright: ignore[reportAny]
        for node in nodes:
            node.metadata.update(self.metadata)

            if self.include_related_nodes:
                for relationship in node.relationships.values():
                    if isinstance(relationship, RelatedNodeInfo):
                        relationship.metadata.update(self.metadata)

        return nodes


class IncludeMetadata(TransformComponent):
    """Adds exclusions for all metadata on the node that is not in the include list."""

    model_config: ConfigDict = ConfigDict(arbitrary_types_allowed=True, use_enum_values=True)

    embed_keys: list[str] | None = Field(...)
    """All metadata keys but these will be added to the excluded_embed_metadata_keys list."""

    llm_keys: list[str] | None = Field(...)
    """All metadata keys but these will be added to the excluded_llm_metadata_keys list."""

    @override
    def __call__(self, nodes: Sequence[BaseNode], **kwargs: Any) -> Sequence[BaseNode]:  # pyright: ignore[reportAny]
        for node in nodes:
            if self.embed_keys is not None:
                embed_exclusions = set(node.metadata.keys())
                for key in self.embed_keys:
                    embed_exclusions.discard(key)
                node.excluded_embed_metadata_keys = sorted(embed_exclusions)

            if self.llm_keys is not None:
                llm_exclusions = set(node.metadata.keys())
                for key in self.llm_keys:
                    llm_exclusions.discard(key)
                node.excluded_llm_metadata_keys = sorted(llm_exclusions)

        return nodes


class ExcludeMetadata(TransformComponent):
    """Adds the provided metadata keys to the exclusions for the node."""

    model_config: ConfigDict = ConfigDict(arbitrary_types_allowed=True, use_enum_values=True)

    embed_keys: list[str] | None = Field(default_factory=list)
    """Metadata keys to add to the excluded_embed_metadata_keys list."""

    llm_keys: list[str] | None = Field(default_factory=list)
    """Metadata keys to add to the excluded_llm_metadata_keys list."""

    @override
    def __call__(self, nodes: Sequence[BaseNode], **kwargs: Any) -> Sequence[BaseNode]:  # pyright: ignore[reportAny]
        for node in nodes:
            if self.embed_keys:
                existing_embed_exclusions: set[str] = set(node.excluded_embed_metadata_keys)

                for key in self.embed_keys:
                    existing_embed_exclusions.add(key)

                node.excluded_embed_metadata_keys = sorted(existing_embed_exclusions)

            if self.llm_keys:
                existing_llm_exclusions: set[str] = set(node.excluded_llm_metadata_keys)

                for key in self.llm_keys:
                    existing_llm_exclusions.add(key)

                node.excluded_llm_metadata_keys = sorted(existing_llm_exclusions)

        return nodes


class RenameMetadata(TransformComponent):
    """Renames the provided metadata keys."""

    renames: dict[str, str] = Field(default_factory=dict)
    """Dictionary of metadata keys to rename: old_key -> new_key."""

    include_related_nodes: bool = Field(default=False)
    """Whether to also rename metadata from the RelatedNodeInfo object in relationships."""

    @override
    def __call__(self, nodes: Sequence[BaseNode], **kwargs: Any) -> Sequence[BaseNode]:  # pyright: ignore[reportAny]
        for node in nodes:
            for old_key, new_key in self.renames.items():
                if old_key not in node.metadata:
                    continue
                node.metadata[new_key] = node.metadata.pop(old_key)

            if self.include_related_nodes:
                for relationship in node.relationships.values():
                    if isinstance(relationship, RelatedNodeInfo):
                        for old_key, new_key in self.renames.items():
                            if old_key not in relationship.metadata:
                                continue
                            relationship.metadata[new_key] = relationship.metadata.pop(old_key)

        return nodes


class RemoveMetadata(TransformComponent):
    """Removes the provided metadata keys from the node."""

    removals: list[str] = Field(default_factory=list)
    """Metadata keys to remove from the node."""

    include_related_nodes: bool = Field(default=False)
    """Whether to also remove metadata from the RelatedNodeInfo object in relationships."""

    @override
    def __call__(self, nodes: Sequence[BaseNode], **kwargs: Any) -> Sequence[BaseNode]:  # pyright: ignore[reportAny]
        for node in nodes:
            for key in self.removals:
                node.metadata.pop(key, None)

            if self.include_related_nodes:
                for relationship in node.relationships.values():
                    if isinstance(relationship, RelatedNodeInfo):
                        for key in self.removals:
                            relationship.metadata.pop(key, None)

        return nodes


class FlattenMetadata(TransformComponent):
    """Flattens the provided metadata keys into the node content."""

    include_related_nodes: bool = Field(default=False)
    """Whether to also flatten metadata from the RelatedNodeInfo object in relationships."""

    @override
    def __call__(self, nodes: Sequence[BaseNode], **kwargs: Any) -> Sequence[BaseNode]:  # pyright: ignore[reportAny]
        for node in nodes:
            self._flatten(metadata=node.metadata)

            if self.include_related_nodes:
                for relationship in node.relationships.values():
                    if isinstance(relationship, RelatedNodeInfo):
                        self._flatten(metadata=relationship.metadata)

        return nodes

    def _flatten(self, metadata: dict[str, Any]) -> None:  # pyright: ignore[reportAny]
        for key, value in metadata.items():  # pyright: ignore[reportAny]
            new_value: str | int | float | bool

            if isinstance(value, str | int | float | bool):
                new_value = value

            elif isinstance(value, dict):
                new_value = json.dumps(obj=value)

            elif isinstance(value, list):
                joined_values: list[str] = []
                for item in value:  # pyright: ignore[reportUnknownVariableType]
                    if isinstance(item, str | int | float | bool):
                        joined_values.append(str(item))
                    else:
                        joined_values.append(json.dumps(obj=item))

                new_value = ", ".join(joined_values)

            else:
                new_value = str(value)  # pyright: ignore[reportAny]

            metadata[key] = new_value
