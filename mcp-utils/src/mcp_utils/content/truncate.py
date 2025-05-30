from mcp.types import TextContent


def truncate_text_content(
    content: TextContent,
    max_length: int,
) -> TextContent:
    """Truncate the data in an MCP TextContent object.
    """
    return TextContent(text=content.text[:max_length], type="text")
