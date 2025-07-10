import asyncio
from collections.abc import AsyncIterator, Callable
from functools import wraps
from pathlib import Path
from typing import Any, Literal

import asyncclick as click
from fastmcp import FastMCP
from fastmcp.tools import FunctionTool

from filesystem_operations_mcp.filesystem.file_system import FileSystem
from filesystem_operations_mcp.filesystem.view import customizable_file, customizable_file_materializer
from filesystem_operations_mcp.logging import BASE_LOGGER

logger = BASE_LOGGER.getChild("main")


ROOT_DIR_HELP = "The allowed filesystem paths for filesystem operations. Defaults to the current working directory for the server."
MAX_SIZE_HELP = "The maximum size of a result in bytes before throwing an exception. Defaults to 400 kb or about 100k tokens."
SERIALIZE_AS_HELP = "The format to serialize the response in. Defaults to Yaml"
MCP_TRANSPORT_HELP = "The transport to use for the MCP server. Defaults to stdio."


def materializer(func: Callable[..., AsyncIterator[Any]]) -> Callable[..., Any]:
    """
    A decorator to convert an asynchronous generator function's output to a list.
    """

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> list[Any]:  # pyright: ignore[reportAny]
        async_gen: AsyncIterator[Any] = func(*args, **kwargs)
        return [item async for item in async_gen]  # pyright: ignore[reportAny]

    return wrapper


@click.command()
@click.option("--root-dir", type=str, default=Path.cwd(), help=ROOT_DIR_HELP)
@click.option("--mcp-transport", type=click.Choice(["stdio", "sse", "streamable-http"]), default="stdio", help=MCP_TRANSPORT_HELP)
async def cli(root_dir: str, mcp_transport: Literal["stdio", "sse", "streamable-http"]):
    mcp: FastMCP[None] = FastMCP(name="Local Filesystem Operations MCP")

    file_system = FileSystem(Path(root_dir))

    mcp.add_tool(
        FunctionTool.from_function(name="find_files", fn=customizable_file_materializer(file_system.afind_files), output_schema=None)
    )
    mcp.add_tool(
        FunctionTool.from_function(name="search_files", fn=customizable_file_materializer(file_system.asearch_files), output_schema=None)
    )
    mcp.add_tool(FunctionTool.from_function(fn=customizable_file_materializer(file_system.get_structure), output_schema=None))
    mcp.add_tool(FunctionTool.from_function(fn=customizable_file(file_system.get_file), output_schema=None))

    mcp.add_tool(FunctionTool.from_function(file_system.create_file, output_schema=None))
    mcp.add_tool(FunctionTool.from_function(file_system.append_file, output_schema=None))
    mcp.add_tool(FunctionTool.from_function(file_system.delete_file_lines, output_schema=None))
    mcp.add_tool(FunctionTool.from_function(file_system.replace_file_lines, output_schema=None))
    mcp.add_tool(FunctionTool.from_function(file_system.insert_file_lines, output_schema=None))
    mcp.add_tool(FunctionTool.from_function(file_system.delete_file, output_schema=None))
    mcp.add_tool(FunctionTool.from_function(file_system.read_file_lines, output_schema=None))

    mcp.add_tool(FunctionTool.from_function(file_system.create_directory, output_schema=None))
    mcp.add_tool(FunctionTool.from_function(file_system.delete_directory, output_schema=None))
    # mcp.add_tool(FunctionTool.from_function(caller_controlled_directory_fields(file_system.get_root)))
    # mcp.add_tool(FunctionTool.from_function(caller_controlled_directory_fields(file_system.get_structure)))
    # mcp.add_tool(FunctionTool.from_function(caller_controlled_file_fields(file_system.get_files)))
    # mcp.add_tool(FunctionTool.from_function(caller_controlled_directory_fields(file_system.get_directories)))
    # mcp.add_tool(FunctionTool.from_function(file_system.get_file_matches))
    # mcp.add_tool(FunctionTool.from_function(caller_controlled_file_fields(file_system.find_files)))
    # mcp.add_tool(FunctionTool.from_function(caller_controlled_directory_fields(file_system.find_dirs)))
    # mcp.add_tool(FunctionTool.from_function(caller_controlled_file_fields(file_system.search_files)))

    # mcp.add_tool(FunctionTool.from_function(file_system.create_file))
    # mcp.add_tool(FunctionTool.from_function(file_system.append_file))
    # mcp.add_tool(FunctionTool.from_function(file_system.delete_file_lines))
    # mcp.add_tool(FunctionTool.from_function(file_system.replace_file_lines))
    # mcp.add_tool(FunctionTool.from_function(file_system.insert_file_lines))
    # mcp.add_tool(FunctionTool.from_function(file_system.delete_file))

    # mcp.add_tool(FunctionTool.from_function(file_system.create_directory))
    # mcp.add_tool(FunctionTool.from_function(file_system.delete_directory))

    await mcp.run_async(transport=mcp_transport)


def run_mcp():
    asyncio.run(cli())


if __name__ == "__main__":
    run_mcp()
