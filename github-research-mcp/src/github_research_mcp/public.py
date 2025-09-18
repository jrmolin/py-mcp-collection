import asyncio
import os
from typing import Any, Literal

import asyncclick as click
from fastmcp import FastMCP
from fastmcp.server.middleware.logging import StructuredLoggingMiddleware
from fastmcp.tools import FunctionTool
from githubkit.github import GitHub

from github_research_mcp.clients.elasticsearch import get_elasticsearch_client
from github_research_mcp.clients.github import get_github_client
from github_research_mcp.sampling.handler import get_sampling_handler
from github_research_mcp.servers.public import PublicServer
from github_research_mcp.servers.repository import RepositoryServer
from github_research_mcp.vendored.caching import InMemoryCache, MethodSettings, ResponseCachingMiddleware
from github_research_mcp.vendored.elasticsearch_cache import ElasticsearchCache


class ConfigurationError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


ONE_WEEK_IN_SECONDS = 60 * 60 * 24 * 7

minimum_stars_env: str | None = os.getenv("MINIMUM_STARS")
minimum_stars: int = int(minimum_stars_env) if minimum_stars_env else 10

owner_allowlist_env: str | None = os.getenv("OWNER_ALLOWLIST")
owner_allowlist: list[str] = [owner.strip() for owner in (owner_allowlist_env.split(",") if owner_allowlist_env else [])]

mcp = FastMCP[None](
    name="GitHub Research MCP",
    sampling_handler=get_sampling_handler(),
    sampling_handler_behavior="always",
)

github_client: GitHub[Any] = get_github_client()

repository_server: RepositoryServer = RepositoryServer(github_client=github_client)

public_server: PublicServer = PublicServer(
    repository_server=repository_server, minimum_stars=minimum_stars, owner_allowlist=owner_allowlist
)

mcp.add_tool(tool=FunctionTool.from_function(fn=public_server.summarize))

mcp.add_middleware(middleware=StructuredLoggingMiddleware(include_payloads=True))

cache_method_settings: MethodSettings = MethodSettings(
    call_tool={
        "ttl": ONE_WEEK_IN_SECONDS,
    },
)

if elasticsearch_client := get_elasticsearch_client():
    elasticsearch_cache: ElasticsearchCache = ElasticsearchCache(elasticsearch_client=elasticsearch_client)

    mcp.add_middleware(middleware=ResponseCachingMiddleware(cache_backend=elasticsearch_cache, method_settings=cache_method_settings))
else:
    mcp.add_middleware(middleware=ResponseCachingMiddleware(cache_backend=InMemoryCache(), method_settings=cache_method_settings))


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
