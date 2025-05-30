import pytest
from mcp.types import BlobResourceContents, EmbeddedResource, ImageContent, TextContent, TextResourceContents
from pydantic import HttpUrl

from mcp_utils.content.view import preview_content, read_content, size_content


def test_read_content_text_content():
    """Test read_content with TextContent."""
    content = TextContent(text="hello world", type="text")
    assert read_content(content) == "hello world"


def test_read_content_image_content():
    """Test read_content with ImageContent."""
    content = ImageContent(data="image data", mimeType="image/png", type="image")
    assert read_content(content) == "image data"


def test_read_content_blob_resource_contents():
    """Test read_content with BlobResourceContents."""
    content = BlobResourceContents(blob="blob data", mimeType="application/octet-stream", uri=HttpUrl("https://resource"))
    assert read_content(content) == "blob data"


def test_read_content_text_resource_contents():
    """Test read_content with TextResourceContents."""
    content = TextResourceContents(text="resource text", mimeType="text/plain", uri=HttpUrl("https://resource"))
    assert read_content(content) == "resource text"


def test_read_content_embedded_resource():
    """Test read_content with EmbeddedResource."""
    embedded_content = TextResourceContents(text="embedded text", mimeType="text/plain", uri=HttpUrl("https://resource"))
    content = EmbeddedResource(type="resource", resource=embedded_content)
    assert read_content(content) == "embedded text"


def test_read_content_unsupported_type():
    """Test read_content with an unsupported type."""
    class UnsupportedType:
        pass
    content = UnsupportedType()
    with pytest.raises(ValueError, match="Unsupported content type:"):
        read_content(content)  # type: ignore


def test_preview_content():
    """Test preview_content."""
    content = TextContent(text="This is a long string that should be truncated.", type="text")
    assert preview_content(content, max_length=10) == "This is a "
    assert preview_content(content, max_length=100) == "This is a long string that should be truncated."



def test_size_content_text_content():
    """Test size_content with TextContent."""
    content = TextContent(text="hello", type="text")
    assert size_content(content) == 5


def test_size_content_image_content():
    """Test size_content with ImageContent."""
    content = ImageContent(data="image data", mimeType="image/png", type="image")
    assert size_content(content) == 10


def test_size_content_blob_resource_contents():
    """Test size_content with BlobResourceContents."""
    content = BlobResourceContents(blob="blob data", mimeType="application/octet-stream", uri=HttpUrl("https://resource"))
    assert size_content(content) == 9


def test_size_content_text_resource_contents():
    """Test size_content with TextResourceContents."""
    content = TextResourceContents(text="resource text", mimeType="text/plain", uri=HttpUrl("https://resource"))
    assert size_content(content) == 13


def test_size_content_embedded_resource():
    """Test size_content with EmbeddedResource."""
    embedded_content = TextResourceContents(text="embedded text", mimeType="text/plain", uri=HttpUrl("https://resource"))
    content = EmbeddedResource(type="resource", resource=embedded_content)
    assert size_content(content) == 13


def test_size_content_unsupported_type():
    """Test size_content with an unsupported type."""
    class UnsupportedType:
        pass
    content = UnsupportedType()
    with pytest.raises(ValueError, match="Unsupported content type:"):
        size_content(content)  # type: ignore
