from collections.abc import Sequence
from logging import Logger
from typing import Any, ClassVar, Literal, override

from llama_index.core.bridge.pydantic import ConfigDict, Field
from llama_index.core.schema import BaseNode

from knowledge_base_mcp.llama_index.hierarchical_node_parsers.hierarchical_node_parser import HierarchicalNodeParser
from knowledge_base_mcp.llama_index.utils.node_registry import NodeRegistry
from knowledge_base_mcp.utils.logging import BASE_LOGGER

logger: Logger = BASE_LOGGER.getChild(suffix=__name__)


class CollapseSmallFamilies(HierarchicalNodeParser):
    """Collapse small families node parser."""

    model_config: ClassVar[ConfigDict] = ConfigDict(arbitrary_types_allowed=True, use_attribute_docstrings=True)

    verification_level: Literal["none", "simple", "full"] = Field(default="none")

    verification_issue_action: Literal["error", "warn"] = Field(default="error")

    @classmethod
    @override
    def class_name(cls) -> str:
        return "CollapseSmallFamilies"

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

        node_registry: NodeRegistry = NodeRegistry(
            verification_level=self.verification_level, verification_issue_action=self.verification_issue_action
        )

        node_registry.add(nodes=list(nodes))

        for parent in node_registry.get_solo_parents():
            node_registry.collapse_node(node=parent)

        return node_registry.get()
