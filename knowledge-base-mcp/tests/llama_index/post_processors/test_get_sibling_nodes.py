import pytest
from llama_index.core.schema import Node, NodeWithScore
from llama_index.core.storage.docstore.simple_docstore import SimpleDocumentStore

from knowledge_base_mcp.llama_index.post_processors.get_sibling_nodes import GetSiblingNodesPostprocessor
from tests.llama_index.post_processors.conftest import get_node_ids, score_nodes


@pytest.fixture
def doc_store():
    return SimpleDocumentStore()


def test_init(doc_store: SimpleDocumentStore):
    postprocessor = GetSiblingNodesPostprocessor(doc_store=doc_store)

    assert postprocessor.doc_store == doc_store
    assert postprocessor.maximum_size == 1024


class Test1p2c:
    @pytest.fixture
    def query_result_one_child_node(self, example_1p_2c: tuple[Node, Node, Node]) -> list[NodeWithScore]:
        return score_nodes(nodes=[example_1p_2c[1]])

    def test_1p_2c(
        self,
        doc_store: SimpleDocumentStore,
        query_result_one_child_node: list[NodeWithScore],
    ):
        """Test the default behavior of the postprocessor with the 1p_2c example."""

        default_postprocessor: GetSiblingNodesPostprocessor = GetSiblingNodesPostprocessor(doc_store=doc_store)
        result = default_postprocessor.postprocess_nodes(nodes=query_result_one_child_node)
        assert len(result) == 2
        assert get_node_ids(result) == sorted(["p1_c1", "p1_c2"])


class Test1gp2p2c1c:
    @pytest.fixture
    def query_result_one_parent_node(self, example_1gp_2p_2c_1c: tuple[Node, Node, Node, Node, Node, Node]) -> list[NodeWithScore]:
        """Return the p1 node."""
        return score_nodes(nodes=[example_1gp_2p_2c_1c[1]])

    @pytest.fixture
    def query_result_two_child_nodes(self, example_1gp_2p_2c_1c: tuple[Node, Node, Node, Node, Node, Node]) -> list[NodeWithScore]:
        """Return the p1c1 and p2c1 nodes."""
        return score_nodes(nodes=[example_1gp_2p_2c_1c[3], example_1gp_2p_2c_1c[5]])

    def test_1gp_2p_2c_1c(
        self,
        doc_store: SimpleDocumentStore,
        query_result_one_parent_node: list[NodeWithScore],
        query_result_two_child_nodes: list[NodeWithScore],
    ):
        """Test the default behavior of the postprocessor with the 1gp_2p_2c_1c example."""

        # Fetch all child nodes.
        default_postprocessor: GetSiblingNodesPostprocessor = GetSiblingNodesPostprocessor(doc_store=doc_store)
        result = default_postprocessor.postprocess_nodes(nodes=query_result_two_child_nodes)
        assert len(result) == 3
        assert get_node_ids(result) == sorted(["p1_c1", "p1_c2", "p2_c1"])

        # Get the sibling of the parent node, which is p2
        result = default_postprocessor.postprocess_nodes(nodes=query_result_one_parent_node)
        assert len(result) == 2
        assert get_node_ids(result) == sorted(["p1", "p2"])

    def test_maximum_size(
        self,
        doc_store: SimpleDocumentStore,
        query_result_one_parent_node: list[NodeWithScore],
        query_result_two_child_nodes: list[NodeWithScore],
    ):
        default_postprocessor: GetSiblingNodesPostprocessor = GetSiblingNodesPostprocessor(doc_store=doc_store, maximum_size=50)
        result = default_postprocessor.postprocess_nodes(nodes=query_result_two_child_nodes)
        assert len(result) == 2
        assert get_node_ids(result) == sorted(["p1_c1", "p2_c1"])

        result = default_postprocessor.postprocess_nodes(nodes=query_result_one_parent_node)
        assert len(result) == 1
        assert get_node_ids(result) == sorted(["p1"])
