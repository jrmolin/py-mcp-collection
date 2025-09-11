import pytest
from inline_snapshot import snapshot

from github_research_mcp.clients.github import get_github_client
from github_research_mcp.models.repository.tree import RepositoryTree, RepositoryTreeDirectory
from github_research_mcp.servers.public import PublicServer
from github_research_mcp.servers.repository import RepositoryServer


@pytest.fixture
def public_server():
    return PublicServer(repository_server=RepositoryServer(github_client=get_github_client()), owner_allowlist=["strawgate"])


async def test_public_server(public_server: PublicServer):
    assert public_server is not None


async def test_public_server_find_files(public_server: PublicServer):
    files = await public_server.find_files(owner="strawgate", repo="github-issues-e2e-test", include=[".py"], exclude=None)
    assert files == snapshot(
        RepositoryTree(
            directories=[
                RepositoryTreeDirectory(
                    path="src",
                    files=[
                        "__init__.py",
                        "cli.py",
                        "existential_coder.py",
                        "oracle.py",
                        "philosopher_agent.py",
                        "utils.py",
                        "zen_master.py",
                    ],
                ),
                RepositoryTreeDirectory(path="tests", files=["__init__.py", "test_existential_coder.py"]),
            ],
            files=[".python-version", "main.py"],
        )
    )
