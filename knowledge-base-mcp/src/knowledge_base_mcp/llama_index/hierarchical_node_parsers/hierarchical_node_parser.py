from abc import ABC
from collections import defaultdict
from collections.abc import Sequence
from hashlib import sha256
from logging import Logger
from typing import Any, override

from llama_index.core.node_parser.interface import NodeParser
from llama_index.core.schema import (
    BaseNode,
    Document,
    MetadataMode,
    Node,
    NodeRelationship,
    ObjectType,
)
from pydantic import Field

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


class GroupNode(Node):
    """A node that represents a group of nodes."""

    member_nodes: list[BaseNode] = Field(default_factory=list, exclude=True)

    @override
    def model_post_init(self, __context: Any) -> None:  # pyright: ignore[reportAny]
        self._refresh_relationships()

    @property
    @override
    def hash(self) -> str:
        doc_identity: str = str(self.get_content()) + str(self.metadata)
        return str(sha256(doc_identity.encode(encoding="utf-8", errors="surrogatepass")).hexdigest())

    @classmethod
    @override
    def get_type(cls) -> str:
        """Get Object type."""
        return ObjectType.TEXT

    def get_content_size(self, metadata_mode: MetadataMode = MetadataMode.NONE) -> int:
        """Get the size of the content of the group node."""
        return len(self.get_content(metadata_mode=metadata_mode))

    def is_root(self) -> bool:
        """Determine if the group node is a root-style node (A node with no parent)."""

        return self.parent_node is None

    def collapse(self, max_group_size: int = 2048, min_group_size: int = 256) -> BaseNode:
        """Collapsing a group node eliminates all group nodes smaller than the max_group_size in its descendant tree.

        All non-group nodes are placed under the collapsed group node."""

        # We can collapse this node into a single group node with all descendant leaf nodes
        if self.get_content_size() < max_group_size:
            self.set_member_nodes(member_nodes=list(self.descendant_nodes(leaf_nodes_only=True)))
            return self

        # If we have one member node, and its also a group node, we collapse it
        if len(self.member_nodes) == 1 and isinstance(self.member_nodes[0], GroupNode):
            self.set_member_nodes(member_nodes=self.member_nodes[0].member_nodes)
            return self

        # We can't collapse this node, but maybe we can collapse its children
        new_member_nodes: list[BaseNode] = []

        for node in self.member_nodes:
            if isinstance(node, GroupNode):
                new_member_nodes.append(node.collapse(max_group_size=max_group_size, min_group_size=min_group_size))
            else:
                new_member_nodes.append(node)

        self.set_member_nodes(member_nodes=new_member_nodes)

        return self

    def set_member_nodes(self, member_nodes: list[BaseNode]) -> None:
        """Set the member nodes."""
        self.member_nodes = member_nodes
        self._refresh_relationships()

    def descendant_nodes(self, leaf_nodes_only: bool = False) -> Sequence[BaseNode]:
        """Get the group node and its descendant nodes."""

        descendant_nodes: Sequence[BaseNode] = []

        for node in self.member_nodes:
            if isinstance(node, GroupNode):
                descendant_nodes.extend(node.descendant_nodes())
            else:
                descendant_nodes.append(node)

        if leaf_nodes_only:
            return [node for node in descendant_nodes if node.child_nodes is None]

        return [self, *descendant_nodes]

    def _refresh_relationships(self) -> None:
        """Refresh the relationships of the group node."""
        reset_parent_child_relationships(parent_node=self, child_nodes=self.member_nodes)
        reset_prev_next_relationships(sibling_nodes=self.member_nodes)


class RootNode(GroupNode):
    pass


class HierarchicalNodeParser(NodeParser, ABC):
    """Base interface for node parser."""

    collapse_nodes: bool = Field(default=False)
    """Whether to collapse nodes."""

    collapse_max_size: int = Field(default=1024)
    """The maximum size of a leaf node in characters when collapsing."""

    collapse_min_size: int = Field(default=256)
    """The minimum size of a leaf node in characters when collapsing."""

    @override
    def _postprocess_parsed_nodes(
        self,
        nodes: list[BaseNode],
        parent_doc_map: dict[str, Document],
    ) -> list[BaseNode]:
        """A parent/child aware postprocessor for hierarchical nodes."""

        all_nodes: list[BaseNode] = nodes.copy()

        if self.collapse_nodes:
            self._collapse_all_nodes_in_place(all_nodes=all_nodes)

            # all_nodes = self._perform_group_small_child_collapsing(all_nodes=all_nodes)

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

    def _collapse_all_nodes_in_place(self, all_nodes: list[BaseNode]) -> None:
        """Perform root node collapsing.

        Returns a tuple of the new nodes and the nodes that were merged."""
        root_nodes: list[GroupNode] = [node for node in all_nodes if isinstance(node, GroupNode) and node.is_root()]

        # Collapse nodes to eliminate groups
        for root_node in root_nodes:
            descendant_nodes: Sequence[BaseNode] = root_node.descendant_nodes()

            for descendant_node in descendant_nodes:
                all_nodes.remove(descendant_node)

            collapsed_root_node: BaseNode = root_node.collapse(max_group_size=self.collapse_max_size, min_group_size=self.collapse_min_size)

            if isinstance(collapsed_root_node, GroupNode):
                new_descendant_nodes: Sequence[BaseNode] = collapsed_root_node.descendant_nodes()

                all_nodes.extend(new_descendant_nodes)
            else:
                all_nodes.append(collapsed_root_node)

    # def _perform_group_small_child_collapsing(self, all_nodes: list[BaseNode]) -> list[BaseNode]:
    #     """Perform group small child collapsing.

    #     Returns a tuple of the new nodes and the nodes that were merged."""

    #     group_nodes: list[GroupNode] = [node for node in all_nodes if isinstance(node, GroupNode)]

    #     for group_node in group_nodes:
    #         new_member_nodes, nodes_merged_away = self._merge_small_nodes(nodes=group_node.member_nodes)

    #         group_node.member_nodes = new_member_nodes
    #         group_node._refresh_relationships()  # pyright: ignore[reportPrivateUsage]

    #         for node_merged_away in nodes_merged_away:
    #             all_nodes.remove(node_merged_away)

    #     return all_nodes

    # def _merge_small_nodes(self, nodes: list[BaseNode]) -> tuple[list[BaseNode], list[BaseNode]]:
    #     """Merge small nodes together. Returns a tuple of the new nodes and the nodes that were merged."""

    #     new_nodes: list[BaseNode] = []

    #     peekable_iterator = PeekableIterator(items=nodes)

    #     nodes_merged_away: list[BaseNode] = []

    #     for node in peekable_iterator:
    #         # If we are at a group node, we can't merge it
    #         if isinstance(node, GroupNode):
    #             new_nodes.append(node)
    #             continue

    #         if node.next_node is None:
    #             new_nodes.append(node)
    #             continue

    #         if _get_node_size(node=node) > self.collapse_max_size:
    #             new_nodes.append(node)
    #             continue

    #         nodes_to_merge: list[BaseNode] = [node]

    #         # Eligible for merging
    #         while peeked_node := peekable_iterator.peek():
    #             # If we are at a group node, we can't merge it
    #             if isinstance(peeked_node, GroupNode):
    #                 new_nodes.append(peeked_node)
    #                 break

    #             peeked_node_size: int = _get_node_size(node=peeked_node)

    #             # Make sure the next node is below our min size
    #             if peeked_node_size > self.collapse_min_size:
    #                 break

    #             # Make sure our potential "merged" node is not too large
    #             nodes_to_merge_size: int = sum(_get_node_size(node=node) for node in nodes_to_merge)

    #             if nodes_to_merge_size + peeked_node_size > self.collapse_max_size:
    #                 break

    #             _ = peekable_iterator.commit_to_peek()

    #             # Try to grab another node!
    #             nodes_to_merge.append(peeked_node)

    #         if len(nodes_to_merge) == 1:
    #             new_nodes.append(node)
    #             continue

    #         # merge the nodes
    #         nodes_merged_away.extend(nodes_to_merge[1:])

    #         new_content = "\n\n".join([node.get_content(metadata_mode=MetadataMode.NONE) for node in nodes_to_merge])

    #         node.set_content(value=new_content)

    #         # Set the next node relationship
    #         if sneaked_node := peekable_iterator.peek(sneak=True):
    #             node.relationships[NodeRelationship.NEXT] = sneaked_node.as_related_node_info()
    #             sneaked_node.relationships[NodeRelationship.PREVIOUS] = node.as_related_node_info()

    #         # or, if there is no next node, remove the next node relationship
    #         elif NodeRelationship.NEXT in node.relationships:
    #             del node.relationships[NodeRelationship.NEXT]

    #         for node_merged_away in nodes_merged_away:
    #             _ = node_merged_away.relationships.pop(NodeRelationship.PREVIOUS, None)
    #             _ = node_merged_away.relationships.pop(NodeRelationship.NEXT, None)
    #             _ = node_merged_away.relationships.pop(NodeRelationship.PARENT, None)

    #         new_nodes.append(node)

    #     return new_nodes, nodes_merged_away

    # Connect the leaf nodes between parent nodes to each other
    # leaf_nodes: list[BaseNode] = [node for node in nodes if node.child_nodes is None]

    # for i, leaf_node in enumerate(leaf_nodes):
    #     if i == 0:
    #         continue

    #     if leaf_node.prev_node and leaf_node.next_node:
    #         continue

    #     previous_node = leaf_nodes[i - 1]

    #     if leaf_node.prev_node is None:
    #         leaf_node.relationships[NodeRelationship.PREVIOUS] = previous_node.as_related_node_info()

    #     if i < len(leaf_nodes) - 1:
    #         next_node = leaf_nodes[i + 1]

    #         if leaf_node.next_node is None:
    #             leaf_node.relationships[NodeRelationship.NEXT] = next_node.as_related_node_info()
