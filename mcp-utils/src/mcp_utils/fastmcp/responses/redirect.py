import json
from copy import deepcopy
from pathlib import Path
from typing import Any

import aiofiles
from fastmcp import Context
from fastmcp.exceptions import ToolError
from mcp.types import EmbeddedResource, ImageContent, TextContent

from mcp_utils.content.split import split_text_content
from mcp_utils.content.view import read_content


async def redirect_to_split_tool_calls(
    ctx: Context,
    *,
    first_tool_name: str,
    first_tool_arguments: dict[str, Any],
    second_tool_name: str,
    second_tool_arguments: dict[str, Any],
    second_tool_response_argument: str,
    split_on_content_entries: bool = False,
    split_on_json_array_entries: bool = True,
    entries_per_tool_call: int = 10,
) -> list[list[TextContent | ImageContent | EmbeddedResource]]:
    """Redirect the result of any existing tool call to multiple tool calls.

    Args:
        first_tool_name: The name of the first tool to call.
        first_tool_arguments: The arguments to pass to the first tool.
        second_tool_name: The name of the second tool to call.
        second_tool_arguments: The arguments to pass to the second tool.
        second_tool_response_argument: The name of the argument to insert the result of the first tool call into.
        split_on_content_entries: Whether to split on the "Content" entries returned by the first tool. Default is False.
        split_on_json_array_entries: Whether to split on the "Content" entries returned by the first tool. Default is True.
        entries_per_tool_call: The number of entries to pass to each tool call. Default is 10.

    Returns:
        The result of the second tool call.
    """

    tools = await ctx.fastmcp.get_tools()
    first_tool = tools[first_tool_name]
    second_tool = tools[second_tool_name]

    first_tool_result = await first_tool.run(first_tool_arguments)

    second_tool_full_arguments = deepcopy(second_tool_arguments)

    entries: list[str] = []

    if split_on_content_entries:
        entries = [read_content(result) for result in first_tool_result]

    if split_on_json_array_entries:
        for result in first_tool_result:
            json_string = read_content(result)

            array = json.loads(json_string)

            if not isinstance(array, list):
                msg = f"Expected a list, got {type(array)}"
                raise ToolError(msg)

            for entry in array:
                entries.append(entry)

    results: list[list[TextContent | ImageContent | EmbeddedResource]] = []

    # split into batches of entries_per_tool_call size
    for i in range(0, len(entries), entries_per_tool_call):
        this_entries = entries[i : i + entries_per_tool_call]
        second_tool_full_arguments[second_tool_response_argument] = this_entries
        results.append(await second_tool.run(second_tool_full_arguments))

    return results


async def redirect_to_tool_call(
    ctx: Context,
    *,
    first_tool_name: str,
    first_tool_arguments: dict[str, Any],
    second_tool_name: str,
    second_tool_arguments: dict[str, Any],
    second_tool_response_argument: str,
) -> list[TextContent | ImageContent | EmbeddedResource]:
    """Redirect the result of any existing tool call to another tool call.

    Args:
        first_tool_name: The name of the first tool to call.
        first_tool_arguments: The arguments to pass to the first tool.
        second_tool_name: The name of the second tool to call.
        second_tool_arguments: The arguments to pass to the second tool.
        second_tool_response_argument: The name of the argument to insert the result of the first tool call into.

    Returns:
        The result of the second tool call.
    """

    tools = await ctx.fastmcp.get_tools()
    first_tool = tools[first_tool_name]
    second_tool = tools[second_tool_name]

    first_tool_result = await first_tool.run(first_tool_arguments)

    second_tool_full_arguments = deepcopy(second_tool_arguments)
    if len(first_tool_result) == 1:
        second_tool_full_arguments[second_tool_response_argument] = read_content(first_tool_result[0])
    else:
        second_tool_full_arguments[second_tool_response_argument] = [read_content(result) for result in first_tool_result]

    return await second_tool.run(second_tool_full_arguments)


async def redirect_to_split_files(
    ctx: Context,
    tool_name: str,
    arguments: dict,
    *,
    directory: Path,
    stem: str,
    extension: str,
    split_text_size: int,
) -> list[Path]:
    """Redirect any tool call to a local file.

    This is useful for debugging tools that are not available in the local environment.

    Args:
        tool_name: The name of the tool to redirect.
        arguments: The arguments to pass to the tool.
        directory: The path to the directory to write the contents to. The directory must already exist.
        stem: The stem of the file to write the contents to. For example
        extension: The extension of the file to write the contents to
        split_text_size: The size to split text contents into.

    Returns:
        True if the tool call was successful, False otherwise.
    """

    tools = await ctx.fastmcp.get_tools()
    tool = tools[tool_name]

    tool_call_result = await tool.run(arguments)

    return await write_contents_to_files(
        ctx,
        contents=tool_call_result,
        directory=directory,
        stem=stem,
        extension=extension,
        split_text_size=split_text_size,
    )


async def redirect_to_files(
    ctx: Context,
    tool_name: str,
    arguments: dict,
    *,
    directory: Path,
    stem: str,
    extension: str,
) -> list[Path]:
    """Redirect any tool call to a local file.

    This is useful for debugging tools that are not available in the local environment.

    Args:
        tool_name: The name of the tool to redirect.
        arguments: The arguments to pass to the tool.
        directory: The path to the directory to write the contents to. The directory must already exist.
        stem: The stem of the file to write the contents to. For example
        extension: The extension of the file to write the contents to

    Returns:
        True if the tool call was successful, False otherwise.
    """

    tools = await ctx.fastmcp.get_tools()
    tool = tools[tool_name]

    tool_call_result = await tool.run(arguments)

    return await write_contents_to_files(
        ctx,
        contents=tool_call_result,
        directory=directory,
        stem=stem,
        extension=extension,
    )


async def write_contents_to_files(
    ctx: Context,
    contents: list[TextContent | ImageContent | EmbeddedResource],
    *,
    directory: Path,
    stem: str,
    extension: str,
    split_text_size: int | None = None,
) -> list[Path]:
    """Write a list of contents each to its own file. The provided path should be a file name,
    but the directory and stem will be used to create the file name. By combining the directory and stem,
    as so: `Path(directory) / f"{stem}-{i}.{extension}"`.

    Args:
        contents: The contents to write to the file.
        directory: The path to the directory to write the contents to. The directory must already exist.
        stem: The stem of the file to write the contents to. For example
        extension: The extension of the file to write the contents to
        split_text_size: The size to split text contents into.

    Returns:
        The paths to the files that were written.
    """

    file_paths = []

    for i, content in enumerate(contents):
        content_string = read_content(content)

        if split_text_size is not None and len(content_string) > split_text_size and isinstance(content, TextContent):
            split_contents = split_text_content(content, split_text_size)

            condensed_stem = stem if len(contents) == 1 else f"{stem}-{i}"

            file_paths.extend(
                await write_contents_to_files(
                    ctx,
                    contents=split_contents,  # type: ignore
                    directory=directory,
                    stem=condensed_stem,
                    extension=extension,
                )
            )
            continue

        file_path = directory / f"{stem}-{i}.{extension}"

        await write_content_to_file(content, path=file_path)

        file_paths.append(file_path)

    return file_paths


async def write_content_to_file(
    content: TextContent | ImageContent | EmbeddedResource,
    *,
    path: Path,
) -> Path:
    """Write a single content to a file."""
    content_string = read_content(content)

    async with aiofiles.open(path, "w", encoding="utf-8") as f:
        await f.write(content_string)

    return path
