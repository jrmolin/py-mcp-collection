import pytest
from dirty_equals import IsStr
from fastmcp import FastMCP
from fastmcp.client import Client
from fastmcp.client.transports import FastMCPTransport
from fastmcp.exceptions import ToolError
from fastmcp.tools import Tool
from inline_snapshot import snapshot

from github_research_mcp.clients.github import get_github_client
from github_research_mcp.servers.public import PublicServer
from github_research_mcp.servers.repository import RepositoryServer


@pytest.fixture
def public_server():
    return PublicServer(repository_server=RepositoryServer(github_client=get_github_client()), minimum_stars=0, owner_allowlist=[])


async def test_public_server(public_server: PublicServer):
    assert public_server is not None


async def test_public_server_summarize(public_server: PublicServer, fastmcp: FastMCP):
    fastmcp.add_tool(tool=Tool.from_function(fn=public_server.summarize))

    async with Client[FastMCPTransport](transport=fastmcp) as fastmcp_client:
        call_tool_result = await fastmcp_client.call_tool(
            "summarize",
            arguments={"owner": "strawgate", "repo": "github-issues-e2e-test"},
        )

    assert call_tool_result.structured_content == snapshot({"result": IsStr(min_length=100)})

    print(call_tool_result.structured_content["result"])  # pyright: ignore[reportOptionalSubscript]


async def test_public_server_summarize_ineligible(public_server: PublicServer, fastmcp: FastMCP):
    public_server.minimum_stars = 10

    fastmcp.add_tool(tool=Tool.from_function(fn=public_server.summarize))

    async with Client[FastMCPTransport](transport=fastmcp) as fastmcp_client:
        with pytest.raises(
            ToolError,
            match=f"Repository strawgate/github-issues-e2e-test is not eligible for summarization, it has less than {public_server.minimum_stars} stars and is not explicitly allowlisted.",
        ):
            await fastmcp_client.call_tool(
                "summarize",
                arguments={"owner": "strawgate", "repo": "github-issues-e2e-test"},
            )


async def test_public_server_summarize_ineligible_allowlisted(public_server: PublicServer, fastmcp: FastMCP):
    public_server.minimum_stars = 10
    public_server.owner_allowlist = ["strawgate"]

    fastmcp.add_tool(tool=Tool.from_function(fn=public_server.summarize))

    async with Client[FastMCPTransport](transport=fastmcp) as fastmcp_client:
        context = await fastmcp_client.call_tool(
            "summarize",
            arguments={"owner": "strawgate", "repo": "github-issues-e2e-test"},
        )

    assert context.structured_content == snapshot({"result": IsStr(min_length=100)})
