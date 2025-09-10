import asyncio
import os
from typing import Any, Literal

import asyncclick as click
from fastmcp import FastMCP
from fastmcp.experimental.sampling.handlers.openai import OpenAISamplingHandler
from fastmcp.server.middleware.logging import LoggingMiddleware
from fastmcp.tools import FunctionTool
from githubkit.github import GitHub
from openai import OpenAI

from github_research_mcp.clients.github import get_github_client
from github_research_mcp.servers.issues_or_pull_requests import IssuesOrPullRequestsServer
from github_research_mcp.servers.repository import RepositoryServer


class ConfigurationError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


def get_sampling_handler():
    default_model = os.getenv("OPENAI_MODEL")
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")

    if not default_model:
        msg = "You must set the OPENAI_MODEL environment variable or disable sampling via --no-sampling"
        raise ConfigurationError(msg)

    return OpenAISamplingHandler(
        default_model=default_model,  # pyright: ignore[reportArgumentType]
        client=OpenAI(api_key=api_key, base_url=base_url),
    )


disable_sampling = os.getenv("DISABLE_SAMPLING")

mcp = FastMCP[None](
    name="GitHub Research MCP",
    sampling_handler=None if disable_sampling else get_sampling_handler(),
)

github_client: GitHub[Any] = get_github_client()

repository_server: RepositoryServer = RepositoryServer(github_client=github_client)

issues_server: IssuesOrPullRequestsServer = IssuesOrPullRequestsServer(repository_server=repository_server, github_client=github_client)

mcp.add_tool(tool=FunctionTool.from_function(fn=issues_server.research_issue_or_pull_request))
mcp.add_tool(tool=FunctionTool.from_function(fn=issues_server.research_issues_or_pull_requests))

mcp.add_tool(tool=FunctionTool.from_function(fn=repository_server.get_readmes))
mcp.add_tool(tool=FunctionTool.from_function(fn=repository_server.get_files))
mcp.add_tool(tool=FunctionTool.from_function(fn=repository_server.count_file_extensions))
mcp.add_tool(tool=FunctionTool.from_function(fn=repository_server.find_files))
mcp.add_tool(tool=FunctionTool.from_function(fn=repository_server.search_files))

if not disable_sampling:
    mcp.add_tool(tool=FunctionTool.from_function(fn=repository_server.summarize))
    mcp.add_tool(tool=FunctionTool.from_function(fn=issues_server.summarize_issue_or_pull_request))
    mcp.add_tool(tool=FunctionTool.from_function(fn=issues_server.summarize_issues_or_pull_requests))

mcp.add_middleware(middleware=LoggingMiddleware())


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
