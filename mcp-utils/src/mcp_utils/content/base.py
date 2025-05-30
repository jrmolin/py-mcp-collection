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
    return content_to_string(content)[:max_length]

def preview_contents(
    contents: list[TextContent | ImageContent | BlobResourceContents | TextResourceContents | EmbeddedResource],
    max_length: int = 100,
) -> list[str]:
    """Preview the data in a list of MCP Content objects.

    Args:
        contents: The list of content objects to preview.
        max_length: The maximum length of each preview.

    Returns:
        A list of strings of the previews.
    """
    return [preview_content(item, max_length) for item in contents]


def content_to_string(
    content: TextContent | ImageContent | BlobResourceContents | TextResourceContents | EmbeddedResource,
) -> str:
    """Pull the data out of an MCP Content object.

    Args:
        content: The content object to pull the data out of.

    Returns:
        The data from the content object.
    """

    if isinstance(content, TextContent):
        return content.text
    if isinstance(content, ImageContent):
        return content.data
    if isinstance(content, BlobResourceContents):
        return content.blob
    if isinstance(content, TextResourceContents):
        return content.text
    if isinstance(content, EmbeddedResource):
        return content_to_string(content.resource)

    msg = f"Unsupported content type: {type(content)}"
    raise ValueError(msg)


def content_to_string_list(
    content: list[TextContent | ImageContent | BlobResourceContents | TextResourceContents | EmbeddedResource],
) -> list[str]:
    """Convert a list of content to a list of strings.

    Args:
        content: The list of content to convert.

    Returns:
        A list of strings.
    """

    return [content_to_string(item) for item in content]


def contents_length(contents: list[TextContent | ImageContent | BlobResourceContents | TextResourceContents | EmbeddedResource]) -> int:
    """Get the length of the data in a list of MCP Content objects.

    Args:
        contents: The list of content objects to get the length of.

    Returns:
        The length of the data in the list of content objects.
    """
    return sum(content_length(item) for item in contents)


def content_length(content: TextContent | ImageContent | BlobResourceContents | TextResourceContents | EmbeddedResource) -> int:
    """Get the length of the data in an MCP Content object.

    Args:
        content: The content object to get the length of.

    Returns:
        The length of the data in the content object.
    """

    return len(content_to_string(content))