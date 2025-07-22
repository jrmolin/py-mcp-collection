import asyncio
from collections.abc import AsyncIterator, Callable
from functools import wraps
from pathlib import Path
from typing import Any, Literal, get_args

import asyncclick as click
from fastmcp import FastMCP
from fastmcp.tools import FunctionTool
from rpygrep.types import RIPGREP_TYPE_LIST

from filesystem_operations_mcp.filesystem.file_system import FileSystem
from filesystem_operations_mcp.filesystem.view import FileExportableField, customizable_file_materializer
from filesystem_operations_mcp.logging import BASE_LOGGER

logger = BASE_LOGGER.getChild("main")


ROOT_DIR_HELP = "The allowed filesystem paths for filesystem operations. Defaults to the current working directory for the server."
MAX_SIZE_HELP = "The maximum size of a result in bytes before throwing an exception. Defaults to 400 kb or about 100k tokens."
SERIALIZE_AS_HELP = "The format to serialize the response in. Defaults to Yaml"
MCP_TRANSPORT_HELP = "The transport to use for the MCP server. Defaults to stdio."
DEFAULT_SUMMARIZE_HELP = "Whether to summarize the file fields by default. Defaults to True."


def materializer(func: Callable[..., AsyncIterator[Any]]) -> Callable[..., Any]:
    """
    A decorator to convert an asynchronous generator function's output to a list.
    """

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> list[Any]:  # pyright: ignore[reportAny]
        async_gen: AsyncIterator[Any] = func(*args, **kwargs)
        return [item async for item in async_gen]  # pyright: ignore[reportAny]

    return wrapper


def get_file_type_options() -> list[str]:
    """Get the list of file types that can be used for find and search. File types are not the same as file extensions.

    Instead they represent a "group" of extensions that make it easier to exclude files that are not relevant to the search."""
    return list[str](get_args(RIPGREP_TYPE_LIST))


@click.command()
@click.option("--root-dir", type=str, default=Path.cwd(), help=ROOT_DIR_HELP)
@click.option("--mcp-transport", type=click.Choice(["stdio", "sse", "streamable-http"]), default="stdio", help=MCP_TRANSPORT_HELP)
@click.option("--default-summarize", type=bool, default=True, help=DEFAULT_SUMMARIZE_HELP)
async def cli(root_dir: str, mcp_transport: Literal["stdio", "sse", "streamable-http"], default_summarize: bool):
    mcp: FastMCP[None] = FastMCP(name="Local Filesystem Operations MCP")

    file_system = FileSystem(Path(root_dir))

    default_file_fields = FileExportableField(
        summarize=default_summarize,
    )

    _ = mcp.add_tool(
        FunctionTool.from_function(name="find_files", fn=customizable_file_materializer(file_system.afind_files, default_file_fields))
    )
    _ = mcp.add_tool(
        FunctionTool.from_function(name="search_files", fn=customizable_file_materializer(file_system.asearch_files, default_file_fields))
    )
    _ = mcp.add_tool(
        FunctionTool.from_function(name="get_structure", fn=file_system.get_structure)
    )
    _ = mcp.add_tool(
        FunctionTool.from_function(name="get_files", fn=customizable_file_materializer(file_system.aget_files, default_file_fields))
    )

    _ = mcp.add_tool(FunctionTool.from_function(name="get_file_type_options", fn=get_file_type_options))

    _ = mcp.add_tool(FunctionTool.from_function(file_system.create_file))
    _ = mcp.add_tool(FunctionTool.from_function(file_system.append_file))
    _ = mcp.add_tool(FunctionTool.from_function(file_system.delete_file_lines))
    _ = mcp.add_tool(FunctionTool.from_function(file_system.replace_file_lines_bulk))
    _ = mcp.add_tool(FunctionTool.from_function(file_system.insert_file_lines_bulk))
    _ = mcp.add_tool(FunctionTool.from_function(file_system.replace_file_lines))
    _ = mcp.add_tool(FunctionTool.from_function(file_system.insert_file_lines))
    _ = mcp.add_tool(FunctionTool.from_function(file_system.delete_file))
    _ = mcp.add_tool(FunctionTool.from_function(file_system.read_file_lines))

    _ = mcp.add_tool(FunctionTool.from_function(file_system.create_directory))
    _ = mcp.add_tool(FunctionTool.from_function(file_system.delete_directory))

    await mcp.run_async(transport=mcp_transport)


def run_mcp():
    asyncio.run(cli())


if __name__ == "__main__":
    run_mcp()
