import pytest
from llama_index.core.schema import Node, NodeWithScore
from llama_index.core.storage.docstore.simple_docstore import SimpleDocumentStore

from knowledge_base_mcp.llama_index.post_processors.get_child_nodes import GetChildNodesPostprocessor
from tests.llama_index.post_processors.conftest import get_node_ids, score_nodes


@pytest.fixture
def doc_store():
    return SimpleDocumentStore()


def test_init(doc_store: SimpleDocumentStore):
    postprocessor = GetChildNodesPostprocessor(doc_store=doc_store)

    assert postprocessor.doc_store == doc_store
    assert postprocessor.keep_parent_nodes


class Test1p2c:
    @pytest.fixture
    def query_result_parent_nodes(self, example_1p_2c: tuple[Node, Node, Node]) -> list[NodeWithScore]:
        return score_nodes(nodes=[example_1p_2c[0]])

    def test_1p_2c(
        self,
        doc_store: SimpleDocumentStore,
        query_result_parent_nodes: list[NodeWithScore],
    ):
        """Test the default behavior of the postprocessor with the 1p_2c example."""

        default_postprocessor: GetChildNodesPostprocessor = GetChildNodesPostprocessor(doc_store=doc_store)
        result = default_postprocessor.postprocess_nodes(nodes=query_result_parent_nodes)
        assert len(result) == 3
        assert get_node_ids(result) == sorted(["p1", "p1_c1", "p1_c2"])

    def test_toss_parent_nodes(
        self,
        doc_store: SimpleDocumentStore,
        query_result_parent_nodes: list[NodeWithScore],
    ):
        default_postprocessor: GetChildNodesPostprocessor = GetChildNodesPostprocessor(doc_store=doc_store, keep_parent_nodes=False)
        result = default_postprocessor.postprocess_nodes(nodes=query_result_parent_nodes)
        assert len(result) == 2
        assert get_node_ids(result) == sorted(["p1_c1", "p1_c2"])


class Test1gp2p2c1c:
    @pytest.fixture
    def query_result_all_parent_nodes(self, example_1gp_2p_2c_1c: tuple[Node, Node, Node, Node, Node, Node]) -> list[NodeWithScore]:
        return score_nodes(nodes=[example_1gp_2p_2c_1c[1], example_1gp_2p_2c_1c[2]])

    @pytest.fixture
    def query_result_one_parent_node(self, example_1gp_2p_2c_1c: tuple[Node, Node, Node, Node, Node, Node]) -> list[NodeWithScore]:
        return score_nodes(nodes=[example_1gp_2p_2c_1c[1]])

    def test_1gp_2p_2c_1c(
        self,
        doc_store: SimpleDocumentStore,
        query_result_one_parent_node: list[NodeWithScore],
        query_result_all_parent_nodes: list[NodeWithScore],
    ):
        """Test the default behavior of the postprocessor with the 1gp_2p_2c_1c example."""

        # Fetch all child nodes.
        default_postprocessor: GetChildNodesPostprocessor = GetChildNodesPostprocessor(doc_store=doc_store)
        result = default_postprocessor.postprocess_nodes(nodes=query_result_all_parent_nodes)
        assert len(result) == 5
        assert get_node_ids(result) == sorted(["p1", "p2", "p1_c1", "p1_c2", "p2_c1"])

        # Fetch all child nodes.
        result = default_postprocessor.postprocess_nodes(nodes=query_result_one_parent_node)
        assert len(result) == 3
        assert get_node_ids(result) == sorted(["p1", "p1_c1", "p1_c2"])

    def test_toss_parent_nodes(
        self,
        doc_store: SimpleDocumentStore,
        query_result_one_parent_node: list[NodeWithScore],
        query_result_all_parent_nodes: list[NodeWithScore],
    ):
        default_postprocessor: GetChildNodesPostprocessor = GetChildNodesPostprocessor(doc_store=doc_store, keep_parent_nodes=False)
        result = default_postprocessor.postprocess_nodes(nodes=query_result_all_parent_nodes)
        assert len(result) == 3
        assert get_node_ids(result) == sorted(["p1_c1", "p1_c2", "p2_c1"])

        result = default_postprocessor.postprocess_nodes(nodes=query_result_one_parent_node)
        assert len(result) == 2
        assert get_node_ids(result) == sorted(["p1_c1", "p1_c2"])
