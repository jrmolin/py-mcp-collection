from abc import ABC
from collections import defaultdict
from collections.abc import Sequence
from logging import Logger
from typing import override

from llama_index.core.node_parser.interface import NodeParser
from llama_index.core.schema import (
    BaseNode,
    Document,
    NodeRelationship,
)

from knowledge_base_mcp.utils.logging import BASE_LOGGER

logger: Logger = BASE_LOGGER.getChild(suffix=__name__)


def reset_prev_next_relationships(sibling_nodes: Sequence[BaseNode]) -> None:
    sibling_node_count: int = len(sibling_nodes)

    for i, sibling_node in enumerate(sibling_nodes):
        if i == 0 and sibling_node.prev_node:
            del sibling_node.relationships[NodeRelationship.PREVIOUS]

        if i > 0:
            previous_node: BaseNode = sibling_nodes[i - 1]
            sibling_node.relationships[NodeRelationship.PREVIOUS] = previous_node.as_related_node_info()

        if i < sibling_node_count - 1:
            next_node: BaseNode = sibling_nodes[i + 1]
            sibling_node.relationships[NodeRelationship.NEXT] = next_node.as_related_node_info()

        if i == sibling_node_count - 1 and sibling_node.next_node:
            del sibling_node.relationships[NodeRelationship.NEXT]


def reset_parent_child_relationships(parent_node: BaseNode, child_nodes: Sequence[BaseNode]) -> None:
    """Reset the parent/child relationships of the child nodes."""

    if len(child_nodes) == 0:
        if parent_node.child_nodes:
            del parent_node.relationships[NodeRelationship.CHILD]
        return

    for child_node in child_nodes:
        child_node.relationships[NodeRelationship.PARENT] = parent_node.as_related_node_info()

    parent_node.relationships[NodeRelationship.CHILD] = [child_node.as_related_node_info() for child_node in child_nodes]


class HierarchicalNodeParser(NodeParser, ABC):
    """Base interface for node parser."""

    # collapse_nodes: bool = Field(default=False)
    # """Whether to collapse nodes."""

    # collapse_max_size: int = Field(default=1024)
    # """The maximum size of a leaf node in characters when collapsing."""

    # collapse_min_size: int = Field(default=256)
    # """The minimum size of a leaf node in characters when collapsing."""

    @override
    def _postprocess_parsed_nodes(
        self,
        nodes: list[BaseNode],
        parent_doc_map: dict[str, Document],
    ) -> list[BaseNode]:
        """A parent/child aware postprocessor for hierarchical nodes."""

        all_nodes: list[BaseNode] = nodes.copy()

        # Clean-up all node relationships
        nodes_by_parent_id: dict[str, list[BaseNode]] = defaultdict(list)
        nodes_by_id: dict[str, BaseNode] = {node.node_id: node for node in all_nodes}

        for node in all_nodes:
            if node.parent_node is not None:
                nodes_by_parent_id[node.parent_node.node_id].append(node)

        for parent_id, child_nodes in nodes_by_parent_id.items():
            if parent_id not in nodes_by_id:
                logger.error(msg=f"Parent node {parent_id} not found in nodes_by_id")

            parent_node: BaseNode = nodes_by_id[parent_id]

            # Propagate the source node to the child nodes
            if source_node := parent_node.source_node:
                for child_node in child_nodes:
                    child_node.relationships[NodeRelationship.SOURCE] = source_node

            # Make sure the child / parent relationships are set
            reset_parent_child_relationships(parent_node=parent_node, child_nodes=child_nodes)

            # Make sure the sibling relationships are set
            reset_prev_next_relationships(sibling_nodes=child_nodes)

        if self.include_metadata:
            for node in all_nodes:
                if node.source_node is not None:
                    node.metadata = {**node.source_node.metadata, **node.metadata}

        return all_nodes

    def _establish_sibling_relationships(self, sibling_nodes: Sequence[BaseNode]) -> None:
        """Establish the sibling relationships for the sibling nodes."""
        reset_prev_next_relationships(sibling_nodes=sibling_nodes)

    def _establish_parent_child_relationships(self, parent: BaseNode, child_nodes: Sequence[BaseNode]) -> None:
        """Establish the parent/child relationships for the child nodes."""

        for child_node in child_nodes:
            child_node.relationships[NodeRelationship.PARENT] = parent.as_related_node_info()

        parent.relationships[NodeRelationship.CHILD] = [child_node.as_related_node_info() for child_node in child_nodes]
