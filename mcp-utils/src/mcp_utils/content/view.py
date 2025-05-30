from mcp.types import BlobResourceContents, EmbeddedResource, ImageContent, TextContent, TextResourceContents


def preview_content(
    content: TextContent | ImageContent | BlobResourceContents | TextResourceContents | EmbeddedResource,
    max_length: int = 100,
) -> str:
    """Preview the data in an MCP Content object.

    Args:
        content: The content object to preview.
        max_length: The maximum length of the preview.

    Returns:
        A string of the preview.
    """
    return _content_to_string(content, max_length)


def read_content(
    content: TextContent | ImageContent | BlobResourceContents | TextResourceContents | EmbeddedResource,
) -> str:
    """Read the data out of an MCP Content object."""
    return _content_to_string(content, None)


def size_content(
    content: TextContent | ImageContent | BlobResourceContents | TextResourceContents | EmbeddedResource,
) -> int:
    """Get the size of the data in an MCP Content object."""
    return len(_content_to_string(content, None))


def _content_to_string(
    content: TextContent | ImageContent | BlobResourceContents | TextResourceContents | EmbeddedResource,
    limit: int | None = None,
) -> str:
    """Pull the data out of an MCP Content object.

    Args:
        content: The content object to pull the data out of.

    Returns:
        The data from the content object.
    """

    if isinstance(content, TextContent):
        return content.text[:limit] if limit else content.text
    if isinstance(content, ImageContent):
        return content.data[:limit] if limit else content.data
    if isinstance(content, BlobResourceContents):
        return content.blob[:limit] if limit else content.blob
    if isinstance(content, TextResourceContents):
        return content.text[:limit] if limit else content.text
    if isinstance(content, EmbeddedResource):
        return _content_to_string(content.resource, limit)

    msg = f"Unsupported content type: {type(content)}"
    raise ValueError(msg)
