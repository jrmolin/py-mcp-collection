from __future__ import annotations

import asyncio
import functools
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

import asyncclick as click
import requests
import yaml
from fastmcp import Client, FastMCP
from fastmcp.contrib.tool_transformer.loader import ToolOverride, ToolOverrides
from fastmcp.contrib.tool_transformer.tool_transformer import transform_tool
from fastmcp.utilities.logging import get_logger
from fastmcp.utilities.mcp_config import MCPConfig, RemoteMCPServer, StdioMCPServer

from mcp_oops.hooks import get_post_call_hook

if TYPE_CHECKING:
    from fastmcp.tools import Tool as FastMCPTool

logger = get_logger(__name__)


MCP_CONFIG_HELP = "The path to the MCP Server config file"
LIMIT_RESPONSE_SIZE_HELP = "The maximum size (in bytes) of a response that is not redirected. Default is 200KB (200000 bytes)."
REDIRECT_RESPONSE_SIZE_HELP = "The maximum size (in bytes) of a response that is redirected. Default is 10MB (10000000 bytes)."
REDIRECT_RESPONSE_CHUNK_SIZE_HELP = "The size (in bytes) of each chunk of a redirected response. Default is 1MB (1000000 bytes)."
TOOL_OVERRIDES_HELP = "The path to the tool overrides file"
MCP_TRANSPORT_HELP = "The transport to use for the MCP Server"


class StdioMCPServerWithOverrides(StdioMCPServer, ToolOverrides):
    pass


class RemoteMCPServerWithOverrides(RemoteMCPServer, ToolOverrides):
    pass


class MCPConfigWithOverrides(MCPConfig):
    mcpServers: dict[str, StdioMCPServerWithOverrides | RemoteMCPServerWithOverrides]  # type: ignore # noqa: N815

    @classmethod
    def from_dict(cls, config: dict[str, Any]):
        return cls(mcpServers=config.get("mcpServers", config))


def install_tool(
    tool: FastMCPTool, frontend_server: FastMCP, limit_response_size: int, override: ToolOverride | None = None
) -> FastMCPTool:
    post_call_hook = get_post_call_hook(limit_response_size)

    if override is None:
        return transform_tool(
            tool=tool,
            add_to_server=frontend_server,
            post_call_hook=post_call_hook,
        )

    return transform_tool(
        tool=tool,
        add_to_server=frontend_server,
        name=override.name,
        description=override.description,
        parameter_overrides=override.parameter_overrides,
        post_call_hook=post_call_hook,
    )


async def install_tools(source_server: FastMCP, target_server: FastMCP, limit_response_size: int, tool_overrides: ToolOverrides) -> None:
    source_tools = await source_server.get_tools()
    for source_tool_name, source_tool in source_tools.items():
        install_tool(source_tool, target_server, limit_response_size, tool_overrides.tools.get(source_tool_name))


@click.group()
def cli():
    pass


def transport_options(func):
    @click.option("--oops-transport", type=click.Choice(["stdio", "sse", "streamable-http"]), default="stdio", help=MCP_TRANSPORT_HELP)
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


def limiter_options(func):
    @click.option("--limit-response-size", type=int, default=400_000, help=LIMIT_RESPONSE_SIZE_HELP)
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


@cli.command(
    "stdio",
    context_settings={
        "ignore_unknown_options": True,
        "allow_extra_args": True,
    },
)
# @click.option("--redirect-response-size", type=int, default=10_000_000, help=REDIRECT_RESPONSE_SIZE_HELP)
# @click.option("--redirect-response-chunk-size", type=int, default=1_000_000, help=REDIRECT_RESPONSE_CHUNK_SIZE_HELP)
@transport_options
@limiter_options
@click.pass_context
async def single_server_cli(
    ctx: click.Context,
    oops_transport: Literal["stdio", "streamable-http", "sse"],
    limit_response_size: int,
    # redirect_response_size: int,
    # redirect_response_chunk_size: int,
):
    args: list[str] = ctx.args

    logger.info(f"Running MCP Server with args: {args}")

    mcp_config = MCPConfig(
        mcpServers={
            "mcp-oops": StdioMCPServer(
                command=args[0],
                args=args[1:],
            ),
        }
    )

    proxy = FastMCP.as_proxy(backend=mcp_config, name="mcp-oops")

    frontend_server = FastMCP(name="frontend")

    # In single server mode we dont have any overrides, just circuit breakers
    await install_tools(proxy, frontend_server, limit_response_size, ToolOverrides(tools={}))

    tools = await frontend_server.get_tools()
    logger.info("Frontend servers now provides the following tools: %s", [tool.name for tool in tools.values()])

    await frontend_server.run_async(transport=oops_transport)

    await proxy.run_async(transport=oops_transport)


MCP_TRANSPORT_HELP = """
The transport to use for the MCP server.

- stdio: Use the standard input and output streams.
- sse: Use Server-Sent Events.
- streamable-http: Use the Streamable HTTP transport.
"""


def get_config(config_file: str) -> MCPConfigWithOverrides:
    config_raw: str
    if config_file.startswith("https://"):
        config_raw = requests.get(config_file, timeout=10).text
    else:
        config_raw = Path(config_file).read_text(encoding="utf-8")

    return MCPConfigWithOverrides.model_validate(yaml.safe_load(config_raw))


@cli.command()
@transport_options
@limiter_options
@click.argument(
    "config-file",
    type=click.Path(exists=True),
)
@click.option(
    "--logging-level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]),
    default="INFO",
    help="The logging level to use for the agent.",
)
async def config(
    oops_transport: Literal["stdio", "sse", "streamable-http"],
    limit_response_size: int,
    config_file: str,
    logging_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
):
    config = get_config(config_file)

    logger.setLevel(logging_level)

    # Create a frontend server to provide tools and our Agents
    frontend_server = FastMCP(name="frontend")

    # For each MCP Server, create a client and transform the tools onto the frontend server
    for server_name, server_config in config.mcpServers.items():
        backend_client = Client(MCPConfig(mcpServers={server_name: server_config}))

        backend_server = FastMCP.as_proxy(backend_client)

        await install_tools(backend_server, frontend_server, limit_response_size, ToolOverrides(tools=server_config.tools))

    tools = await frontend_server.get_tools()
    logger.info("Frontend servers now provides the following tools: %s", [tool.name for tool in tools.values()])

    # Run the frontend server
    await frontend_server.run_async(transport=oops_transport)


def run_mcp():
    asyncio.run(cli())


if __name__ == "__main__":
    run_mcp()
