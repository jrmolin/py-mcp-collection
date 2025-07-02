from textwrap import dedent
from typing import Any

import pytest
from docling.datamodel.base_models import InputFormat
from docling.document_converter import FormatOption
from docling.pipeline.simple_pipeline import SimplePipeline
from llama_index.core.schema import BaseNode as LlamaBaseNode
from llama_index.core.schema import Document as LlamaDocument
from llama_index.core.schema import MediaResource
from llama_index.embeddings.fastembed import FastEmbedEmbedding
from syrupy.assertion import SnapshotAssertion

from knowledge_base_mcp.docling.html_backend import TrimmedHTMLDocumentBackend
from knowledge_base_mcp.llama_index.hierarchical_node_parsers.docling_hierarchical_node_parser import DoclingHierarchicalNodeParser
from knowledge_base_mcp.llama_index.hierarchical_node_parsers.hierarchical_node_parser import GroupNode, RootNode
from knowledge_base_mcp.llama_index.hierarchical_node_parsers.leaf_semantic_merging import LeafSemanticMergerNodeParser
from tests.conftest import (
    DoclingSample,
    get_docling_samples,
    organize_nodes_for_snapshot,
    serialize_nodes_for_snapshot,
    validate_relationships,
)

embedding_model: FastEmbedEmbedding | None = None
try:
    embedding_model = FastEmbedEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2", embedding_cache=None)
    test = embedding_model._model.embed(["Hello, world!"])  # pyright: ignore[reportPrivateUsage]
    fastembed_available = True
except Exception:
    fastembed_available = False


def get_root_node(nodes: list[LlamaBaseNode]) -> RootNode:
    return next(node for node in nodes if isinstance(node, RootNode))


def get_group_nodes(nodes: list[LlamaBaseNode]) -> list[GroupNode]:
    return [node for node in nodes if isinstance(node, GroupNode) and not isinstance(node, RootNode)]


def get_leaf_nodes(nodes: list[LlamaBaseNode]) -> list[LlamaBaseNode]:
    return [node for node in nodes if node.child_nodes is None]


def assert_source_relationship(document: LlamaBaseNode, node: LlamaBaseNode) -> None:
    assert node.source_node is not None, f"Node {node.node_id} has no source node"
    assert document.node_id == node.source_node.node_id, (
        f"The source of node {node.node_id} is not {document.node_id}, it's {node.source_node.node_id}"
    )


def assert_sibling_relationship(first_node: LlamaBaseNode, second_node: LlamaBaseNode) -> None:
    assert first_node.next_node is second_node.as_related_node_info()
    assert second_node.prev_node is first_node.as_related_node_info()


def assert_parent_child_relationship(parent: LlamaBaseNode, child: LlamaBaseNode) -> None:
    parent_id: str = parent.node_id
    child_id: str = child.node_id

    assert child.parent_node is not None, f"Child node {child_id} has no parent node"
    assert parent_id == child.parent_node.node_id, f"The parent of node {child_id} is not {parent_id}, it's {child.parent_node.node_id}"

    assert parent.child_nodes is not None, f"Parent node {parent_id} has no child nodes"
    assert child_id in [c.node_id for c in parent.child_nodes], f"Child node {child_id} is not in parent node {parent_id} child nodes"


def assert_not_isolated(node: LlamaBaseNode) -> None:
    is_isolated: bool = node.parent_node is None and node.child_nodes is None
    assert not is_isolated, f"Node {node.node_id} is isolated"


def test_init():
    assert DoclingHierarchicalNodeParser()


@pytest.fixture
def docling_hierarchical_node_parser() -> DoclingHierarchicalNodeParser:
    """Takes a list of Llama nodesfrom the Docling node parserand converts them to a list of Llama nodes with a hierarchical structure."""
    return DoclingHierarchicalNodeParser()


class TestDocuments:
    @pytest.fixture
    def source_document(self) -> LlamaDocument: ...

    @pytest.fixture
    def parsed_nodes(
        self, docling_hierarchical_node_parser: DoclingHierarchicalNodeParser, source_document: LlamaDocument
    ) -> list[LlamaBaseNode]:
        return docling_hierarchical_node_parser.get_nodes_from_documents(documents=[source_document])

    @pytest.fixture(autouse=True)
    def assert_has_root_node(self, parsed_nodes: list[LlamaBaseNode]) -> None:
        root_node: RootNode = get_root_node(nodes=parsed_nodes)
        assert root_node.next_node is None
        assert root_node.prev_node is None

    @pytest.fixture(autouse=True)
    def assert_source_document_relationships(self, source_document: LlamaDocument, parsed_nodes: list[LlamaBaseNode]) -> None:
        for node in parsed_nodes:
            assert_source_relationship(document=source_document, node=node)

    @pytest.fixture(autouse=True)
    def assert_no_isolation(self, parsed_nodes: list[LlamaBaseNode]) -> None:
        for node in parsed_nodes:
            assert_not_isolated(node=node)

    @pytest.fixture(autouse=True)
    def assert_valid_relationships(self, parsed_nodes: list[LlamaBaseNode]) -> None:
        validate_relationships(nodes=parsed_nodes)

    class TestSimpleHTML:
        @pytest.fixture
        def source_document(self) -> LlamaDocument:
            input_html: str = dedent(
                text="""
                <!DOCTYPE html>
                <html>
                    <head>
                        <title>A document with a title</title>
                    </head>
                    <body>
                        <header>
                            <h1>A document that is good for testing</h1>
                        </header>
                        <h1>A document with an h1 heading</h1>
                        <p>Some text under the first h1 heading</p>
                    </body>
                </html>
                """
            ).strip()

            return LlamaDocument(text_resource=MediaResource(text=input_html, mimetype="text/html"))

        @pytest.fixture
        def ideal_content(self) -> str:
            return dedent(
                text="""
                # A document that is good for testing

                # A document with an h1 heading

                Some text under the first h1 heading
            """
            ).strip()

        @pytest.fixture
        def ideal_metadata(self) -> dict[str, Any]:
            return {}

        def test_nodes(self, parsed_nodes: list[LlamaBaseNode], ideal_content: str) -> None:
            root: LlamaBaseNode = parsed_nodes[0]

            assert root.get_content() == ideal_content
            assert root.metadata == {}

            root_1: LlamaBaseNode = parsed_nodes[1]

            assert root_1.get_content() == "# A document that is good for testing"

            assert root_1.metadata == {
                "docling_label": "title",
                "docling_ref": "#/texts/0",
                "headings": ["# A document that is good for testing"],
            }

            root_1_1: LlamaBaseNode = parsed_nodes[2]
            assert root_1_1.get_content() == "# A document that is good for testing"
            assert root_1_1.metadata == {
                "docling_label": "title",
                "docling_ref": "#/texts/0",
                "headings": ["# A document that is good for testing"],
            }

            root_2: LlamaBaseNode = parsed_nodes[3]

            assert root_2.get_content() == "# A document with an h1 heading\n\nSome text under the first h1 heading"

            assert root_2.metadata == {
                "docling_label": "title",
                "docling_ref": "#/texts/1",
                "headings": ["# A document with an h1 heading"],
            }

            assert root.child_nodes == [
                root_1.as_related_node_info(),
                root_2.as_related_node_info(),
            ]

            root_2_1: LlamaBaseNode = parsed_nodes[4]
            root_2_2: LlamaBaseNode = parsed_nodes[5]

            assert root_2.child_nodes == [
                root_2_1.as_related_node_info(),
                root_2_2.as_related_node_info(),
            ]

            assert root_2_1.get_content() == "# A document with an h1 heading"

            assert root_2_1.metadata == {
                "docling_label": "title",
                "docling_ref": "#/texts/1",
                "headings": ["# A document with an h1 heading"],
            }

            assert root_2_1.parent_node == root_2.as_related_node_info()
            assert root_2_1.child_nodes is None
            assert root_2_1.prev_node is None
            assert root_2_1.next_node == root_2_2.as_related_node_info()

            assert root_2_2.get_content() == "Some text under the first h1 heading"
            assert root_2_2.metadata == {
                "docling_label": "text",
                "docling_ref": "#/texts/2",
                "headings": ["# A document with an h1 heading"],
            }

            assert root_2_2.parent_node == root_2.as_related_node_info()
            assert root_2_2.child_nodes is None
            assert root_2_2.prev_node == root_2_1.as_related_node_info()
            assert root_2_2.next_node is None

        class TestCollapsed:
            @pytest.fixture
            def docling_hierarchical_node_parser(self) -> DoclingHierarchicalNodeParser:
                return DoclingHierarchicalNodeParser(
                    collapse_nodes=True,
                    collapse_max_size=1024,
                    collapse_min_size=256,
                )

            def test_collapsed(self, parsed_nodes: list[LlamaBaseNode], ideal_content: str, yaml_snapshot: SnapshotAssertion) -> None:
                node_parser: DoclingHierarchicalNodeParser = DoclingHierarchicalNodeParser(collapse_nodes=True)
                collapsed_nodes: list[LlamaBaseNode] = node_parser._postprocess_parsed_nodes(nodes=parsed_nodes, parent_doc_map={})

                root: LlamaBaseNode = collapsed_nodes[0]

                assert root.get_content() == ideal_content
                assert root.metadata == {}

                root_1: LlamaBaseNode = collapsed_nodes[1]

                assert root_1.get_content() == "# A document that is good for testing"

                assert root_1.metadata == {
                    "docling_label": "title",
                    "docling_ref": "#/texts/0",
                    "headings": ["# A document that is good for testing"],
                }

                root_2: LlamaBaseNode = collapsed_nodes[2]

                assert root_2.get_content() == "# A document with an h1 heading"

                assert root_2.metadata == {
                    "docling_label": "title",
                    "docling_ref": "#/texts/1",
                    "headings": ["# A document with an h1 heading"],
                }

                root_3: LlamaBaseNode = collapsed_nodes[3]

                assert root_3.get_content() == "Some text under the first h1 heading"

                assert root_3.metadata == {
                    "docling_label": "text",
                    "docling_ref": "#/texts/2",
                    "headings": ["# A document with an h1 heading"],
                }

                assert root_3.parent_node == root.as_related_node_info()
                assert root_3.child_nodes is None
                assert root_3.prev_node == root_2.as_related_node_info()
                assert root_3.next_node is None

                assert organize_nodes_for_snapshot(nodes=collapsed_nodes) == yaml_snapshot

    class TestMixedHTML:
        @pytest.fixture
        def source_document(self) -> LlamaDocument:
            input_html: str = dedent(
                text="""
                <!DOCTYPE html>
                <html>
                    <head>
                        <title>A document with a title</title>
                    </head>
                    <body>
                        <p>This is initial content. It has <strong>bold text</strong> and a link to <a href="https://example.com">a site</a>.</p>

                        <h1>Main Heading</h1>
                        <p>Content under the first H1, with <em>italic text</em>.</p>

                        <h2>Section with a Table</h2>
                        <table>
                            <thead>
                                <tr><th>Column A</th><th>Column B</th></tr>
                            </thead>
                            <tbody>
                                <tr><td>Data 1A</td><td>Data 1B</td></tr>
                                <tr><td>Data 2A</td><td>Data 2B</td></tr>
                            </tbody>
                        </table>

                        <h2>Another Section with Lists</h2>
                        <p>Here are some lists.</p>
                        <ul>
                            <li>First item</li>
                            <li>Second item</li>
                        </ul>
                        <ol>
                            <li>Step 1</li>
                            <li>Step 2</li>
                        </ol>
                        <blockquote><p>This is a blockquote.</p></blockquote>

                        <h3>Subsection with Code</h3>
                        <p>An example of inline code is <code>document.getElementById()</code>.</p>
                        <pre><code class="language-js">
                function hello() {
                    console.log("Hello, world!");
                }
                        </code></pre>

                        <hr>

                        <h1>Final Heading</h1>
                        <p>A final paragraph with an image and some text that should not be formatted: 5 * 3 = 15.</p>
                        <img src="https://via.placeholder.com/100" alt="Placeholder Image">
                    </body>
                </html>
                """
            ).strip()

            return LlamaDocument(text_resource=MediaResource(text=input_html, mimetype="text/html"))

        @pytest.fixture
        def converted_content(self) -> str:
            # Notes:
            # - Docling does not support quotes/blockquotes
            # - Docling does not support inline code
            # - If the page has headers, any content before the first header is "outside" the body and excluded

            return dedent(
                text="""
                # Main Heading

                Content under the first H1, with italic text.

                ## Section with a Table

                | Column A   | Column B   |
                |------------|------------|
                | Data 1A    | Data 1B    |
                | Data 2A    | Data 2B    |

                ## Another Section with Lists

                Here are some lists.

                - First item
                - Second item

                1. Step 1
                2. Step 2

                This is a blockquote.

                ### Subsection with Code

                An example of inline code is document.getElementById().

                ```
                function hello() {
                    console.log("Hello, world!");
                }
                ```

                # Final Heading

                A final paragraph with an image and some text that should not be formatted: 5 * 3 = 15.
            """
            ).strip()

        def test_node(
            self,
            converted_content: str,
            parsed_nodes: list[LlamaBaseNode],
            yaml_snapshot: SnapshotAssertion,
        ) -> None:
            root: LlamaBaseNode = parsed_nodes[0]
            assert root.get_content() == converted_content

            assert root.metadata == {}
            assert root.next_node is None
            assert root.prev_node is None
            assert root.child_nodes is not None
            assert len(root.child_nodes) == 2

            root_1: LlamaBaseNode = parsed_nodes[1]

            assert (
                root_1.get_content()
                == dedent(
                    text="""
                # Main Heading

                Content under the first H1, with italic text.

                ## Section with a Table

                | Column A   | Column B   |
                |------------|------------|
                | Data 1A    | Data 1B    |
                | Data 2A    | Data 2B    |

                ## Another Section with Lists

                Here are some lists.

                - First item
                - Second item

                1. Step 1
                2. Step 2

                This is a blockquote.

                ### Subsection with Code

                An example of inline code is document.getElementById().

                ```
                function hello() {
                    console.log("Hello, world!");
                }
                ```
                """
                ).strip()
            )

            assert root_1.metadata == {
                "docling_label": "title",
                "docling_ref": "#/texts/1",
                "headings": ["# Main Heading"],
            }

            assert root_1.parent_node == root.as_related_node_info()

            root_2: LlamaBaseNode = parsed_nodes[17]

            assert (
                root_2.get_content()
                == dedent(
                    text="""
            # Final Heading

            A final paragraph with an image and some text that should not be formatted: 5 * 3 = 15.
            """
                ).strip()
            )

            assert root_2.metadata == {
                "docling_label": "title",
                "docling_ref": "#/texts/14",
                "headings": ["# Final Heading"],
            }

            assert organize_nodes_for_snapshot(nodes=parsed_nodes, extra_nodes=parsed_nodes) == yaml_snapshot

        class TestCollapsed:
            @pytest.fixture
            def docling_hierarchical_node_parser(self) -> DoclingHierarchicalNodeParser:
                return DoclingHierarchicalNodeParser(
                    collapse_nodes=True,
                    collapse_max_size=1024,
                    collapse_min_size=256,
                )

            def test_collapsed(
                self,
                converted_content: str,
                parsed_nodes: list[LlamaBaseNode],
                yaml_snapshot: SnapshotAssertion,
            ) -> None:
                root: LlamaBaseNode = parsed_nodes[0]

                assert root.get_content() == converted_content
                assert root.metadata == {}

                assert organize_nodes_for_snapshot(nodes=parsed_nodes) == yaml_snapshot


samples = get_docling_samples(sample_type="html")

test_case_ids: list[str] = [sample.name for sample in samples]


class TestSamples:
    @pytest.fixture
    def docling_hierarchical_node_parser(self) -> DoclingHierarchicalNodeParser:
        return DoclingHierarchicalNodeParser()

    @pytest.fixture
    def leaf_semantic_merger_node_parser(self) -> LeafSemanticMergerNodeParser:
        assert embedding_model is not None

        return LeafSemanticMergerNodeParser(
            embed_model=embedding_model,
        )

    @pytest.mark.parametrize(argnames=("sample"), argvalues=samples, ids=test_case_ids)
    def test_sample(
        self,
        sample: DoclingSample,
        yaml_snapshot: SnapshotAssertion,
        markdown_snapshot: SnapshotAssertion,
        leaf_semantic_merger_node_parser: LeafSemanticMergerNodeParser,
    ):
        # Generate nodes without collapsing
        node_parser: DoclingHierarchicalNodeParser = DoclingHierarchicalNodeParser()

        parsed_nodes: list[LlamaBaseNode] = node_parser.get_nodes_from_documents(documents=[sample.input_as_document()])
        validate_relationships(nodes=parsed_nodes)

        assert serialize_nodes_for_snapshot(nodes=parsed_nodes) == yaml_snapshot
        assert parsed_nodes[0].get_content() == markdown_snapshot

        parsed_root_node: LlamaBaseNode = parsed_nodes[0]
        assert isinstance(parsed_root_node, LlamaBaseNode)

        # Generate nodes with collapsing
        collapsing_node_parser: DoclingHierarchicalNodeParser = DoclingHierarchicalNodeParser(collapse_nodes=True)
        collapsed_nodes: list[LlamaBaseNode] = collapsing_node_parser.get_nodes_from_documents(documents=[sample.input_as_document()])
        validate_relationships(nodes=collapsed_nodes)

        assert serialize_nodes_for_snapshot(nodes=collapsed_nodes) == yaml_snapshot(name="collapsed")

        collapsed_root_node: LlamaBaseNode = collapsed_nodes[0]
        assert isinstance(collapsed_root_node, LlamaBaseNode)

        # Generate collapsed nodes with custom HTML Backend
        format_options: dict[InputFormat, FormatOption] = {
            InputFormat.HTML: FormatOption(
                pipeline_cls=SimplePipeline,
                backend=TrimmedHTMLDocumentBackend,
            ),
        }
        assert collapsed_root_node.get_content() == parsed_root_node.get_content()

        # Use the custom HTML backend to generate nodes
        trimmed_node_parser: DoclingHierarchicalNodeParser = DoclingHierarchicalNodeParser(
            format_options=format_options, collapse_nodes=True
        )

        trimmed_nodes: list[LlamaBaseNode] = trimmed_node_parser.get_nodes_from_documents(documents=[sample.input_as_document()])
        validate_relationships(nodes=trimmed_nodes)

        assert serialize_nodes_for_snapshot(nodes=trimmed_nodes) == yaml_snapshot(name="custom_backend")

        assert trimmed_nodes[0].get_content() == markdown_snapshot(name="custom_backend")

        leaf_nodes = [leaf_node for leaf_node in trimmed_nodes if leaf_node.child_nodes is None]

        assert embedding_model is not None
        _ = embedding_model(nodes=leaf_nodes)

        merged_nodes: list[LlamaBaseNode] = leaf_semantic_merger_node_parser._parse_nodes(nodes=trimmed_nodes)
        merged_nodes = leaf_semantic_merger_node_parser._postprocess_parsed_nodes(nodes=merged_nodes, parent_doc_map={})

        validate_relationships(nodes=merged_nodes)

        assert serialize_nodes_for_snapshot(nodes=merged_nodes) == yaml_snapshot(name="merged")


# class TestSimpleMarkdown:
#     def test_one_heading(self, docling_hierarchical_node_parser: DoclingHierarchicalNodeParser, yaml_snapshot: SnapshotAssertion):
#         """A markdown document loaded into a Llama document object."""
#         markdown_text: str = dedent(
#             text="""
#             # A document with a heading

#             Also with a small amount of text
#             """
#         ).strip()
#         text_resource: MediaResource = MediaResource(text=markdown_text, mimetype="text/markdown")
#         document: LlamaDocument = LlamaDocument(text_resource=text_resource)
#         result: list[LlamaBaseNode] = docling_hierarchical_node_parser.get_nodes_from_documents(documents=[document])
#         assert len(result) == 1

#         first_node: LlamaBaseNode = result[0]
#         assert first_node.get_content() == markdown_text

#         assert serialize_nodes_for_snapshot(nodes=result) == snapshot

#     def test_two_headings(self, docling_hierarchical_node_parser: DoclingHierarchicalNodeParser):
#         """A markdown document loaded into a Llama document object."""
#         markdown_text: str = dedent(
#             text="""
#             # A document with a heading

#             Some text under the first heading

#             ## A subheading

#             Some text under the subheading
#             """
#         ).strip()
#         text_resource: MediaResource = MediaResource(text=markdown_text, mimetype="text/markdown")
#         document: LlamaDocument = LlamaDocument(text_resource=text_resource)
#         result: list[LlamaBaseNode] = docling_hierarchical_node_parser.get_nodes_from_documents(documents=[document])
#         assert len(result) == 2


# @pytest.fixture
# def llama_markdown_document() -> LlamaDocument:
#     """A markdown document loaded into a Llama document object."""
#     return get_sample_simple_markdown_document()


# def test_markdown_document(
#     docling_hierarchical_node_parser: DoclingHierarchicalNodeParser, llama_markdown_document: LlamaDocument
# ) -> LlamaDocument:
#     """Llama document object with docling's json dump as its text."""
#     result: list[LlamaBaseNode] = docling_hierarchical_node_parser.get_nodes_from_documents(documents=[llama_markdown_document])
#     assert len(result) == 16
#     assert isinstance(result[0], LlamaDocument)
#     return result[0]
