import pytest
from llama_index.core.schema import TextNode

from knowledge_base_mcp.llama_index.node_parsers.markdown_element import MarkdownElementNodeParser


@pytest.fixture
def parser():
    """Fixture for the markdown element node parser."""
    return MarkdownElementNodeParser.from_defaults()


@pytest.fixture
def text_node():
    """Factory fixture for creating TextNode from markdown string."""

    def _make(markdown: str) -> TextNode:
        return TextNode(text=markdown)

    return _make
