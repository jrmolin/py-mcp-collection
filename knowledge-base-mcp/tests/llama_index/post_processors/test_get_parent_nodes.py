import pytest
from llama_index.core.schema import Node, NodeWithScore
from llama_index.core.storage.docstore.simple_docstore import SimpleDocumentStore

from knowledge_base_mcp.llama_index.post_processors.get_parent_nodes import GetParentNodesPostprocessor
from tests.llama_index.post_processors.conftest import get_node_ids, score_nodes


@pytest.fixture
def doc_store():
    return SimpleDocumentStore()


def test_init(doc_store: SimpleDocumentStore):
    postprocessor = GetParentNodesPostprocessor(doc_store=doc_store)

    assert postprocessor.doc_store == doc_store
    assert postprocessor.minimum_coverage == 0.0
    assert postprocessor.maximum_size is None
    assert postprocessor.minimum_size is None


@pytest.fixture
def post_processor(doc_store: SimpleDocumentStore):
    return GetParentNodesPostprocessor(doc_store=doc_store)


class Test1p2c:
    @pytest.fixture
    def query_result_both_child_nodes(self, example_1p_2c: tuple[Node, Node, Node]) -> list[NodeWithScore]:
        return score_nodes(nodes=[example_1p_2c[1], example_1p_2c[2]])

    @pytest.fixture
    def query_result_one_child_node(self, example_1p_2c: tuple[Node, Node, Node]) -> list[NodeWithScore]:
        return score_nodes(nodes=[example_1p_2c[1]])

    def test_1p_2c(
        self,
        doc_store: SimpleDocumentStore,
        query_result_one_child_node: list[NodeWithScore],
        query_result_both_child_nodes: list[NodeWithScore],
    ):
        """Test the default behavior of the postprocessor with the 1p_2c example."""

        default_postprocessor: GetParentNodesPostprocessor = GetParentNodesPostprocessor(doc_store=doc_store)
        result = default_postprocessor.postprocess_nodes(nodes=query_result_both_child_nodes)
        assert len(result) == 1
        assert get_node_ids(result) == ["p1"]

        result = default_postprocessor.postprocess_nodes(nodes=query_result_one_child_node)
        assert len(result) == 1
        assert get_node_ids(result) == ["p1"]

    def test_minimum_size(
        self,
        doc_store: SimpleDocumentStore,
        query_result_one_child_node: list[NodeWithScore],
        query_result_both_child_nodes: list[NodeWithScore],
    ):
        custom_postprocessor: GetParentNodesPostprocessor = GetParentNodesPostprocessor(doc_store=doc_store, minimum_size=100)
        result = custom_postprocessor.postprocess_nodes(nodes=query_result_both_child_nodes)
        assert len(result) == 1
        assert get_node_ids(result) == ["p1"]

        result = custom_postprocessor.postprocess_nodes(nodes=query_result_one_child_node)
        assert len(result) == 1
        assert get_node_ids(result) == ["p1"]

    def test_maximum_size(
        self,
        doc_store: SimpleDocumentStore,
        query_result_one_child_node: list[NodeWithScore],
        query_result_both_child_nodes: list[NodeWithScore],
    ):
        custom_postprocessor: GetParentNodesPostprocessor = GetParentNodesPostprocessor(doc_store=doc_store, maximum_size=50)
        result = custom_postprocessor.postprocess_nodes(nodes=query_result_both_child_nodes)
        assert len(result) == 2
        assert get_node_ids(result) == ["p1_c1", "p1_c2"]

        result = custom_postprocessor.postprocess_nodes(nodes=query_result_one_child_node)
        assert len(result) == 1
        assert get_node_ids(result) == ["p1_c1"]

    def test_1_threshold(
        self,
        doc_store: SimpleDocumentStore,
        query_result_one_child_node: list[NodeWithScore],
        query_result_both_child_nodes: list[NodeWithScore],
    ):
        custom_postprocessor: GetParentNodesPostprocessor = GetParentNodesPostprocessor(doc_store=doc_store, minimum_coverage=0.9)
        result = custom_postprocessor.postprocess_nodes(nodes=query_result_both_child_nodes)
        assert len(result) == 1

        result = custom_postprocessor.postprocess_nodes(nodes=query_result_one_child_node)
        assert len(result) == 1

    def test_0_5_threshold(
        self,
        doc_store: SimpleDocumentStore,
        query_result_one_child_node: list[NodeWithScore],
        query_result_both_child_nodes: list[NodeWithScore],
    ):
        custom_postprocessor: GetParentNodesPostprocessor = GetParentNodesPostprocessor(doc_store=doc_store, minimum_coverage=0.5)
        result = custom_postprocessor.postprocess_nodes(nodes=query_result_both_child_nodes)
        assert len(result) == 1
        assert get_node_ids(result) == ["p1"]

        result = custom_postprocessor.postprocess_nodes(nodes=query_result_one_child_node)
        assert len(result) == 1
        assert get_node_ids(result) == ["p1"]

    def test_always_replace(
        self,
        doc_store: SimpleDocumentStore,
        query_result_one_child_node: list[NodeWithScore],
        query_result_both_child_nodes: list[NodeWithScore],
    ):
        custom_postprocessor: GetParentNodesPostprocessor = GetParentNodesPostprocessor(doc_store=doc_store, minimum_coverage=0.0)
        result = custom_postprocessor.postprocess_nodes(nodes=query_result_both_child_nodes)
        assert len(result) == 1
        assert get_node_ids(result) == ["p1"]

        result = custom_postprocessor.postprocess_nodes(nodes=query_result_one_child_node)
        assert len(result) == 1
        assert get_node_ids(result) == ["p1"]


class Test1gp2p2c1c:
    @pytest.fixture
    def query_result_all_child_nodes(self, example_1gp_2p_2c_1c: tuple[Node, Node, Node, Node, Node, Node]) -> list[NodeWithScore]:
        return score_nodes(nodes=[example_1gp_2p_2c_1c[3], example_1gp_2p_2c_1c[4], example_1gp_2p_2c_1c[5]])

    @pytest.fixture
    def query_result_one_child_node(self, example_1gp_2p_2c_1c: tuple[Node, Node, Node, Node, Node, Node]) -> list[NodeWithScore]:
        return score_nodes(nodes=[example_1gp_2p_2c_1c[3]])

    def test_1gp_2p_2c_1c(
        self,
        doc_store: SimpleDocumentStore,
        query_result_one_child_node: list[NodeWithScore],
        query_result_all_child_nodes: list[NodeWithScore],
    ):
        """Test the default behavior of the postprocessor with the 1gp_2p_2c_1c example."""

        # In the default configuration, all child nodes are merged into their corresponding parent node.
        default_postprocessor: GetParentNodesPostprocessor = GetParentNodesPostprocessor(doc_store=doc_store)
        result = default_postprocessor.postprocess_nodes(nodes=query_result_all_child_nodes)
        assert len(result) == 2
        assert get_node_ids(result) == ["p1", "p2"]

        # The one child node is merged into its parent node.
        result = default_postprocessor.postprocess_nodes(nodes=query_result_one_child_node)
        assert len(result) == 1
        assert get_node_ids(result) == ["p1"]

    def test_minimum_size(
        self,
        doc_store: SimpleDocumentStore,
        query_result_one_child_node: list[NodeWithScore],
        query_result_all_child_nodes: list[NodeWithScore],
    ):
        # All child nodes are merged into their corresponding parent node.
        custom_postprocessor: GetParentNodesPostprocessor = GetParentNodesPostprocessor(doc_store=doc_store, minimum_size=100)
        result = custom_postprocessor.postprocess_nodes(nodes=query_result_all_child_nodes)
        assert len(result) == 2
        assert get_node_ids(result) == ["p1", "p2"]

        # The one child node is merged into its parent node.
        result = custom_postprocessor.postprocess_nodes(nodes=query_result_one_child_node)
        assert len(result) == 1
        assert get_node_ids(result) == ["p1"]

    def test_maximum_size(
        self,
        doc_store: SimpleDocumentStore,
        query_result_one_child_node: list[NodeWithScore],
        query_result_all_child_nodes: list[NodeWithScore],
    ):
        # No child nodes are merged into their parent node as all of them are too large.
        custom_postprocessor: GetParentNodesPostprocessor = GetParentNodesPostprocessor(doc_store=doc_store, maximum_size=50)
        result = custom_postprocessor.postprocess_nodes(nodes=query_result_all_child_nodes)
        assert len(result) == 3
        assert get_node_ids(result) == ["p1_c1", "p1_c2", "p2_c1"]

        # The one child node is left as is.
        result = custom_postprocessor.postprocess_nodes(nodes=query_result_one_child_node)
        assert len(result) == 1
        assert get_node_ids(result) == ["p1_c1"]

    def test_0_9_threshold(
        self,
        doc_store: SimpleDocumentStore,
        query_result_one_child_node: list[NodeWithScore],
        query_result_all_child_nodes: list[NodeWithScore],
    ):
        # All child nodes are merged into their corresponding parent node.
        custom_postprocessor: GetParentNodesPostprocessor = GetParentNodesPostprocessor(doc_store=doc_store, minimum_coverage=0.9)
        result = custom_postprocessor.postprocess_nodes(nodes=query_result_all_child_nodes)
        assert len(result) == 2
        assert get_node_ids(result) == ["p1", "p2"]

        # The one child node is not enough to end up in a parent node as our threshold is too high.
        result = custom_postprocessor.postprocess_nodes(nodes=query_result_one_child_node)
        assert len(result) == 1
        assert get_node_ids(result) == ["p1_c1"]

    def test_0_5_threshold(
        self,
        doc_store: SimpleDocumentStore,
        query_result_one_child_node: list[NodeWithScore],
        query_result_all_child_nodes: list[NodeWithScore],
    ):
        custom_postprocessor: GetParentNodesPostprocessor = GetParentNodesPostprocessor(doc_store=doc_store, minimum_coverage=0.5)
        result = custom_postprocessor.postprocess_nodes(nodes=query_result_all_child_nodes)
        assert len(result) == 2
        assert get_node_ids(result) == ["p1", "p2"]

        result = custom_postprocessor.postprocess_nodes(nodes=query_result_one_child_node)
        assert len(result) == 1
        assert get_node_ids(result) == ["p1"]

    def test_always_replace(
        self,
        doc_store: SimpleDocumentStore,
        query_result_one_child_node: list[NodeWithScore],
        query_result_all_child_nodes: list[NodeWithScore],
    ):
        custom_postprocessor: GetParentNodesPostprocessor = GetParentNodesPostprocessor(doc_store=doc_store, minimum_coverage=0.5)
        result = custom_postprocessor.postprocess_nodes(nodes=query_result_all_child_nodes)
        assert len(result) == 2
        assert get_node_ids(result) == ["p1", "p2"]

        result = custom_postprocessor.postprocess_nodes(nodes=query_result_one_child_node)
        assert len(result) == 1
        assert get_node_ids(result) == ["p1"]
