from mcp.types import TextContent


def split_text_content(
    content: TextContent,
    split_size: int,
) -> list[TextContent]:
    """Split a text content into a list of text contents, each of which is less than or equal to the split size."""

    if len(content.text) <= split_size:
        return [content]

    content_text = content.text
    contents = []

    while len(content_text) > split_size:
        contents.append(TextContent(text=content_text[:split_size], type="text"))
        content_text = content_text[split_size:]

    if len(content_text) > 0:
        contents.append(TextContent(text=content_text, type="text"))

    return contents
