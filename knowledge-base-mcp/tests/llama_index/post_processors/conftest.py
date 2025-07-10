import pytest
from llama_index.core.schema import MediaResource, Node, NodeRelationship, NodeWithScore
from llama_index.core.storage.docstore.simple_docstore import SimpleDocumentStore

DEFAULT_CONTENT = "This is a test node with 100 bytes of content. This is a test node with 100 bytes of content. Really"


@pytest.fixture
def doc_store():
    """The document store to get the parent nodes from."""
    return SimpleDocumentStore()


def attach_content(nodes: list[Node], content: str = DEFAULT_CONTENT, multiplier: int = 1):
    """Attach content to a list of nodes."""

    for node in nodes:
        node.text_resource = MediaResource(text=content * multiplier)


def set_parent_child_relationships(parent: Node, children: list[Node]):
    """Set the parent-child relationships for a parent node and its children."""

    parent.relationships[NodeRelationship.CHILD] = [child.as_related_node_info() for child in children]
    for child in children:
        child.relationships[NodeRelationship.PARENT] = parent.as_related_node_info()


def set_sibling_relationships(nodes: list[Node]):
    """Set the sibling relationships for a list of nodes."""

    for i, node in enumerate(nodes):
        if i > 0:
            node.relationships[NodeRelationship.PREVIOUS] = nodes[i - 1].as_related_node_info()
        if i < len(nodes) - 1:
            node.relationships[NodeRelationship.NEXT] = nodes[i + 1].as_related_node_info()


@pytest.fixture
def example_1p_2c(doc_store: SimpleDocumentStore):
    """Example setup one involving:
    - A parent node [p1] (200 bytes)
    - Two sibling child nodes [p1_c1, p1_c2] (100 bytes each)
    """

    p1 = Node(id_="p1")
    p1_c1 = Node(id_="p1_c1")
    p1_c2 = Node(id_="p1_c2")

    set_parent_child_relationships(parent=p1, children=[p1_c1, p1_c2])
    set_sibling_relationships(nodes=[p1_c1, p1_c2])

    attach_content(nodes=[p1], multiplier=2)
    attach_content(nodes=[p1_c1, p1_c2])

    doc_store.add_documents([p1, p1_c1, p1_c2])

    return p1, p1_c1, p1_c2


@pytest.fixture
def example_2p_4c(doc_store: SimpleDocumentStore):
    """Example setup one involving:
    - Two parent nodes [p1, p2] (200 bytes each)
    - Four sibling child nodes [p1_c1, p1_c2, p2_c1, p2_c2] (100 bytes each)
    """

    p1 = Node(id_="p1")
    p2 = Node(id_="p2")

    p1_c1 = Node(id_="p1_c1")
    p1_c2 = Node(id_="p1_c2")
    p2_c1 = Node(id_="p2_c1")
    p2_c2 = Node(id_="p2_c2")

    set_parent_child_relationships(parent=p1, children=[p1_c1, p1_c2])
    set_parent_child_relationships(parent=p2, children=[p2_c1, p2_c2])
    set_sibling_relationships(nodes=[p1_c1, p1_c2, p2_c1, p2_c2])

    attach_content(nodes=[p1, p2], multiplier=2)
    attach_content(nodes=[p1_c1, p1_c2, p2_c1, p2_c2])

    doc_store.add_documents([p1, p2, p1_c1, p1_c2, p2_c1, p2_c2])

    return p1, p2, p1_c1, p1_c2, p2_c1, p2_c2


@pytest.fixture
def example_1p_2c_1p_1c_1p_3c(doc_store: SimpleDocumentStore):
    """Example setup one involving:
    - A parent node [p1] (200 bytes)
    - Two sibling child nodes [p1_c1, p1_c2] (100 bytes each)
    - A parent node [p2] (100 bytes)
    - A child node [p2_c1] (100 bytes)
    - A parent node [p3] (300 bytes)
    - Three sibling child nodes [p3_c1, p3_c2, p3_c3] (100 bytes each)
    """

    p1 = Node(id_="p1")
    p1_c1 = Node(id_="p1_c1")
    p1_c2 = Node(id_="p1_c2")

    p2 = Node(id_="p2")
    p2_c1 = Node(id_="p2_c1")

    p3 = Node(id_="p3")
    p3_c1 = Node(id_="p3_c1")
    p3_c2 = Node(id_="p3_c2")
    p3_c3 = Node(id_="p3_c3")

    set_parent_child_relationships(parent=p1, children=[p1_c1, p1_c2])
    set_parent_child_relationships(parent=p2, children=[p2_c1])
    set_parent_child_relationships(parent=p3, children=[p3_c1, p3_c2, p3_c3])
    set_sibling_relationships(nodes=[p1_c1, p1_c2, p2_c1, p3_c1, p3_c2, p3_c3])

    attach_content(nodes=[p1], multiplier=2)
    attach_content(nodes=[p1_c1, p1_c2])
    attach_content(nodes=[p2])
    attach_content(nodes=[p3], multiplier=3)
    attach_content(nodes=[p3_c1, p3_c2, p3_c3])

    doc_store.add_documents([p1, p1_c1, p1_c2, p2, p2_c1, p3, p3_c1, p3_c2, p3_c3])


@pytest.fixture
def example_1gp_2p_2c_1c(doc_store: SimpleDocumentStore):
    """Example setup one involving:
    - A grandparent node [gp1] (300 bytes)
    - A parent node [p1] (200 bytes)
    - Two sibling child nodes [p1_c1, p1_c2] (100 bytes each)
    - A parent node [p2] (100 bytes)
    - A child node [p2_c1] (100 bytes)
    """

    gp1 = Node(id_="gp1")
    p1 = Node(id_="p1")
    p2 = Node(id_="p2")

    p1_c1 = Node(id_="p1_c1")
    p1_c2 = Node(id_="p1_c2")
    p2_c1 = Node(id_="p2_c1")

    set_parent_child_relationships(parent=gp1, children=[p1, p2])
    set_parent_child_relationships(parent=p1, children=[p1_c1, p1_c2])
    set_parent_child_relationships(parent=p2, children=[p2_c1])
    set_sibling_relationships(nodes=[p1_c1, p1_c2, p2_c1])
    set_sibling_relationships(nodes=[p1, p2])

    attach_content(nodes=[gp1], multiplier=3)
    attach_content(nodes=[p1], multiplier=2)
    attach_content(nodes=[p2])
    attach_content(nodes=[p1_c1, p1_c2])
    attach_content(nodes=[p2_c1])

    doc_store.add_documents([gp1, p1, p2, p1_c1, p1_c2, p2_c1])

    return gp1, p1, p2, p1_c1, p1_c2, p2_c1


def score_nodes(nodes: list[Node], score: float = 0.50) -> list[NodeWithScore]:
    return [NodeWithScore(node=node, score=score) for node in nodes]


def get_node_ids(nodes: list[NodeWithScore]) -> list[str]:
    return sorted([node.node.id_ for node in nodes])
