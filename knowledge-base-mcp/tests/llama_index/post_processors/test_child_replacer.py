import pytest
from llama_index.core.schema import MediaResource, MetadataMode, Node, NodeRelationship, NodeWithScore
from llama_index.core.storage.docstore.simple_docstore import SimpleDocumentStore

from knowledge_base_mcp.llama_index.post_processors.child_replacer import ChildReplacerNodePostprocessor


@pytest.fixture
def doc_store():
    return SimpleDocumentStore()


def test_init(doc_store: SimpleDocumentStore):
    postprocessor = ChildReplacerNodePostprocessor(doc_store=doc_store)

    assert postprocessor.doc_store == doc_store
    assert postprocessor.rounds == 2
    assert postprocessor.threshold == 0.25
    assert postprocessor.maximum_size == 4096


@pytest.fixture
def post_processor(doc_store: SimpleDocumentStore):
    return ChildReplacerNodePostprocessor(doc_store=doc_store)


def test_process_no_op(post_processor: ChildReplacerNodePostprocessor):
    child_node_one = Node(text_resource=MediaResource(text="Node 1"))
    child_node_two = Node(text_resource=MediaResource(text="Node 2"))

    child_node_one.relationships[NodeRelationship.NEXT] = [child_node_two.as_related_node_info()]
    child_node_two.relationships[NodeRelationship.PREVIOUS] = [child_node_one.as_related_node_info()]

    nodes = [
        NodeWithScore(node=child_node_one, score=0.5),
        NodeWithScore(node=child_node_two, score=0.5),
    ]

    result = post_processor.postprocess_nodes(nodes)

    assert len(result) == 2

    assert result[0].node.get_content(metadata_mode=MetadataMode.NONE) == "Node 1"
    assert result[1].node.get_content(metadata_mode=MetadataMode.NONE) == "Node 2"


def test_process_merge(post_processor: ChildReplacerNodePostprocessor, doc_store: SimpleDocumentStore):
    """Test that a single child node is merged into the parent node."""

    parent_node = Node(text_resource=MediaResource(text="Parent Node"))
    child_node = Node(text_resource=MediaResource(text="Child Node"))

    parent_node.relationships[NodeRelationship.CHILD] = [child_node.as_related_node_info()]
    child_node.relationships[NodeRelationship.PARENT] = parent_node.as_related_node_info()

    doc_store.add_documents([parent_node, child_node])

    scored_child_node = NodeWithScore(node=child_node, score=0.5)

    result = post_processor.postprocess_nodes(nodes=[scored_child_node])

    assert len(result) == 1
    assert result[0].node.get_content(metadata_mode=MetadataMode.NONE) == "Parent Node"
    assert result[0].score == 0.5


def test_process_merge_keep_children(post_processor: ChildReplacerNodePostprocessor, doc_store: SimpleDocumentStore):
    """Test that a single child node is merged into the parent node."""

    parent_node = Node(text_resource=MediaResource(text="Parent Node"))
    child_node = Node(text_resource=MediaResource(text="Child Node"))

    parent_node.relationships[NodeRelationship.CHILD] = [child_node.as_related_node_info()]
    child_node.relationships[NodeRelationship.PARENT] = parent_node.as_related_node_info()

    doc_store.add_documents([parent_node, child_node])

    scored_child_node = NodeWithScore(node=child_node, score=0.5)

    post_processor.keep_children = True

    result = post_processor.postprocess_nodes(nodes=[scored_child_node])

    assert len(result) == 2
    assert result[0].node.get_content(metadata_mode=MetadataMode.NONE) == "Parent Node"
    assert result[0].score == 0.5

    assert result[1].node.get_content(metadata_mode=MetadataMode.NONE) == "Child Node"
    assert result[1].score == 0.5


def test_process_merge_mixed(post_processor: ChildReplacerNodePostprocessor, doc_store: SimpleDocumentStore):
    """Test that a single child node is merged into the parent node while ignoring the other nodes."""

    parent_node = Node(text_resource=MediaResource(text="Parent Node"))
    child_node_one = Node(text_resource=MediaResource(text="Child Node"))

    lonely_node_one = Node(text_resource=MediaResource(text="Lonely Node One"))
    lonely_node_two = Node(text_resource=MediaResource(text="Lonely Node Two"))

    parent_node.relationships[NodeRelationship.CHILD] = [child_node_one.as_related_node_info()]
    child_node_one.relationships[NodeRelationship.PARENT] = parent_node.as_related_node_info()

    doc_store.add_documents([parent_node, child_node_one, lonely_node_one, lonely_node_two])

    scored_child_node_one = NodeWithScore(node=child_node_one, score=0.5)
    scored_lonely_node_one = NodeWithScore(node=lonely_node_one, score=0.5)
    scored_lonely_node_two = NodeWithScore(node=lonely_node_two, score=0.5)

    result = post_processor.postprocess_nodes(nodes=[scored_child_node_one, scored_lonely_node_one, scored_lonely_node_two])

    assert len(result) == 3
    assert result[0].node.get_content(metadata_mode=MetadataMode.NONE) == "Lonely Node One"
    assert result[1].node.get_content(metadata_mode=MetadataMode.NONE) == "Lonely Node Two"
    assert result[2].node.get_content(metadata_mode=MetadataMode.NONE) == "Parent Node"


def test_merge(post_processor: ChildReplacerNodePostprocessor, doc_store: SimpleDocumentStore):
    parent_node = Node(text_resource=MediaResource(text="Parent Node"))
    child_node = Node(text_resource=MediaResource(text="Child Node"))
    scored_child_node = NodeWithScore(node=child_node, score=0.5)

    doc_store.add_documents([parent_node, child_node])

    result = post_processor.merge_children_into_parent(parent_node=parent_node, children=[scored_child_node])

    assert result.node.get_content(metadata_mode=MetadataMode.NONE) == "Parent Node"
    assert result.score == 0.5
