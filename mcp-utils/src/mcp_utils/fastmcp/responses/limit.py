from typing import Any

from fastmcp import Context
from fastmcp.exceptions import ToolError
from mcp.types import EmbeddedResource, ImageContent, TextContent

from mcp_utils.content.truncate import truncate_text_content
from mcp_utils.content.view import size_content


async def limit_tool_response(
    ctx: Context,
    *,
    tool_name: str,
    tool_arguments: dict[str, Any],
    limit: int,
) -> list[TextContent | ImageContent | EmbeddedResource]:
    """Limit the result of any existing tool call to a given number of bytes. Raises
    an error if the tool result exceeds the limit.

    Args:
        tool_name: The name of the tool to call.
        tool_arguments: The arguments to pass to the tool.
        limit: The maximum number of bytes before an error is raised.

    Returns:
        The tool response.
    """

    tools = await ctx.fastmcp.get_tools()
    tool = tools[tool_name]

    tool_response: list[TextContent | ImageContent | EmbeddedResource] = await tool.run(tool_arguments)

    tool_response_length = sum(size_content(item) for item in tool_response)

    if tool_response_length > limit:
        msg = f"Tool result was exceeded limit of {limit} bytes: {tool_response_length}"
        raise ToolError(msg)

    return tool_response


async def truncate_tool_response(
    ctx: Context,
    *,
    tool_name: str,
    tool_arguments: dict[str, Any],
    limit: int,
) -> list[TextContent | ImageContent | EmbeddedResource]:
    """Perform a tool call and limit the result to a given number of bytes. If the result
    exceeds the limit, and the result is a Text result, it will be truncated. If the result
    exceeds the limit and is an image, blob, or other type, an error will be raised.

    Args:
        tool_name: The name of the tool to call.
        tool_arguments: The arguments to pass to the tool.
        limit: The maximum number of bytes before an error is raised or truncation is performed.

    Returns:
        The tool response, truncated if needed and possible.
    """

    tools = await ctx.fastmcp.get_tools()
    tool = tools[tool_name]

    tool_response: list[TextContent | ImageContent | EmbeddedResource] = await tool.run(tool_arguments)

    tool_response_length = sum(size_content(item) for item in tool_response)

    if tool_response_length <= limit:
        return tool_response

    if not all(isinstance(content, TextContent) for content in tool_response):
        msg = "Truncate tool will only truncate text contents. The request size exceeds the limit and truncation is not allowed."
        raise ToolError(msg)

    accumulated_size = 0
    accumulated_contents: list[TextContent | ImageContent | EmbeddedResource] = []

    for content in tool_response:
        if not isinstance(content, TextContent):
            msg = "Truncate tool will only truncate text contents. The request size exceeds the limit and truncation is not allowed."
            raise ToolError(msg)

        if accumulated_size + size_content(content) <= limit:
            accumulated_contents.append(content)
            accumulated_size += size_content(content)
            continue

        accumulated_contents.append(truncate_text_content(content, limit - accumulated_size))
        break

    return accumulated_contents
