from textwrap import dedent

from knowledge_base_mcp.llama_index.node_parsers.markdown_element import MarkdownElementNodeParser

# Uses parser and text_node fixtures from conftest.py


def test_unordered_list_simple(parser: MarkdownElementNodeParser, text_node):
    parser.elements = ["list"]
    markdown = dedent("""
- Item 1
- Item 2
- Item 3
""").strip()
    nodes = parser.get_nodes_from_node(text_node(markdown))
    assert len(nodes) == 1
    assert nodes[0].metadata["markdown_type"] == "list"
    assert nodes[0].get_content().rstrip() == markdown


def test_ordered_list_simple(parser, text_node):
    parser.elements = ["list"]
    markdown = dedent("""
1. First
2. Second
3. Third
""").strip()
    nodes = parser.get_nodes_from_node(text_node(markdown))
    assert len(nodes) == 1
    assert nodes[0].metadata["markdown_type"] == "list"
    assert nodes[0].get_content().rstrip() == markdown


def test_nested_lists(parser, text_node):
    parser.elements = ["list"]
    markdown = dedent("""
- Item 1
  - Subitem 1.1
  - Subitem 1.2
- Item 2
""").strip()
    nodes = parser.get_nodes_from_node(text_node(markdown))
    # Should produce a blank line, single List node, with nested content
    assert len(nodes) == 1
    assert nodes[0].metadata["markdown_type"] == "list"
    assert nodes[0].get_content().rstrip() == markdown


def test_tight_vs_loose_lists(parser, text_node):
    # Tight list (no blank lines between items)
    parser.elements = ["list"]
    markdown_tight = dedent("""
- a
- b
- c
""").strip()
    nodes_tight = parser.get_nodes_from_node(text_node(markdown_tight))
    assert len(nodes_tight) == 1
    assert nodes_tight[0].metadata["markdown_type"] == "list"
    assert nodes_tight[0].get_content().rstrip() == markdown_tight

    # Loose list (blank lines between items)
    markdown_loose = dedent("""
- a

- b

- c
""").strip()
    nodes_loose = parser.get_nodes_from_node(text_node(markdown_loose))
    assert len(nodes_loose) == 1
    assert nodes_loose[0].metadata["markdown_type"] == "list"
    assert nodes_loose[0].get_content().rstrip() == markdown_loose
