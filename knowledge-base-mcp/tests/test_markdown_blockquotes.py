from knowledge_base_mcp.llama_index.node_parsers.markdown_element import MarkdownElementNodeParser


def test_simple_blockquote(parser: MarkdownElementNodeParser, text_node):
    parser.elements = ["block_quote"]
    markdown = "> This is a blockquote."
    nodes = parser.get_nodes_from_node(text_node(markdown))
    assert len(nodes) == 1
    assert nodes[0].metadata["markdown_type"] == "block_quote"
    assert nodes[0].get_content().rstrip() == markdown


def test_nested_blockquote(parser: MarkdownElementNodeParser, text_node):
    parser.elements = ["block_quote"]
    markdown = "> Outer\n> > Inner"
    nodes = parser.get_nodes_from_node(text_node(markdown))
    assert len(nodes) == 1
    assert nodes[0].metadata["markdown_type"] == "block_quote"
    assert nodes[0].get_content().rstrip() == "> Outer\n> \n> > Inner"


def test_blockquote_with_list(parser: MarkdownElementNodeParser, text_node):
    parser.elements = ["block_quote"]
    markdown = "> - Item 1\n> - Item 2"
    nodes = parser.get_nodes_from_node(text_node(markdown))
    assert len(nodes) == 1
    assert nodes[0].metadata["markdown_type"] == "block_quote"
    assert nodes[0].get_content().rstrip() == markdown
