from llama_index.core.schema import MediaResource, Node, NodeRelationship

from knowledge_base_mcp.llama_index.transformations.large_node_detector import LargeNodeDetector


def test_init() -> None:
    warning: LargeNodeDetector = LargeNodeDetector(max_size=100)

    assert warning.max_size == 100


def test_call_all_nodes() -> None:
    warning: LargeNodeDetector = LargeNodeDetector(max_size=5, exclude=True, node_type="all")

    parent_node: Node = Node(text_resource=MediaResource(text="This is a test node"))
    child_node: Node = Node(text_resource=MediaResource(text="This is a test node"))

    parent_node.relationships[NodeRelationship.CHILD] = [child_node.as_related_node_info()]
    child_node.relationships[NodeRelationship.PARENT] = parent_node.as_related_node_info()

    nodes = warning(nodes=[parent_node, child_node])

    assert nodes == []


def test_call_leaf_node() -> None:
    warning: LargeNodeDetector = LargeNodeDetector(max_size=5, exclude=True, node_type="leaf")

    parent_node: Node = Node(text_resource=MediaResource(text="This is a test node"))
    child_node: Node = Node(text_resource=MediaResource(text="This is a test node"))

    parent_node.relationships[NodeRelationship.CHILD] = [child_node.as_related_node_info()]
    child_node.relationships[NodeRelationship.PARENT] = parent_node.as_related_node_info()

    nodes = warning(nodes=[parent_node, child_node])

    assert nodes == [parent_node]
