from typing import TYPE_CHECKING

import pytest

from knowledge_base_mcp.clients.knowledge_base import KnowledgeBaseClient
from knowledge_base_mcp.servers.ingest.filesystem import FilesystemIngestServer

if TYPE_CHECKING:
    from knowledge_base_mcp.servers.ingest.base import IngestResult


@pytest.fixture
def filesystem_ingest_server(knowledge_base_client: KnowledgeBaseClient):
    return FilesystemIngestServer(knowledge_base_client=knowledge_base_client)


class TestGitIngest:
    async def test_git_ingest(self, filesystem_ingest_server: FilesystemIngestServer):
        ingest_result: IngestResult | None = await filesystem_ingest_server.load_git_repository(
            knowledge_base="test",
            repository_url="https://github.com/elastic/logstash",
            branch="main",
            paths=["docs/extend"],
            background=False,
        )

        assert ingest_result is not None
        assert ingest_result.parsed_nodes > 70
