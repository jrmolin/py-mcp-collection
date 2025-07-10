import sys
from collections import defaultdict
from typing import ClassVar, Literal, Self, overload

from llama_index.core.schema import BaseNode, NodeRelationship, RelatedNodeInfo
from pydantic import BaseModel, ConfigDict, PrivateAttr

from knowledge_base_mcp.utils.logging import BASE_LOGGER

logger = BASE_LOGGER.getChild(__name__)


def is_debugging():
    """
    Checks if a Python debugger is currently active.
    """
    return hasattr(sys, "gettrace") and sys.gettrace() is not None


def related_node_info_as_list(related_node_info: RelatedNodeInfo | list[RelatedNodeInfo]) -> list[RelatedNodeInfo]:
    if isinstance(related_node_info, RelatedNodeInfo):
        return [related_node_info]
    return related_node_info


def order_nodes(nodes: list[BaseNode]) -> list[BaseNode]:
    """Order the nodes by their prev/next relationships."""
    if not nodes:
        return []

    nodes_to_order: list[BaseNode] = nodes.copy()

    nodes_by_id: dict[str, BaseNode] = {node.node_id: node for node in nodes_to_order}

    ordered_nodes: list[BaseNode] = []

    current_node: BaseNode | None = nodes_to_order[0]

    while current_node:
        ordered_nodes.append(current_node)

        if current_node.next_node:
            # We have reached a node that is not in our list, time to break!
            if current_node.next_node.node_id not in nodes_by_id:
                break

            current_node = nodes_by_id[current_node.next_node.node_id]

        else:
            current_node = None

    if len(ordered_nodes) != len(nodes):
        msg = "Asked to order nodes that are not connected."
        raise ValueError(msg)

    return ordered_nodes


def _transfer_next(source_node: BaseNode, target_node: BaseNode, next_node: BaseNode | None = None) -> None:
    """Transfer the next node of a node to another node. This does not change any other relationships."""
    if source_node.next_node and next_node:
        target_node.relationships[NodeRelationship.NEXT] = source_node.next_node
        _set_node_previous(node=next_node, previous_node=target_node)
    else:
        del target_node.relationships[NodeRelationship.NEXT]


def _transfer_previous(source_node: BaseNode, target_node: BaseNode, previous_node: BaseNode | None = None) -> None:
    """Transfer the previous node of a node to another node. This does not change any other relationships."""
    if source_node.prev_node and previous_node:
        target_node.relationships[NodeRelationship.PREVIOUS] = source_node.prev_node
        _set_node_next(node=previous_node, next_node=target_node)
    else:
        del target_node.relationships[NodeRelationship.PREVIOUS]


def _transfer_children(source_node: BaseNode, target_node: BaseNode, children: list[BaseNode]) -> None:
    """Transfer the children of a node to another node. This does not change any other relationships."""
    if source_node.child_nodes:
        target_node.relationships[NodeRelationship.CHILD] = source_node.child_nodes

        _set_nodes_parent(children=children, parent=target_node)
    else:
        del target_node.relationships[NodeRelationship.CHILD]


def _swap_child_node(parent: BaseNode, child: BaseNode, replacement_child: BaseNode) -> None:
    """Swap a child node with a replacement child node. This does not change any other relationships."""
    _set_nodes_parent(children=[replacement_child], parent=parent)

    new_children: list[RelatedNodeInfo] = []

    for child_node in parent.child_nodes or []:
        if child_node.node_id == child.node_id:
            new_children.append(replacement_child.as_related_node_info())
        else:
            new_children.append(child_node)

    parent.relationships[NodeRelationship.CHILD] = new_children


def _transfer_source_and_parent(source_node: BaseNode, target_nodes: list[BaseNode]) -> None:
    """Transfer the source and parent of a node to another node. This does not change any other relationships."""
    _transfer_source(source_node=source_node, target_nodes=target_nodes)
    _transfer_parent(source_node=source_node, target_nodes=target_nodes)


def _transfer_source(source_node: BaseNode, target_nodes: list[BaseNode]) -> None:
    """Transfer the source of a node to another node. This does not change any other relationships."""

    for target_node in target_nodes:
        if source_node.source_node:
            target_node.relationships[NodeRelationship.SOURCE] = source_node.source_node
        elif NodeRelationship.SOURCE in target_node.relationships:
            del target_node.relationships[NodeRelationship.SOURCE]


def _transfer_parent(source_node: BaseNode, target_nodes: list[BaseNode]) -> None:
    """Transfer the parent of a node to another node. This does not change any other relationships."""

    for target_node in target_nodes:
        if source_node.parent_node:
            target_node.relationships[NodeRelationship.PARENT] = source_node.parent_node
        elif NodeRelationship.PARENT in target_node.relationships:
            del target_node.relationships[NodeRelationship.PARENT]


def _set_node_next(node: BaseNode, next_node: BaseNode | RelatedNodeInfo) -> None:
    """Set the next node of a node. This does not change any other relationships."""
    if isinstance(next_node, RelatedNodeInfo):
        node.relationships[NodeRelationship.NEXT] = next_node
    else:
        node.relationships[NodeRelationship.NEXT] = next_node.as_related_node_info()


def _set_node_previous(node: BaseNode, previous_node: BaseNode | RelatedNodeInfo) -> None:
    """Set the previous node of a node. This does not change any other relationships."""
    if isinstance(previous_node, RelatedNodeInfo):
        node.relationships[NodeRelationship.PREVIOUS] = previous_node
    else:
        node.relationships[NodeRelationship.PREVIOUS] = previous_node.as_related_node_info()


def _make_siblings(first_node: BaseNode, second_node: BaseNode) -> None:
    """Make two nodes siblings. This does not change any other relationships."""
    _set_node_next(node=first_node, next_node=second_node)
    _set_node_previous(node=second_node, previous_node=first_node)


def _make_siblings_from_list(nodes: list[BaseNode]) -> None:
    """Make siblings from a list of nodes. This does not change any other relationships."""
    for i in range(len(nodes) - 1):
        _make_siblings(first_node=nodes[i], second_node=nodes[i + 1])


def _remove_child_from_parent(parent: BaseNode, child: BaseNode) -> None:
    """Remove a child from a parent node."""
    children: list[RelatedNodeInfo] = related_node_info_as_list(related_node_info=parent.relationships[NodeRelationship.CHILD])

    new_children: list[RelatedNodeInfo] = []

    for child_node_ref in children:
        if child_node_ref.node_id == child.node_id:
            continue
        new_children.append(child_node_ref)

    parent.relationships[NodeRelationship.CHILD] = new_children


def _set_nodes_parent(children: list[BaseNode], parent: BaseNode | RelatedNodeInfo) -> None:
    """Set the parent of a node. This does not change any other relationships."""
    for node in children:
        node.relationships[NodeRelationship.PARENT] = parent.as_related_node_info() if isinstance(parent, BaseNode) else parent


def _set_node_children(parent: BaseNode, children: list[BaseNode]) -> None:
    """Set the children of a node. Children must already have prev/next relationships. This does not change any other relationships."""
    ordered_children: list[BaseNode] = order_nodes(nodes=children)
    ordered_children_refs: list[RelatedNodeInfo] = [child.as_related_node_info() for child in ordered_children]

    parent.relationships[NodeRelationship.CHILD] = ordered_children_refs


class NodeRegistry(BaseModel):
    """A registry of nodes."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, use_attribute_docstrings=True, extra="forbid")

    verification_level: Literal["full", "simple", "none"] = "simple"
    """Whether to verify the integrity of the registry after each operation."""

    verification_issue_action: Literal["error", "warn"] = "error"
    """Whether to verify the actions of the registry after each operation."""

    _nodes_by_id: dict[str, BaseNode] = PrivateAttr(default_factory=dict)
    """The set of nodes in the registry."""

    @classmethod
    def from_nodes(cls, nodes: list[BaseNode]) -> Self:
        new_registry = cls()
        new_registry.add(nodes=nodes)
        new_registry.verify_integrity()
        return new_registry

    @overload
    def get(self) -> list[BaseNode]:
        """Get all nodes from the registry."""

    @overload
    def get(self, ids: str) -> BaseNode:
        """Get a node by node id."""

    @overload
    def get(self, ids: list[str]) -> list[BaseNode]:
        """Get nodes by node ids."""

    @overload
    def get(self, *, refs: RelatedNodeInfo) -> BaseNode:
        """Get a node by node reference."""

    @overload
    def get(self, *, refs: list[RelatedNodeInfo]) -> list[BaseNode]:
        """Get nodes by node references."""

    def get(
        self,
        ids: str | list[str] | None = None,
        refs: RelatedNodeInfo | list[RelatedNodeInfo] | None = None,
    ) -> BaseNode | list[BaseNode]:
        """Get nodes from the registry by node id or node reference."""

        if ids is None and refs is None:
            all_nodes: list[BaseNode] = []

            root_nodes: list[BaseNode] = self.get_root_nodes()

            for root_node in root_nodes:
                all_nodes.append(root_node)
                all_nodes.extend(self.get_descendants(node=root_node))

            return all_nodes

        if ids is not None and refs is not None:
            msg = "Cannot get nodes by both ids and refs."
            raise ValueError(msg)

        if ids is not None:
            if isinstance(ids, list):
                return self._get_many(ids=ids)

            return self._get_one(get_id=ids)

        if refs is not None:
            if isinstance(refs, list):
                return self._get_many(ids=[ref.node_id for ref in refs])

            return self._get_one(get_id=refs.node_id)

        return []

    def _get_one(self, get_id: str) -> BaseNode:
        """Get a node by id."""
        if get_id not in self._nodes_by_id:
            msg = f"Node {get_id} not found in the registry."
            raise ValueError(msg)

        return self._nodes_by_id[get_id]

    def _get_many(self, ids: list[str]) -> list[BaseNode]:
        nodes: list[BaseNode] = []
        for get_id in ids:
            if get_id not in self._nodes_by_id:
                msg = f"Node {get_id} not found in the registry."
                raise ValueError(msg)

            nodes.append(self._nodes_by_id[get_id])

        return nodes

    @overload
    def add(self, nodes: BaseNode, upsert: bool = False) -> None:
        """Add a node to the registry."""

    @overload
    def add(self, nodes: list[BaseNode], upsert: bool = False) -> None:
        """Add nodes to the registry."""

    def add(self, nodes: BaseNode | list[BaseNode], upsert: bool = False) -> None:
        """Add a node or nodes to the registry."""
        if isinstance(nodes, BaseNode):
            nodes = [nodes]

        for node in nodes:
            if not upsert and node.node_id in self._nodes_by_id:
                msg = "Node already exists in the registry."
                raise ValueError(msg)

            self._nodes_by_id[node.node_id] = node

        self.verify_integrity()

    def size(self) -> int:
        """Get the number of nodes in the registry."""
        return len(self._nodes_by_id)

    @overload
    def set(self, nodes: BaseNode) -> None:
        """Set the registry to a single node."""

    @overload
    def set(self, nodes: list[BaseNode]) -> None:
        """Set the registry to a list of nodes."""

    def set(self, nodes: BaseNode | list[BaseNode]) -> None:
        """Set the registry to a single node or a list of nodes."""
        if isinstance(nodes, BaseNode):
            nodes = [nodes]

        nodes_by_id: dict[str, BaseNode] = {node.node_id: node for node in nodes}

        self._nodes_by_id = nodes_by_id

        self.verify_integrity()

    def remove(
        self,
        ids: str | list[str] | None = None,
        nodes: BaseNode | list[BaseNode] | None = None,
        refs: RelatedNodeInfo | list[RelatedNodeInfo] | None = None,
    ) -> None:
        """Remove a node or nodes and its children from the registry."""
        ids_to_remove: set[str] = set()

        if ids is not None:
            ids = [ids] if isinstance(ids, str) else ids
            ids_to_remove.update(ids)

        if refs is not None:
            refs = [refs] if isinstance(refs, RelatedNodeInfo) else refs
            ids_to_remove.update(ref.node_id for ref in refs)

        if nodes is not None:
            nodes = [nodes] if isinstance(nodes, BaseNode) else nodes
            ids_to_remove.update(node.node_id for node in nodes)

        descendants_removed: set[str] = set()

        for id_to_remove in ids_to_remove:
            if id_to_remove in descendants_removed:
                continue

            this_node = self._get_one(get_id=id_to_remove)
            descendants = self.get_descendants(node=this_node)

            self._remove_node(node=this_node)

            descendants_removed.update(descendant.node_id for descendant in descendants)

        self.verify_integrity()

    def get_root_nodes(self) -> list[BaseNode]:
        """Get the root nodes of the registry."""
        return [node for node in self._nodes_by_id.values() if not node.parent_node]

    def get_orphans(self) -> list[BaseNode]:
        """Get the orphans (no parent node) of the registry."""
        return [node for node in self._nodes_by_id.values() if not node.parent_node]

    def get_solo_parents(self) -> list[BaseNode]:
        """Get the solo parents (one child node) of the registry."""
        return [node for node in self._nodes_by_id.values() if node.child_nodes and len(node.child_nodes) == 1]

    def get_leaf_families(self) -> list[tuple[BaseNode | None, list[BaseNode]]]:
        """Get the leaf families of the registry.

        Returns a list of tuples, where the first element is the parent node and the second element is a list of child nodes.
        The child nodes are ordered by their prev/next relationships.
        """

        child_nodes_by_parent_id: dict[str | None, list[BaseNode]] = defaultdict(list)

        for node in self._nodes_by_id.values():
            if node.child_nodes:
                continue

            if node.parent_node:
                child_nodes_by_parent_id[node.parent_node.node_id].append(node)
            else:
                child_nodes_by_parent_id[None].append(node)

        return [(self.get(ids=parent_id) if parent_id else None, children) for parent_id, children in child_nodes_by_parent_id.items()]

    def get_children(self, parent: BaseNode, ordered: bool = True) -> list[BaseNode]:
        """Get the children of a parent node."""
        if children := parent.child_nodes:
            return order_nodes(nodes=self.get(refs=children)) if ordered else self.get(refs=children)

        return []

    def get_descendants(self, node: BaseNode, leaf_nodes_only: bool = False) -> list[BaseNode]:
        """Get the descendants of a node."""

        all_descendants: list[BaseNode] = []

        if children := self.get_children(parent=node):
            for child in children:
                all_descendants.append(child)
                all_descendants.extend(self.get_descendants(node=child, leaf_nodes_only=leaf_nodes_only))

        if leaf_nodes_only:
            return [descendant for descendant in all_descendants if not descendant.child_nodes]

        return all_descendants

    def get_parent(self, child: BaseNode) -> BaseNode | None:
        """Get the parent of a child node."""
        if parent_node := child.parent_node:
            return self.get(refs=parent_node)

        return None

    def add_children(self, parent: BaseNode, children: list[BaseNode]) -> None:
        """Add children to a parent node."""
        current_children: list[BaseNode] = self.get_children(parent=parent)

        if len(current_children) == 0:
            self.add(nodes=children)
            _make_siblings_from_list(nodes=children)
            _set_node_children(parent=parent, children=children)
            _set_nodes_parent(children=children, parent=parent)
            return

        # Insert the new children after the last current child
        self.insert_after(node=current_children[-1], next_nodes=children, verify=False)

        self.verify_integrity()

    def verify_integrity(self) -> None:
        """Verify the references of the registry."""
        if self.verification_level == "none":
            return

        for node in self._nodes_by_id.values():
            for relationship_type, item_or_list in node.relationships.items():
                if relationship_type == NodeRelationship.SOURCE:
                    continue

                targets: list[RelatedNodeInfo] = list(related_node_info_as_list(related_node_info=item_or_list))

                for target in targets:
                    if target.node_id not in self._nodes_by_id:
                        msg = f"Node {node.node_id} has a {relationship_type} that does not exist in the registry: {target.node_id}"
                        if self.verification_issue_action == "error":
                            raise ValueError(msg)

                        if self.verification_issue_action == "warn":
                            logger.warning(msg=msg)

        if self.verification_level == "simple":
            return

        self.verify_reference_hashes()

    def verify_reference_hashes(self) -> None:
        """Verify the reference hashes of the registry."""

        out_of_date_refs: int = 0

        recalculated_node_refs_by_id: dict[str, RelatedNodeInfo] = {
            node.node_id: node.as_related_node_info() for node in self._nodes_by_id.values()
        }

        for node in self._nodes_by_id.values():
            for relationship_type, item_or_list in node.relationships.items():
                if relationship_type == NodeRelationship.SOURCE:
                    continue

                targets: list[RelatedNodeInfo] = list(related_node_info_as_list(related_node_info=item_or_list))

                for target in targets:
                    if target != recalculated_node_refs_by_id[target.node_id]:
                        out_of_date_refs += 1

        if out_of_date_refs > 0 and self.verification_issue_action == "warn":
            logger.warning(msg=f"Found {out_of_date_refs} out-of-date refs in the registry.")

    def insert_after(self, node: BaseNode, next_nodes: list[BaseNode], upsert: bool = False, verify: bool = True) -> None:
        """Inserts a node after an existing node. The inserted node inherits the parent and next nodes of the existing node.

        Given: r1 <-> r2 [r2_1 <-> r2_2] <-> r3
        _insert_next_node(node=r2_1, next_nodes=[r4, r5]):
        r1 <-> r2 [r2_1 <-> r4 <-> r5 <-> r2_2] <-> r3
        """
        if len(next_nodes) == 0:
            return

        self.add(nodes=next_nodes, upsert=upsert)

        # 1. Transfer the source and parent of the node to the new nodes
        _transfer_source_and_parent(source_node=node, target_nodes=next_nodes)

        # 2. Setup sibling relationships with existing node, new nodes, existing node's next node
        siblings: list[BaseNode] = [node, *next_nodes]

        if node.next_node and (next_node := self.get(refs=node.next_node)):
            siblings.append(next_node)

        _make_siblings_from_list(nodes=siblings)

        # 3. Update the parent with its new children
        if node.parent_node and (parent_node := self.get(refs=node.parent_node)):
            _set_node_children(
                parent=parent_node,
                children=self.get_children(parent=parent_node, ordered=False) + next_nodes,
            )

        if verify:
            self.verify_integrity()

    def collapse_node(self, node: BaseNode) -> None:
        """Collapse a node. The children of the node are added to the parent node. The node is removed from the registry.

        Given: r1 [r1_1 [r1_1_1 <-> r1_1_2 <-> r1_1_3]] <-> r2
        >>> remove_node(node=r1_1):
        r1 [r1_1_1 <-> r1_1_2 <-> r1_1_3] <-> r2
        """

        # If the node has children, we need to insert them after the node
        # r1 [r1_1 <-> r1_1_1 <-> r1_1_2 <-> r1_1_3] <-> r2
        if node.child_nodes:
            self.insert_after(node=node, next_nodes=self.get(refs=node.child_nodes), upsert=True, verify=False)

        # r1 [r1_1 | r1_1_1 <-> r1_1_2 <-> r1_1_3] <-> r2 (Remove r1_1 from the chain, it's now isolated under the parent node)
        self._remove_previous_next_relationships(node=node)

        # r1 [r1_1 <-> r1_1_1 <-> r1_1_2 <-> r1_1_3] <-> r2 (Remove r1_1 from the parent node)
        if node.parent_node:
            parent_node: BaseNode = self.get(refs=node.parent_node)
            _remove_child_from_parent(parent=parent_node, child=node)

        self._remove_and_isolate_node(node=node)

        self.verify_integrity()

    def replace_node(self, node: BaseNode, replacement_node: BaseNode) -> None:
        """Replace a node with a new node.

        Given: r1 [r1_1 [r1_1_1 <-> r1_1_2 <-> r1_1_3]] <-> r2
        >>> replace_node(node=r1_1, replacement_node=new1):
        r1 [new1 [r1_1_1 <-> r1_1_2 <-> r1_1_3]] <-> r2
        """
        self.add(nodes=[replacement_node])

        # Enumerate all relationships and swap the node with the replacement node
        if node.prev_node and (prev_node := self.get(refs=node.prev_node)):
            _transfer_previous(source_node=node, target_node=replacement_node, previous_node=prev_node)

        if node.next_node and (next_node := self.get(refs=node.next_node)):
            _transfer_next(source_node=node, target_node=replacement_node, next_node=next_node)

        if node.child_nodes and (children := self.get(refs=node.child_nodes)):
            _transfer_children(source_node=node, target_node=replacement_node, children=children)

        _transfer_source_and_parent(source_node=node, target_nodes=[replacement_node])

        # Update the parent node to point to the replacement node
        if node.parent_node and (parent_node := self.get(refs=node.parent_node)):
            _swap_child_node(parent=parent_node, child=node, replacement_child=replacement_node)

        self._remove_and_isolate_node(node=node)

        self.verify_integrity()

    def _remove_node(self, node: BaseNode) -> None:
        """Remove a node from the registry. It is removed along with all of its children.

        Given: r1 [r1_1 [r1_1_1 <-> r1_1_2 <-> r1_1_3]] <-> r2
        >>> remove_node(node=r1_1):
        r1 <-> r2
        """

        # Fill in any prev/next gaps that occur as a result of removing the node
        self._remove_previous_next_relationships(node=node)

        if node.parent_node:
            parent_node: BaseNode = self.get(refs=node.parent_node)
            _remove_child_from_parent(parent=parent_node, child=node)

        # Fill in any prev/next gaps that occur as a result of removing the node's descendants
        descendants: list[BaseNode] = self.get_descendants(node=node)
        for descendant in descendants:
            self._remove_previous_next_relationships(node=descendant)
            self._remove_and_isolate_node(node=descendant)

        self._remove_and_isolate_node(node=node)

    def _remove_previous_next_relationships(self, node: BaseNode) -> None:
        """Remove the previous and next relationships from a node. Connecting the previous and next nodes together if applicable.

        Example:
        r1 <-> r2 <-> r2_1 <-> r2_2 <-> r2_3 <-> r3
        _remove_previous_next_relationships(node=r2_2):
        r1 <-> r2 <-> r2_1 <-> r2_3 <-> r3
        """

        previous_node: BaseNode | None = None
        next_node: BaseNode | None = None

        if node.prev_node:
            previous_node = self.get(refs=node.prev_node)
            del previous_node.relationships[NodeRelationship.NEXT]
            del node.relationships[NodeRelationship.PREVIOUS]

        if node.next_node:
            next_node = self.get(refs=node.next_node)
            del next_node.relationships[NodeRelationship.PREVIOUS]
            del node.relationships[NodeRelationship.NEXT]

        if previous_node and next_node:
            _make_siblings(first_node=previous_node, second_node=next_node)

    def _remove_and_isolate_node(self, node: BaseNode) -> None:
        """Remove a node from the registry and isolate it from the rest of the registry"""
        del self._nodes_by_id[node.node_id]
        node.relationships = {}
