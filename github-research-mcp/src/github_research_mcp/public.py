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
from github_research_mcp.servers.public import PublicServer
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


owner_allowlist_env: str | None = os.getenv("OWNER_ALLOWLIST")
owner_allowlist: list[str] = owner_allowlist_env.split(",") if owner_allowlist_env else []

mcp = FastMCP[None](
    name="GitHub Research MCP",
    sampling_handler=get_sampling_handler(),
    sampling_handler_behavior="always",
)

github_client: GitHub[Any] = get_github_client()

repository_server: RepositoryServer = RepositoryServer(github_client=github_client)

public_server: PublicServer = PublicServer(repository_server=repository_server, owner_allowlist=owner_allowlist)

mcp.add_middleware(middleware=LoggingMiddleware())

mcp.add_tool(tool=FunctionTool.from_function(fn=public_server.summarize))
mcp.add_tool(tool=FunctionTool.from_function(fn=public_server.find_files))


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
