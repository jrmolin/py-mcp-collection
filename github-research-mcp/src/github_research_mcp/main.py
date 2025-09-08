import asyncio
import os
from typing import Literal

import asyncclick as click
from fastmcp import FastMCP
from fastmcp.experimental.sampling.handlers.openai import OpenAISamplingHandler
from fastmcp.tools import FunctionTool
from openai import OpenAI

from github_research_mcp.servers.issues import IssuesServer


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


@click.command()
@click.option("--no-sampling", type=bool, default=False, help="Whether to disable tools that require sampling")
@click.option(
    "--mcp-transport", type=click.Choice(["stdio", "streamable-http"]), default="stdio", help="The transport to run the MCP server on"
)
async def cli(no_sampling: bool, mcp_transport: Literal["stdio", "streamable-http"]):
    sampling: bool = not no_sampling

    mcp: FastMCP[None] = FastMCP[None](
        name="GitHub Research MCP",
        sampling_handler=get_sampling_handler() if sampling else None,
    )

    issues_server = IssuesServer()
    mcp.add_tool(tool=FunctionTool.from_function(fn=issues_server.research_issue))
    mcp.add_tool(tool=FunctionTool.from_function(fn=issues_server.research_issues_by_keywords))

    if sampling:
        mcp.add_tool(tool=FunctionTool.from_function(fn=issues_server.summarize_issue))
        mcp.add_tool(tool=FunctionTool.from_function(fn=issues_server.summarize_issues_by_keywords))

    await mcp.run_async(transport=mcp_transport)


def run_mcp():
    asyncio.run(cli())


if __name__ == "__main__":
    run_mcp()
