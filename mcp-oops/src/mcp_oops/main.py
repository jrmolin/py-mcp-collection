import asyncio
from functools import wraps
from pathlib import Path
from typing import Any

import asyncclick as click
import yaml
from fastmcp import Client, FastMCP
from mcp.types import TextContent, ImageContent, EmbeddedResource

class MCPoopsError(Exception):

    def __init__(self, message: str):
        self.message = message

class MCPoopsResponseTooLargeError(MCPoopsError):
    
    def __init__(self, tool: str, size: int, max_size: int):
        super().__init__(f"Response for tool {tool} is too large: {size} bytes. The maximum size is {max_size} bytes.")


def error_on_large_response(tool_name: str, tool_response: list[TextContent | ImageContent | EmbeddedResource], max_size: int):
    total_size = 0

    for item in tool_response:
        if isinstance(item, TextContent):
            total_size += len(item.text)
        elif isinstance(item, ImageContent):
            total_size += len(item.data)
        elif isinstance(item, EmbeddedResource):
            total_size += len(item.resource.text)

    if total_size > max_size:
        raise MCPoopsResponseTooLargeError(tool_name, total_size, max_size)


@click.command()
@click.option("--mcp-config", type=click.Path(exists=True), required=True, help="The path to the MCP Server config file")
@click.option("--mcp-transport", type=click.Choice(["stdio", "sse", "streamable-http"]), default="stdio", help="The transport to use for the MCP Server")
async def cli(mcp_config: str, mcp_transport: str):
    config_contents = Path(mcp_config).read_text(encoding="utf-8")
    config = yaml.safe_load(config_contents)

    client = Client(config)

    async with client:
        proxy = FastMCP.as_proxy(client)

        original_call_tool = proxy.client.call_tool

        @wraps(proxy.client.call_tool)
        async def call_tool(key: str, arguments: dict[str, Any]):
            print(f"Calling tool: {key} with arguments: {arguments}")
            response = await original_call_tool(key, arguments)
            error_on_large_response(key, response, 200_000)
            return response

        proxy.client.call_tool = call_tool

        await proxy.run_async(transport=mcp_transport)


def run_mcp():
    asyncio.run(cli())


if __name__ == "__main__":
    run_mcp()
