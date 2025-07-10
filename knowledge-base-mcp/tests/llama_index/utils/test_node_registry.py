import pytest
from llama_index.core.schema import BaseNode, MediaResource, Node, NodeRelationship
from syrupy.assertion import SnapshotAssertion

from knowledge_base_mcp.llama_index.utils.node_registry import NodeRegistry


def test_init() -> None:
    node_registry = NodeRegistry()

    assert node_registry


def test_add_get() -> None:
    node_registry = NodeRegistry()

    node_to_register: BaseNode = Node(text_resource=MediaResource(text="test"))

    node_registry.add(nodes=[node_to_register])

    nodes_from_registry: list[BaseNode] = node_registry.get()

    assert len(nodes_from_registry) == 1

    assert nodes_from_registry[0] == node_to_register


def serialize_hierarchy_to_text(registry: NodeRegistry) -> str:
    return "\n".join(serialize_hierarchy(registry))


def serialize_hierarchy(registry: NodeRegistry) -> list[str]:
    nodes_from_registry: list[BaseNode] = registry.get()

    serialized_hierarchy: list[str] = []

    root_nodes: list[BaseNode] = [node for node in nodes_from_registry if node.parent_node is None]

    for root_node in root_nodes:
        serialized_hierarchy.extend(serialize_hierarchy_node(registry, root_node))

    return serialized_hierarchy


def serialize_hierarchy_node(registry: NodeRegistry, node: BaseNode, level: int = 0) -> list[str]:
    children: list[BaseNode] = registry.get_children(parent=node)

    this_node_serialized: str = f"{'  ' * level} - {node.node_id}"

    children_serialized: list[str] = []

    for i, child in enumerate(children):
        if child.prev_node and child.prev_node.node_id != children[i - 1].node_id:
            msg = f"Child {child.node_id} has a prev_node that is not the previous child."
            raise ValueError(msg)

        if child.next_node and child.next_node.node_id != children[i + 1].node_id:
            msg = f"Child {child.node_id} has a next_node that is not the next child."
            raise ValueError(msg)

        children_serialized.extend(serialize_hierarchy_node(registry, child, level + 1))

    return [this_node_serialized, *children_serialized]


class TestSimpleCase:
    @pytest.fixture
    def sample_node(self) -> BaseNode:
        return Node(text_resource=MediaResource(text="test"))

    def test_init(self, sample_node: BaseNode) -> None:
        node_registry = NodeRegistry()
        node_registry.add(nodes=[sample_node])
        assert node_registry

    @pytest.fixture
    def registry_with_node(self, sample_node: BaseNode) -> NodeRegistry:
        node_registry = NodeRegistry()

        node_to_register: BaseNode = sample_node

        node_registry.add(nodes=[node_to_register])

        assert node_registry.get() == [node_to_register]

        return node_registry

    @pytest.fixture
    def node_registry(self) -> NodeRegistry:
        node_registry = NodeRegistry()

        root = Node(id_="root")
        r_1 = Node(id_="r_1")
        r_2 = Node(id_="r_2")

        node_registry.add(root)

        node_registry.add_children(parent=root, children=[r_1, r_2])

        return node_registry

    def test_add(self, node_registry: NodeRegistry) -> None:
        node_to_add: Node = Node(id_="node_to_add")

        node_registry.add(node_to_add)

        assert node_to_add in node_registry.get()

    def test_set(self, node_registry: NodeRegistry) -> None:
        node_to_set: Node = Node(id_="node_to_set")

        node_registry.set(node_to_set)

        assert node_to_set in node_registry.get()
        assert len(node_registry.get()) == 1

    def test_remove(self, node_registry: NodeRegistry) -> None:
        root: BaseNode = node_registry.get("root")
        r_1: BaseNode = node_registry.get("r_1")

        node_registry.remove(nodes=r_1)

        assert r_1 not in node_registry.get()
        assert node_registry.size() == 2

        node_registry.remove(nodes=root)

        assert root not in node_registry.get()
        assert node_registry.size() == 0

    def test_remove_children(self, node_registry: NodeRegistry) -> None:
        root: BaseNode = node_registry.get("root")
        r_1: BaseNode = node_registry.get("r_1")
        r_2: BaseNode = node_registry.get("r_2")

        node_registry.remove(nodes=r_2)

        assert r_2 not in node_registry.get()
        assert node_registry.size() == 2

        assert root.child_nodes == [r_1.as_related_node_info()]
        assert root.next_node is None
        assert root.prev_node is None

        assert r_1.parent_node == root.as_related_node_info()
        assert r_1.next_node is None
        assert r_1.prev_node is None
        assert r_1.child_nodes is None

    def test_insert_after(self, node_registry: NodeRegistry) -> None:
        r_1: BaseNode = node_registry.get("r_1")

        r_1_1: BaseNode = Node(id_="r_1_1")
        node_registry.add_children(parent=r_1, children=[r_1_1])

        r_1_2: BaseNode = Node(id_="r_1_2")
        node_registry.insert_after(node=r_1_1, next_nodes=[r_1_2])

        assert node_registry.get_children(parent=r_1) == [r_1_1, r_1_2]

    def test_insert_after_larger(self, node_registry: NodeRegistry) -> None:
        r_1: BaseNode = node_registry.get("r_1")

        r_1_1: BaseNode = Node(id_="r_1_1")
        r_1_2: BaseNode = Node(id_="r_1_2")
        r_1_5: BaseNode = Node(id_="r_1_5")

        node_registry.add_children(parent=r_1, children=[r_1_1, r_1_2, r_1_5])

        r_1_3: BaseNode = Node(id_="r_1_3")
        r_1_4: BaseNode = Node(id_="r_1_4")
        node_registry.insert_after(node=r_1_2, next_nodes=[r_1_3, r_1_4])

        assert node_registry.get_children(parent=r_1) == [r_1_1, r_1_2, r_1_3, r_1_4, r_1_5]

    def test_replace_node(self, node_registry: NodeRegistry) -> None:
        root: BaseNode = node_registry.get("root")
        r_1: BaseNode = node_registry.get("r_1")
        r_2: BaseNode = node_registry.get("r_2")

        replacement_node: BaseNode = Node(id_="replacement_node")

        node_registry.replace_node(node=r_1, replacement_node=replacement_node)

        assert node_registry.get_children(parent=root) == [replacement_node, r_2]

        assert replacement_node.parent_node == root.as_related_node_info()
        assert replacement_node.next_node == r_2.as_related_node_info()
        assert replacement_node.prev_node is None
        assert replacement_node.child_nodes is None

        assert r_2.parent_node == root.as_related_node_info()
        assert r_2.next_node is None
        assert r_2.prev_node == replacement_node.as_related_node_info()
        assert r_2.child_nodes is None

        assert root.child_nodes == [replacement_node.as_related_node_info(), r_2.as_related_node_info()]
        assert root.next_node is None
        assert root.prev_node is None


def establish_family_relationships(parent: BaseNode, children: list[BaseNode]) -> None:
    for child in children:
        child.relationships[NodeRelationship.PARENT] = parent.as_related_node_info()

    parent.relationships[NodeRelationship.CHILD] = [child.as_related_node_info() for child in children]

    for i, child in enumerate(children):
        if i < len(children) - 1:
            child.relationships[NodeRelationship.NEXT] = children[i + 1].as_related_node_info()
        if i > 0:
            child.relationships[NodeRelationship.PREVIOUS] = children[i - 1].as_related_node_info()


class TestNodeRegistry:
    @pytest.fixture
    def manual_hierarchy(self) -> NodeRegistry:
        root_node = Node(id_="r")

        r_1 = Node(id_="r_1")
        r_1_1 = Node(id_="r_1_1")
        r_1_2 = Node(id_="r_1_2")
        establish_family_relationships(parent=r_1, children=[r_1_1, r_1_2])

        r_2 = Node(id_="r_2")
        r_2_1 = Node(id_="r_2_1")
        r_2_2 = Node(id_="r_2_2")
        r_2_3 = Node(id_="r_2_3")
        establish_family_relationships(parent=r_2, children=[r_2_1, r_2_2, r_2_3])

        r_3 = Node(id_="r_3")
        r_3_1 = Node(id_="r_3_1")
        establish_family_relationships(parent=r_3, children=[r_3_1])

        r_4 = Node(id_="r_4")
        r_4_1 = Node(id_="r_4_1")
        r_4_2 = Node(id_="r_4_2")
        establish_family_relationships(parent=r_4, children=[r_4_1, r_4_2])

        r_4_2_1 = Node(id_="r_4_2_1")
        establish_family_relationships(parent=r_4_2, children=[r_4_2_1])

        establish_family_relationships(parent=root_node, children=[r_1, r_2, r_3, r_4])

        node_registry: NodeRegistry = NodeRegistry()

        node_registry.add(nodes=[root_node, r_1, r_1_1, r_1_2, r_2, r_2_1, r_2_2, r_2_3, r_3, r_3_1, r_4, r_4_1, r_4_2, r_4_2_1])

        return node_registry

    @pytest.fixture
    def managed_hierarchy(self) -> NodeRegistry:
        node_registry = NodeRegistry()

        root_node = Node(id_="r")

        node_registry.add(nodes=[root_node])

        r_1 = Node(id_="r_1")
        r_1_1 = Node(id_="r_1_1")
        r_1_2 = Node(id_="r_1_2")
        node_registry.add_children(parent=root_node, children=[r_1])
        node_registry.add_children(parent=r_1, children=[r_1_1, r_1_2])

        r_2 = Node(id_="r_2")
        r_2_1 = Node(id_="r_2_1")
        r_2_2 = Node(id_="r_2_2")
        r_2_3 = Node(id_="r_2_3")
        node_registry.add_children(parent=root_node, children=[r_2])
        node_registry.add_children(parent=r_2, children=[r_2_1, r_2_2, r_2_3])

        r_3 = Node(id_="r_3")
        r_3_1 = Node(id_="r_3_1")
        node_registry.add_children(parent=root_node, children=[r_3])
        node_registry.add_children(parent=r_3, children=[r_3_1])

        r_4 = Node(id_="r_4")
        r_4_1 = Node(id_="r_4_1")
        r_4_2 = Node(id_="r_4_2")
        node_registry.add_children(parent=root_node, children=[r_4])
        node_registry.add_children(parent=r_4, children=[r_4_1, r_4_2])

        r_4_2_1 = Node(id_="r_4_2_1")
        node_registry.add_children(parent=r_4_2, children=[r_4_2_1])

        return node_registry

    @pytest.fixture
    def node_registry(self, method: str, manual_hierarchy: NodeRegistry, managed_hierarchy: NodeRegistry) -> NodeRegistry:
        node_registry: NodeRegistry

        node_registry = manual_hierarchy if method == "manual" else managed_hierarchy

        return node_registry

    @pytest.mark.parametrize(argnames="method", argvalues=["manual", "managed"], ids=["Manual Relationships", "Managed Relationships"])
    class TestHierarchy:
        def test_hierarchy_is_correct(self, node_registry: NodeRegistry, text_snapshot: SnapshotAssertion) -> None:  # noqa: PLR0915
            nodes_from_registry: list[BaseNode] = node_registry.get()

            root_node: BaseNode = nodes_from_registry[0]
            r_1: BaseNode = nodes_from_registry[1]
            r_2: BaseNode = nodes_from_registry[4]
            r_3: BaseNode = nodes_from_registry[8]
            r_4: BaseNode = nodes_from_registry[10]

            assert r_1.parent_node == root_node.as_related_node_info()
            assert r_1.next_node == r_2.as_related_node_info()
            assert r_1.prev_node is None

            assert r_2.parent_node == root_node.as_related_node_info()
            assert r_2.next_node == r_3.as_related_node_info()
            assert r_2.prev_node == r_1.as_related_node_info()

            assert r_3.parent_node == root_node.as_related_node_info()
            assert r_3.next_node == r_4.as_related_node_info()
            assert r_3.prev_node == r_2.as_related_node_info()

            assert r_4.parent_node == root_node.as_related_node_info()
            assert r_4.next_node is None
            assert r_4.prev_node == r_3.as_related_node_info()

            r_1_1: BaseNode = nodes_from_registry[2]
            r_1_2: BaseNode = nodes_from_registry[3]

            assert r_1_1.parent_node == r_1.as_related_node_info()
            assert r_1_2.parent_node == r_1.as_related_node_info()
            assert r_1_1.prev_node is None
            assert r_1_1.next_node == r_1_2.as_related_node_info()
            assert r_1_2.prev_node == r_1_1.as_related_node_info()
            assert r_1_2.next_node is None

            r_2_1: BaseNode = nodes_from_registry[5]
            r_2_2: BaseNode = nodes_from_registry[6]
            r_2_3: BaseNode = nodes_from_registry[7]

            assert r_2_1.parent_node == r_2.as_related_node_info()
            assert r_2_2.parent_node == r_2.as_related_node_info()
            assert r_2_3.parent_node == r_2.as_related_node_info()

            assert r_2_1.prev_node is None
            assert r_2_1.next_node == r_2_2.as_related_node_info()
            assert r_2_2.prev_node == r_2_1.as_related_node_info()
            assert r_2_2.next_node == r_2_3.as_related_node_info()

            r_3_1: BaseNode = nodes_from_registry[9]

            assert r_3_1.parent_node == r_3.as_related_node_info()
            assert r_3_1.prev_node is None
            assert r_3_1.next_node is None

            r_4_1: BaseNode = nodes_from_registry[11]
            r_4_2: BaseNode = nodes_from_registry[12]
            r_4_2_1: BaseNode = nodes_from_registry[13]

            assert r_4_1.prev_node is None
            assert r_4_1.parent_node == r_4.as_related_node_info()
            assert r_4_1.next_node == r_4_2.as_related_node_info()

            assert r_4_2.parent_node == r_4.as_related_node_info()
            assert r_4_2.prev_node == r_4_1.as_related_node_info()
            assert r_4_2.next_node is None

            assert r_4_2_1.parent_node == r_4_2.as_related_node_info()
            assert r_4_2_1.prev_node is None
            assert r_4_2_1.next_node is None

            serialized_hierarchy: str = serialize_hierarchy_to_text(registry=node_registry)
            assert serialized_hierarchy == text_snapshot

        def test_get(self, node_registry: NodeRegistry) -> None:
            nodes_from_registry: list[BaseNode] = node_registry.get()

            assert len(nodes_from_registry) == 14

        def test_get_leaf_families(self, node_registry: NodeRegistry) -> None:
            leaf_families: list[tuple[BaseNode, list[BaseNode]]] = node_registry.get_leaf_families()
            assert len(leaf_families) == 5

            parent, children = leaf_families[0]
            assert parent == node_registry.get("r_1")
            assert children == [node_registry.get("r_1_1"), node_registry.get("r_1_2")]

            parent, children = leaf_families[1]
            assert parent == node_registry.get("r_2")
            assert children == [node_registry.get("r_2_1"), node_registry.get("r_2_2"), node_registry.get("r_2_3")]

            parent, children = leaf_families[2]
            assert parent == node_registry.get("r_3")
            assert children == [node_registry.get("r_3_1")]

            parent, children = leaf_families[3]
            assert parent == node_registry.get("r_4")
            assert children == [node_registry.get("r_4_1")]

            parent, children = leaf_families[4]
            assert parent == node_registry.get("r_4_2")
            assert children == [node_registry.get("r_4_2_1")]

        def test_remove(self, node_registry: NodeRegistry) -> None:
            r_1: BaseNode = node_registry.get("r_1")
            node_registry.remove(nodes=r_1)
            assert r_1.relationships == {}

            assert r_1 not in node_registry.get()
            assert node_registry.size() == 11

            r_2: BaseNode = node_registry.get("r_2")
            node_registry.remove(nodes=r_2)
            assert r_2.relationships == {}

            assert r_2 not in node_registry.get()
            assert node_registry.size() == 7

            r_3_1: BaseNode = node_registry.get("r_3_1")
            node_registry.remove(nodes=r_3_1)

            assert r_3_1 not in node_registry.get()
            assert node_registry.size() == 6

            r_4_1: BaseNode = node_registry.get("r_4_1")
            node_registry.remove(nodes=r_4_1)

            assert r_4_1 not in node_registry.get()
            assert node_registry.size() == 5

        def test_get_children(self, node_registry: NodeRegistry) -> None:
            nodes_from_registry: list[BaseNode] = node_registry.get()
            children: list[BaseNode] = node_registry.get_children(parent=nodes_from_registry[0])

            assert len(children) == 4

            assert children[0].parent_node == node_registry.get()[0].as_related_node_info()
            assert children[1].parent_node == node_registry.get()[0].as_related_node_info()
            assert children[2].parent_node == node_registry.get()[0].as_related_node_info()
            assert children[3].parent_node == node_registry.get()[0].as_related_node_info()

        def test_replace_node(self, node_registry: NodeRegistry) -> None:
            r_2_2: BaseNode = node_registry.get("r_2_2")

            replacement_node: BaseNode = Node(id_="replacement_node")

            r_2_2_relationships = r_2_2.relationships.copy()

            node_registry.replace_node(node=r_2_2, replacement_node=replacement_node)

            assert r_2_2 not in node_registry.get()
            assert replacement_node in node_registry.get()
            assert node_registry.size() == 14

            # Our new node should have the same relationships as the old node
            assert r_2_2_relationships == replacement_node.relationships
            # our old node should have no relationships
            assert r_2_2.relationships == {}

        def test_collapse_node(self, node_registry: NodeRegistry) -> None:
            root: BaseNode = node_registry.get("r")
            r_1: BaseNode = node_registry.get("r_1")
            r_1_1: BaseNode = node_registry.get("r_1_1")
            r_1_2: BaseNode = node_registry.get("r_1_2")

            r_2: BaseNode = node_registry.get("r_2")

            node_registry.collapse_node(node=r_1)

            assert r_1 not in node_registry.get()
            assert r_1_1 in node_registry.get()
            assert r_1_2 in node_registry.get()

            assert r_1_1.parent_node == root.as_related_node_info()
            assert r_1_1.next_node == r_1_2.as_related_node_info()
            assert r_1_1.prev_node is None
            assert r_1_1.child_nodes is None

            assert r_1_2.parent_node == root.as_related_node_info()
            assert r_1_2.next_node == r_2.as_related_node_info()
            assert r_1_2.prev_node == r_1_1.as_related_node_info()
            assert r_1_2.child_nodes is None

        def test_collapse_node_larger(self, node_registry: NodeRegistry) -> None:
            root: BaseNode = node_registry.get("r")
            r_3: BaseNode = node_registry.get("r_3")
            r_4: BaseNode = node_registry.get("r_4")
            r_4_1: BaseNode = node_registry.get("r_4_1")
            r_4_2: BaseNode = node_registry.get("r_4_2")
            r_4_2_1: BaseNode = node_registry.get("r_4_2_1")

            node_registry.collapse_node(node=r_4)

            assert r_4 not in node_registry.get()
            assert r_4_1 in node_registry.get()
            assert r_4_2 in node_registry.get()
            assert r_4_2_1 in node_registry.get()

            assert r_4_1.parent_node == root.as_related_node_info()
            assert r_4_1.next_node == r_4_2.as_related_node_info()
            assert r_4_1.prev_node == r_3.as_related_node_info()
            assert r_4_1.child_nodes is None

            assert r_4_2.parent_node == root.as_related_node_info()
            assert r_4_2.next_node is None
            assert r_4_2.prev_node == r_4_1.as_related_node_info()
            assert r_4_2.child_nodes == [r_4_2_1.as_related_node_info()]

            assert r_4_2_1.parent_node == r_4_2.as_related_node_info()
            assert r_4_2_1.prev_node is None
            assert r_4_2_1.next_node is None
            assert r_4_2_1.child_nodes is None

        def test_collapse_node_root(self, node_registry: NodeRegistry) -> None:
            root: BaseNode = node_registry.get("r")

            node_registry.collapse_node(node=root)

            assert root not in node_registry.get()

            assert node_registry.size() == 13

        def test_get_descendants(self, node_registry: NodeRegistry) -> None:
            root: BaseNode = node_registry.get("r")
            descendants: list[BaseNode] = node_registry.get_descendants(node=root)
            assert len(descendants) == 13

            descendants = node_registry.get_children(parent=root)
            assert len(descendants) == 4

            descendants = node_registry.get_children(parent=root, ordered=False)
            assert len(descendants) == 4

            descendants = node_registry.get_descendants(node=root, leaf_nodes_only=True)
            assert len(descendants) == 8
