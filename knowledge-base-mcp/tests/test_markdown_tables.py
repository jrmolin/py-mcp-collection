from textwrap import dedent

from knowledge_base_mcp.llama_index.node_parsers.markdown_element import MarkdownElementNodeParser


def test_simple_table(parser: MarkdownElementNodeParser, text_node):
    markdown = dedent("""
        | Name  | Age |
        |-------|-----|
        | Alice |  30 |
        | Bob   |  25 |
    """)
    nodes = parser.get_nodes_from_node(text_node(markdown))
    # A blank line node followed by the table node
    assert len(nodes) == 1
    # Second node is the table node
    assert nodes[0].metadata["markdown_type"] == "table"
    content = nodes[0].get_content()
    assert content == "| Name | Age |\n|------|-----|\n| Alice | 30 |\n| Bob | 25 |"
    assert "Name" in content
    assert "Age" in content
    assert "Alice" in content
    assert "30" in content
    assert "Bob" in content
    assert "25" in content


def test_table_with_inline_formatting(parser: MarkdownElementNodeParser, text_node):
    markdown = dedent("""
        | Name      | Description        |
        |-----------|--------------------|
        | *Alice*   | `Developer`        |
        | **Bob**   | _Designer_         |
    """)
    nodes = parser.get_nodes_from_node(text_node(markdown))
    assert len(nodes) == 1

    # Second node is the table node
    assert nodes[0].metadata["markdown_type"] == "table"
    content = nodes[0].get_content()

    # Inline formatting should be present as text (not markdown)
    assert (
        content
        == dedent("""
        | Name | Description |
        |------|-------------|
        | *Alice* | `Developer` |
        | **Bob** | *Designer* |
    """).strip()
    )
    assert "Alice" in content
    assert "Developer" in content
    assert "Bob" in content
    assert "Designer" in content
