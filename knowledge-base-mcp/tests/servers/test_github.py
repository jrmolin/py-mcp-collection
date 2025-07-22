from textwrap import dedent
from typing import TYPE_CHECKING

import pytest
from llama_index.core.indices.vector_store import VectorStoreIndex
from llama_index.core.schema import BaseNode, MetadataMode
from syrupy.assertion import SnapshotAssertion

from knowledge_base_mcp.clients.knowledge_base import KnowledgeBaseClient
from knowledge_base_mcp.servers.github import GitHubSearchResponse, GitHubServer

if TYPE_CHECKING:
    from knowledge_base_mcp.servers.ingest.base import IngestResult


@pytest.fixture
def github_server(knowledge_base_client: KnowledgeBaseClient):
    return GitHubServer(knowledge_base_client=knowledge_base_client)


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


@pytest.mark.not_on_ci
class TestIngest:
    async def test_ingest(self, github_server: GitHubServer, vector_store_index: VectorStoreIndex, yaml_snapshot: SnapshotAssertion):
        ingest_result: IngestResult = await github_server.load_github_issues(
            knowledge_base="test",
            owner="strawgate",
            repo="gemini-for-github-demo",
        )

        assert ingest_result.parsed_nodes == 15

        nodes_by_id: dict[str, BaseNode] = vector_store_index.docstore.docs

        nodes: list[BaseNode] = list(nodes_by_id.values())

        # Sort nodes by their "number" field
        nodes.sort(key=lambda x: x.metadata.get("issue", 0))  # pyright: ignore[reportAny]

        node_one: BaseNode = nodes[13]

        node_one_content: str = node_one.get_content(metadata_mode=MetadataMode.NONE)

        assert (
            node_one_content
            == "/gemini can you summarize this repository and tell me what it is all about anyway? Please inlude information about commits, prs, and issues. Suggest improvements."
        )

        node_one_embed_content: str = node_one.get_content(metadata_mode=MetadataMode.EMBED)

        assert (
            node_one_embed_content
            == dedent("""
        repository: strawgate/gemini-for-github-demo
        title: Just what is this all about anyway?
        user.association: NONE

        /gemini can you summarize this repository and tell me what it is all about anyway? Please inlude information about commits, prs, and issues. Suggest improvements.""").strip()
        )

        assert node_one.metadata["knowledge_base"] == "test"
        assert node_one.metadata["knowledge_base_type"] == "github_issues"
        assert node_one.metadata["title"] == "Just what is this all about anyway?"
        assert node_one.metadata["state"] == "open"

        assert prepare_nodes_for_snapshot(nodes) == yaml_snapshot

    async def test_ingest_comments(
        self, github_server: GitHubServer, vector_store_index: VectorStoreIndex, yaml_snapshot: SnapshotAssertion
    ):
        ingest_result: IngestResult = await github_server.load_github_issues(
            knowledge_base="test",
            owner="strawgate",
            repo="gemini-for-github-demo",
            include_comments=True,
        )

        assert ingest_result.parsed_nodes == 74

        nodes_by_id: dict[str, BaseNode] = vector_store_index.docstore.docs

        nodes: list[BaseNode] = list(nodes_by_id.values())

        # Sort the nodes by the "id" field in the metadata
        nodes.sort(key=lambda x: x.metadata.get("id"))  # pyright: ignore[reportArgumentType]

        # Get the node with a "number" metadata field of 1
        node_one: BaseNode = next(node for node in nodes if node.metadata.get("issue") == 1 and node.metadata.get("type") == "issue")

        assert node_one.metadata["knowledge_base"] == "test"
        assert node_one.metadata["knowledge_base_type"] == "github_issues"
        assert node_one.metadata["type"] == "issue"
        assert node_one.metadata["issue"] == 1

        assert node_one.metadata["title"] == "The readme has nothing in it"
        assert node_one.metadata["state"] == "open"

        node_two: BaseNode = next(node for node in nodes if node.metadata.get("issue") == 1 and node.metadata.get("type") == "comment")

        node_two_content: str = node_two.get_content(metadata_mode=MetadataMode.NONE)

        assert "It appears that the `README.md` file is not empty" in node_two_content

        assert node_two.metadata["knowledge_base"] == "test"
        assert node_two.metadata["knowledge_base_type"] == "github_issues"
        assert node_two.metadata["type"] == "comment"

        assert prepare_nodes_for_snapshot(nodes) == yaml_snapshot

    @pytest.mark.not_on_ci
    async def test_ingest_logstash_comments(
        self, github_server: GitHubServer, vector_store_index: VectorStoreIndex, yaml_snapshot: SnapshotAssertion
    ):
        ingest_result: IngestResult = await github_server.load_github_issues(
            knowledge_base="logstash",
            owner="elastic",
            repo="logstash",
            include_comments=True,
        )

        assert ingest_result.parsed_nodes > 7000

        nodes_by_id: dict[str, BaseNode] = vector_store_index.docstore.docs

        nodes: list[BaseNode] = list(nodes_by_id.values())

        # Sort the nodes by the "id" field in the metadata
        nodes.sort(key=lambda x: x.metadata.get("id"))  # pyright: ignore[reportArgumentType]

        # Get the node with a "number" metadata field of 1
        node_one: BaseNode = next(node for node in nodes if node.metadata.get("issue") == 1487 and node.metadata.get("type") == "issue")

        assert node_one.metadata["knowledge_base"] == "logstash"
        assert node_one.metadata["knowledge_base_type"] == "github_issues"
        assert node_one.metadata["type"] == "issue"
        assert node_one.metadata["issue"] == 1487

        assert node_one.metadata["title"] == "New output: unix"
        assert node_one.metadata["state"] == "open"

        node_two: BaseNode = next(node for node in nodes if node.metadata.get("issue") == 1487 and node.metadata.get("type") == "comment")

        node_two_content: str = node_two.get_content(metadata_mode=MetadataMode.NONE)

        assert (
            "@mezzatto This is actually a cool idea! If you have already a working plugin, would be very good to add it to logstash-plugins org. Makes sense?"
            in node_two_content
        )

        assert node_two.metadata["knowledge_base"] == "logstash"
        assert node_two.metadata["knowledge_base_type"] == "github_issues"
        assert node_two.metadata["type"] == "comment"


@pytest.mark.not_on_ci
class TestSearch:
    @pytest.fixture(autouse=True)
    async def vector_store_index_with_comments(self, github_server: GitHubServer):
        ingest_result: IngestResult = await github_server.load_github_issues(
            knowledge_base="test",
            owner="strawgate",
            repo="gemini-for-github-demo",
            include_comments=True,
        )

        assert ingest_result.parsed_nodes == 74

    @pytest.fixture
    def github_search_server(self, knowledge_base_client: KnowledgeBaseClient):
        return GitHubServer(knowledge_base_client=knowledge_base_client)

    async def test_search(self, github_search_server: GitHubServer, yaml_snapshot: SnapshotAssertion):
        response: GitHubSearchResponse = await github_search_server.query(query="What do you do as a feature request triager?")

        assert response.query == "What do you do as a feature request triager?"

        assert response.summary.root == {"test": 74}

        assert len(response.results) == 8

        # sort them by their "number" field
        response.results = sorted(response.results, key=lambda x: x.number)

        assert response.model_dump() == yaml_snapshot

    async def test_search_issues_only(self, github_search_server: GitHubServer, yaml_snapshot: SnapshotAssertion):
        response: GitHubSearchResponse = await github_search_server.query(
            query="What do you do as a feature request triager?", issues_only=True
        )

        assert response.query == "What do you do as a feature request triager?"

        assert response.summary.root == {"test": 15}

        assert len(response.results) == 12

        # sort them by their "number" field
        response.results = sorted(response.results, key=lambda x: x.number)

        assert response.model_dump() == yaml_snapshot
