import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from llama_index.core.indices.vector_store import VectorStoreIndex
from llama_index.core.schema import BaseNode, Document, MediaResource, Node, NodeRelationship
from syrupy.assertion import SnapshotAssertion

from knowledge_base_mcp.clients.knowledge_base import KnowledgeBaseClient
from knowledge_base_mcp.main import DEFAULT_DOCS_CROSS_ENCODER_MODEL
from knowledge_base_mcp.servers.ingest.filesystem import FilesystemIngestServer
from knowledge_base_mcp.servers.search.docs import DocumentationSearchServer
from tests.servers.conftest import embedding_model

if TYPE_CHECKING:
    from knowledge_base_mcp.servers.models.documentation import KnowledgeBaseResult
    from knowledge_base_mcp.servers.search.docs import DocumentationSearchResponse


@pytest.fixture
def documentation_search_server(knowledge_base_client: KnowledgeBaseClient):
    return DocumentationSearchServer(knowledge_base_client=knowledge_base_client, reranker_model=DEFAULT_DOCS_CROSS_ENCODER_MODEL)


def prepare_nodes_for_snapshot(nodes: list[BaseNode]) -> list[BaseNode]:
    node_guids_to_sequential: dict[str, int] = {}
    for node in nodes:
        node.embedding = None
        new_id = len(node_guids_to_sequential)

        node_guids_to_sequential[node.node_id] = new_id

        node.node_id = str(new_id)

    for node in nodes:
        for relationship_members in node.relationships.values():
            if isinstance(relationship_members, list):
                for relationship_member in relationship_members:
                    relationship_member.node_id = str(node_guids_to_sequential[relationship_member.node_id])
            else:
                relationship_members.node_id = str(node_guids_to_sequential[relationship_members.node_id])

    return nodes


@pytest.fixture
def filesystem_ingest_server(knowledge_base_client: KnowledgeBaseClient):
    return FilesystemIngestServer(knowledge_base_client=knowledge_base_client)


@pytest.fixture
def playground_beats():
    root_dir = Path("./playground/beats")
    if not root_dir.exists():
        # git clone --depth 1 --branch <branch_name> --single-branch <repo_url> <clone_path>

        # Clone commit 63a537a17839ef23b0cd4cd7d62e708319374b61 with depth 1 and single branch
        commit = "static-branch-e2e-tests"
        repo_url = "https://github.com/strawgate/beats.git"
        clone_path = "./playground/beats"
        git_clone_command = f"git clone --depth 1 --branch {commit} --single-branch {repo_url} {clone_path}"

        _ = subprocess.run(git_clone_command, check=False, shell=True)  # noqa: S602

    return root_dir.resolve()


class TestSearch:
    @pytest.fixture
    def documentation_search_server(
        self,
        knowledge_base_client: KnowledgeBaseClient,
    ):
        return DocumentationSearchServer(knowledge_base_client=knowledge_base_client, reranker_model=DEFAULT_DOCS_CROSS_ENCODER_MODEL)

    @pytest.fixture
    async def vector_store_index_with_documents(self, vector_store_index: VectorStoreIndex):
        document = Document(
            id_="doc1",
            text="Hello, world!",
            metadata={
                "knowledge_base": "test",
                "knowledge_base_type": "documentation",
                "title": "Hello, world document!",
            },
        )

        parent_node = Node(
            id_="parent_node",
            text_resource=MediaResource(text="Hello, world!"),
            extra_info={
                **document.metadata,
                "headings": "# Parent Node",
            },
        )

        node_one = Node(
            id_="node_one",
            text_resource=MediaResource(text="I'm just a Node, I am not a document!"),
            extra_info={
                **document.metadata,
                "headings": "## Node One",
            },
        )

        node_two = Node(
            id_="node_two",
            text_resource=MediaResource(text="I'm the second node, better than the first one!"),
            extra_info={
                **document.metadata,
                "headings": "## Node Two",
            },
        )

        node_three = Node(
            id_="node_three",
            text_resource=MediaResource(text="I'm the third node, better than any other node!"),
            extra_info={
                **document.metadata,
                "headings": "## Node Three",
            },
        )

        for node in [node_one, node_two, node_three]:
            node.relationships[NodeRelationship.PARENT] = parent_node.as_related_node_info()

        parent_node.relationships[NodeRelationship.CHILD] = [
            node_one.as_related_node_info(),
            node_two.as_related_node_info(),
            node_three.as_related_node_info(),
        ]

        if not embedding_model:
            msg = "Embedding model not available"
            raise TypeError(msg)

        _ = await embedding_model.acall(
            [
                node_one,
                node_two,
                node_three,
            ]
        )

        _ = await vector_store_index.vector_store.async_add(
            nodes=[node_one, node_two, node_three],
        )

        await vector_store_index.docstore.async_add_documents(
            docs=[document, parent_node],
        )

    async def test_search(
        self,
        documentation_search_server: DocumentationSearchServer,
        vector_store_index_with_documents: VectorStoreIndex,
        yaml_snapshot: SnapshotAssertion,
    ):
        response: DocumentationSearchResponse = await documentation_search_server.query("Who is the best?")

        assert response.query == "Who is the best?"

        assert response.summary.root == {"test": 3}

        assert len(response.results.root) == 1

        kb_results: dict[str, KnowledgeBaseResult] = response.results.root

        headings = kb_results["test"].root["Hello, world document!"].headings

        assert sorted(headings) == sorted(["# Parent Node"])

        assert response == yaml_snapshot

    # class TestBenchmark:
    #     @pytest.fixture
    #     async def vector_store_index_with_documents(self, filesystem_ingest_server: FilesystemIngestServer, playground_beats: Path):
    #         ingest_result: IngestResult | None = await filesystem_ingest_server.load_directory(
    #             knowledge_base="test",
    #             path=str(playground_beats / "docs"),
    #             background=False,
    #         )

    #         if not ingest_result:
    #             msg = "Failed to ingest documentation"
    #             raise TypeError(msg)

    #         assert ingest_result.parsed_nodes == 74

    #     async def test_search(
    #         self,
    #         documentation_search_server: DocumentationSearchServer,
    #         vector_store_index_with_documents: VectorStoreIndex,
    #         yaml_snapshot: SnapshotAssertion,
    #     ):
    #         """Benchmark searching over a larger number of documents."""

    #         start_time = time.time()
    #         response: SearchResponseWithSummary = await documentation_search_server.query("What do you do as a feature request triager?")

    #         end_time = time.time()

    #         duration = end_time - start_time

    #         assert duration < 1

    #         assert response.query == "What do you do as a feature request triager?"

    #         assert response.summary.root == {"test": 59}

    #         assert len(response.results) == 10

    #         # sort them by their "number" field
    #         response.results = sorted(response.results, key=lambda x: x.number)

    #         assert response.model_dump() == yaml_snapshot
