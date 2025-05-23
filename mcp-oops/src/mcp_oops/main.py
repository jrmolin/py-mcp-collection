import asyncio
import json
from pathlib import Path
from typing import Literal

import asyncclick as click
import yaml
from fastmcp import Client, FastMCP
from fastmcp.tools.tool import Tool as FastMCPTool
from fastmcp.utilities.logging import get_logger

from mcp_oops.intercepting.proxy_tool import InterceptingProxyTool

logger = get_logger(__name__)


MCP_CONFIG_HELP = "The path to the MCP Server config file"
MAX_RESPONSE_SIZE_HELP = "The maximum size (in KB) of a response that is not redirected. Default is 200KB."
MAX_REDIRECTED_RESPONSE_SIZE_HELP = "The maximum size (in KB) of a response that is redirected. Default is 10MB."
SPLIT_REDIRECTED_RESPONSES_HELP = "The size (in KB) of each chunk of a redirected response. Default is 1MB."
TOOL_DEFAULTS_HELP = "The path to the tool defaults file"
MCP_TRANSPORT_HELP = "The transport to use for the MCP Server"


def _proxy_passthrough():
    pass


def add_redirect_to_schema(schema: dict):
    schema.get("properties", {}).update(
        {
            "redirect_to": {
                "type": "string",
                "description": "The file to redirect results to",
            }
        }
    )


@click.command()
@click.option("--mcp-config", type=click.Path(exists=True), required=True, help=MCP_CONFIG_HELP)
@click.option("--max-response-size", type=int, default=200, help=MAX_RESPONSE_SIZE_HELP)
@click.option("--max-redirected-response-size", type=int, default=10_000, help=MAX_REDIRECTED_RESPONSE_SIZE_HELP)
@click.option("--split-redirected-responses", type=int, default=1_000, help=SPLIT_REDIRECTED_RESPONSES_HELP)
@click.option("--tool-defaults", type=click.Path(exists=True), required=False, help=TOOL_DEFAULTS_HELP)
@click.option("--mcp-transport", type=click.Choice(["stdio", "sse", "streamable-http"]), default="stdio", help=MCP_TRANSPORT_HELP)
async def cli(
    mcp_config: str,
    mcp_transport: Literal["stdio", "streamable-http", "sse"],
    tool_defaults: str | None,
    max_response_size: int,
    max_redirected_response_size: int,
    split_redirected_responses: int,
):
    mcp = FastMCP(name="mcp-oops")

    config_contents = Path(mcp_config).read_text(encoding="utf-8")
    config = yaml.safe_load(config_contents)

    client = Client(config)

    async with client:

        result = await client.ping()
        await client.list_tools()

        proxy = FastMCP.as_proxy(client)

        proxy_tools: dict[str, FastMCPTool] = await proxy.get_tools()

        for tool in proxy_tools.values():
            new_input_schema = json.loads(json.dumps(tool.parameters))

            add_redirect_to_schema(new_input_schema)

            # Create an instance of our new InterceptingProxyTool
            proxy_tool = InterceptingProxyTool(
                client=client,  # type: ignore
                name=f"oops-{tool.name}",
                description=tool.description,
                parameters=new_input_schema,
                fn=_proxy_passthrough,
                annotations=tool.annotations,
                serializer=tool.serializer,
                max_response_size=max_response_size * 1024,
                max_redirected_response_size=max_redirected_response_size * 1024,
                split_redirected_responses=split_redirected_responses * 1024,
            )

            mcp._tool_manager.add_tool(proxy_tool)

        await mcp.run_async(transport=mcp_transport)

        # proxy.client.call_tool = new_tools

        # original_call_tool = proxy.client.call_tool

        # @wraps(proxy.client.call_tool)
        # async def call_tool(key: str, arguments: dict[str, Any]):
        #     print(f"Calling tool: {key} with arguments: {arguments}")
        #     response = await original_call_tool(key, arguments)
        #     error_on_large_response(key, response, 200_000)
        #     return response

        # proxy.client.call_tool = call_tool


def run_mcp():
    asyncio.run(cli())


if __name__ == "__main__":
    run_mcp()
