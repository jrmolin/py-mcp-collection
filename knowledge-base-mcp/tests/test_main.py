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


def test_main_imports():
    from knowledge_base_mcp.main import cli

    assert cli is not None


def test_markdown_element_node_parser_simple_headers(parser: MarkdownElementNodeParser, text_node):
    parser.split_on_headers = [1, 2, 3, 4, 5]
    markdown = """
# Title

Some intro text.

## Section 1

Content 1.

### Subsection

Subcontent.

## Section 2

Content 2.
"""
    nodes = parser.get_nodes_from_node(text_node(markdown))
    assert len(nodes) == 4

    assert nodes[0].metadata.get("header_path") == "/Title"
    assert nodes[0].metadata.get("markdown_type") == "text"
    assert nodes[0].get_content() == "Some intro text.\n\n\n"

    assert nodes[1].metadata.get("header_path") == "/Title/Section 1"
    assert nodes[1].metadata.get("markdown_type") == "text"
    assert nodes[1].get_content() == "Content 1.\n\n\n"

    assert nodes[2].metadata.get("header_path") == "/Title/Section 1/Subsection"
    assert nodes[2].metadata.get("markdown_type") == "text"
    assert nodes[2].get_content() == "Subcontent.\n\n\n"

    assert nodes[3].metadata.get("header_path") == "/Title/Section 2"
    assert nodes[3].metadata.get("markdown_type") == "text"
    assert nodes[3].get_content() == "Content 2.\n\n\n"


def test_markdown_element_node_parser_complex_headers(parser: MarkdownElementNodeParser, text_node):
    parser.split_on_headers = [1, 2, 3, 4, 5]
    markdown = """
# Title

Some intro text.

## Section 1 with *bold* text, `inline code`, [link](https://www.google.com) and a [link with title](https://www.google.com "Google")

test content
"""

    nodes = parser.get_nodes_from_node(text_node(markdown))
    assert len(nodes) == 2

    assert nodes[0].metadata.get("header_path") == "/Title"
    assert nodes[0].metadata.get("markdown_type") == "text"
    assert nodes[0].get_content() == "Some intro text.\n\n\n"

    assert (
        nodes[1].metadata.get("header_path")
        == '/Title/Section 1 with *bold* text, `inline code`, [link](https://www.google.com) and a [link with title](https://www.google.com "Google")'
    )
    assert nodes[1].metadata.get("markdown_type") == "text"
    assert nodes[1].get_content() == "test content\n\n\n"
