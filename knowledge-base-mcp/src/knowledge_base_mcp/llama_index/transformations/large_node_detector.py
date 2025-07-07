from collections.abc import Sequence
from logging import Logger
from typing import Any, ClassVar, Literal, override

from llama_index.core.embeddings import BaseEmbedding
from llama_index.core.schema import (
    BaseNode,
    Document,
    MetadataMode,
    TransformComponent,
)
from pydantic import ConfigDict, Field

from knowledge_base_mcp.utils.logging import BASE_LOGGER

logger: Logger = BASE_LOGGER.getChild(__name__)


class LargeNodeDetector(TransformComponent):
    """Warns about large nodes."""

    model_config: ClassVar[ConfigDict] = ConfigDict(use_attribute_docstrings=True, arbitrary_types_allowed=True)

    max_size: int = Field(default=4096)
    """The maximum size of a node in characters."""

    node_type: Literal["leaf", "all"] = Field(default="all")
    """The type of node to warn about."""

    print_content: bool = Field(default=True)
    """Whether to print the content of large nodes."""

    exclude: bool = Field(default=False)
    """Whether to exclude large nodes."""

    @classmethod
    def from_embed_model(
        cls, embed_model: BaseEmbedding, node_type: Literal["leaf", "all"] = "all", exclude: bool = False, extra_size: int = 0
    ) -> "LargeNodeDetector":
        model_as_dict: dict[str, Any] = embed_model.to_dict()

        max_length: Any | None = model_as_dict.get("max_length")

        max_size = (max_length * 4) if isinstance(max_length, int) else 4096
        return cls(max_size=max_size + extra_size, node_type=node_type, exclude=exclude)

    @override
    def __call__(self, nodes: Sequence[BaseNode], **kwargs: Any) -> Sequence[BaseNode]:  # pyright: ignore[reportAny]
        """Warn about large nodes."""

        new_nodes: list[BaseNode] = []

        for node in nodes:
            content: str = node.get_content(metadata_mode=MetadataMode.EMBED)
            content_size: int = len(content)

            node_is_leaf: bool = not isinstance(node, Document) and (node.child_nodes is None or len(node.child_nodes) == 0)
            node_type_matches: bool = self.node_type == "all" or (self.node_type == "leaf" and node_is_leaf)

            if content_size > self.max_size and node_type_matches:
                action: str = "Excluding" if self.exclude else "Warning"

                content_to_print: str = content[:100] if self.print_content else ""
                logger.warning(msg=f"{action} Node {node.id_} -- size {content_size} > max size {self.max_size}: {content_to_print}...")

                if self.exclude:
                    continue

            new_nodes.append(node)

        return new_nodes
