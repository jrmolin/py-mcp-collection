import asyncio
import os
from typing import Any, Literal

import asyncclick as click
from fastmcp import FastMCP
from fastmcp.tools import FunctionTool
from githubkit.github import GitHub

from github_research_mcp.clients.github import get_github_client
from github_research_mcp.sampling.google_genai import GoogleGenaiSamplingHandler
from github_research_mcp.servers.issues_or_pull_requests import IssuesOrPullRequestsServer
from github_research_mcp.servers.repository import RepositoryServer


class ConfigurationError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


def get_sampling_handler():
    return GoogleGenaiSamplingHandler(default_model=os.getenv("MODEL") or "gemini-2.5-flash")


disable_sampling = os.getenv("DISABLE_SAMPLING")

mcp = FastMCP[None](
    name="GitHub Research MCP",
    sampling_handler=None if disable_sampling else get_sampling_handler(),
)

github_client: GitHub[Any] = get_github_client()

repository_server: RepositoryServer = RepositoryServer(github_client=github_client)

issues_server: IssuesOrPullRequestsServer = IssuesOrPullRequestsServer(repository_server=repository_server, github_client=github_client)

mcp.add_tool(tool=FunctionTool.from_function(fn=issues_server.get_issue_or_pull_request))
mcp.add_tool(tool=FunctionTool.from_function(fn=issues_server.search_issues_or_pull_requests))

if not disable_sampling:
    mcp.add_tool(tool=FunctionTool.from_function(fn=repository_server.summarize))
    mcp.add_tool(tool=FunctionTool.from_function(fn=issues_server.research_issue_or_pull_request))

mcp.add_tool(tool=FunctionTool.from_function(fn=repository_server.get_files))
mcp.add_tool(tool=FunctionTool.from_function(fn=repository_server.get_human_readmes))
mcp.add_tool(tool=FunctionTool.from_function(fn=repository_server.get_agents_readmes))
mcp.add_tool(tool=FunctionTool.from_function(fn=repository_server.find_files))
mcp.add_tool(tool=FunctionTool.from_function(fn=repository_server.search_files))
mcp.add_tool(tool=FunctionTool.from_function(fn=repository_server.get_file_extensions))


@click.command()
@click.option(
    "--mcp-transport", type=click.Choice(["stdio", "streamable-http"]), default="stdio", help="The transport to run the MCP server on"
)
async def cli(mcp_transport: Literal["stdio", "streamable-http"]):
    await mcp.run_async(transport=mcp_transport)


def run_mcp():
    asyncio.run(cli())


if __name__ == "__main__":
    run_mcp()
