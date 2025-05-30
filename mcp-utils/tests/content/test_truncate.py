import pytest
from mcp.types import TextContent
from mcp_utils.content.truncate import truncate_text_content

def test_truncate_text_content_within_limit():
    """Test that truncate_text_content does not truncate when content is within the limit."""
    content = TextContent(text="This is a test string.", type="text")
    max_length = 50
    truncated_content = truncate_text_content(content, max_length)
    assert truncated_content.text == "This is a test string."

def test_truncate_text_content_at_limit():
    """Test that truncate_text_content does not truncate when content is exactly at the limit."""
    content = TextContent(text="This is a test string.", type="text")
    max_length = len("This is a test string.")
    truncated_content = truncate_text_content(content, max_length)
    assert truncated_content.text == "This is a test string."

def test_truncate_text_content_exceeding_limit():
    """Test that truncate_text_content truncates when content exceeds the limit."""
    content = TextContent(text="This is a test string that is too long.", type="text")
    max_length = 10
    truncated_content = truncate_text_content(content, max_length)
    assert truncated_content.text == "This is a "

def test_truncate_text_content_empty_string():
    """Test that truncate_text_content handles an empty string."""
    content = TextContent(text="", type="text")
    max_length = 10
    truncated_content = truncate_text_content(content, max_length)
    assert truncated_content.text == ""

def test_truncate_text_content_zero_limit():
    """Test that truncate_text_content handles a zero limit."""
    content = TextContent(text="This is a test string.", type="text")
    max_length = 0
    truncated_content = truncate_text_content(content, max_length)
    assert truncated_content.text == ""