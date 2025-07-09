from textwrap import dedent

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
from knowledge_base_mcp.docling.md_backend import GroupingMarkdownDocumentBackend
from knowledge_base_mcp.llama_index.hierarchical_node_parsers.docling_hierarchical_node_parser import DoclingHierarchicalNodeParser
from knowledge_base_mcp.llama_index.hierarchical_node_parsers.leaf_semantic_merging import LeafSemanticMergerNodeParser
from tests.conftest import (
    DoclingSample,
    get_docling_samples,
    organize_nodes_for_snapshot,
    serialize_node_structure_for_snapshot,
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


def test_init():
    assert DoclingHierarchicalNodeParser()


def common_assertions(parsed_nodes: list[LlamaBaseNode], source_document: LlamaDocument) -> None:
    assert len(parsed_nodes) > 1
    for node in parsed_nodes:
        assert node.source_node is not None, f"Node {node.node_id} has no source node"
        assert source_document.node_id == node.source_node.node_id, (
            f"The source of node {node.node_id} is not {source_document.node_id}, it's {node.source_node.node_id}"
        )

        is_isolated: bool = node.parent_node is None and node.child_nodes is None and node.prev_node is None and node.next_node is None
        assert not is_isolated, f"Node {node.node_id} is isolated"

    validate_relationships(nodes=parsed_nodes)


class TestUnitTests:
    class TestMarkdown:
        @pytest.fixture
        def simple_document(self) -> LlamaDocument:
            input_markdown: str = dedent(
                text="""
                # A document that is good for testing

                # A document with an h1 heading

                Some text under the first h1 heading
            """
            ).strip()

            return LlamaDocument(text_resource=MediaResource(text=input_markdown, mimetype="text/markdown"))

        def test_simple(self, simple_document: LlamaDocument, yaml_snapshot: SnapshotAssertion) -> None:
            docling_hierarchical_node_parser: DoclingHierarchicalNodeParser = DoclingHierarchicalNodeParser()
            parsed_nodes: list[LlamaBaseNode] = docling_hierarchical_node_parser.get_nodes_from_documents(documents=[simple_document])
            common_assertions(parsed_nodes=parsed_nodes, source_document=simple_document)

            assert len(parsed_nodes) == 3

            root_1: LlamaBaseNode = parsed_nodes[0]
            root_2: LlamaBaseNode = parsed_nodes[1]
            root_3: LlamaBaseNode = parsed_nodes[2]

            assert root_1.get_content() == "# A document that is good for testing"

            assert root_1.metadata == {
                "docling_label": "title",
                "docling_ref": "#/texts/0",
                "headings": ["# A document that is good for testing"],
            }

            assert root_1.parent_node is None
            assert root_1.next_node == root_2.as_related_node_info()
            assert root_2.prev_node == root_1.as_related_node_info()

            assert root_2.get_content() == "# A document with an h1 heading"

            assert root_2.metadata == {
                "docling_label": "title",
                "docling_ref": "#/texts/1",
                "headings": ["# A document with an h1 heading"],
            }
            assert root_2.next_node == root_3.as_related_node_info()
            assert root_3.prev_node == root_2.as_related_node_info()

            assert root_3.get_content() == "Some text under the first h1 heading"

            assert root_3.metadata == {
                "docling_label": "text",
                "docling_ref": "#/texts/2",
                "headings": ["# A document with an h1 heading"],
            }

            assert root_3.parent_node is None
            assert root_3.child_nodes is None
            assert root_3.prev_node == root_2.as_related_node_info()
            assert root_3.next_node is None

            assert serialize_nodes_for_snapshot(nodes=parsed_nodes) == yaml_snapshot

    class TestHTML:
        @pytest.fixture
        def simple_document(self) -> LlamaDocument:
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

        def test_simple(self, simple_document: LlamaDocument) -> None:
            docling_hierarchical_node_parser: DoclingHierarchicalNodeParser = DoclingHierarchicalNodeParser()
            parsed_nodes: list[LlamaBaseNode] = docling_hierarchical_node_parser.get_nodes_from_documents(documents=[simple_document])
            common_assertions(parsed_nodes=parsed_nodes, source_document=simple_document)

            assert len(parsed_nodes) == 2

            root_1: LlamaBaseNode = parsed_nodes[0]
            assert root_1.get_content() == "# A document that is good for testing"
            assert root_1.metadata == {
                "docling_label": "title",
                "docling_ref": "#/texts/0",
                "headings": ["# A document that is good for testing"],
            }

            assert root_1.parent_node is None

            root_2: LlamaBaseNode = parsed_nodes[1]
            assert root_2.get_content() == "# A document with an h1 heading\n\nSome text under the first h1 heading"

            assert root_2.metadata == {
                "docling_label": "title",
                "docling_ref": "#/texts/1",
                "headings": ["# A document with an h1 heading"],
            }

        def test_simple_no_chunking(self, simple_document: LlamaDocument) -> None:
            docling_hierarchical_node_parser: DoclingHierarchicalNodeParser = DoclingHierarchicalNodeParser(minimum_chunk_size=0)
            parsed_nodes: list[LlamaBaseNode] = docling_hierarchical_node_parser.get_nodes_from_documents(documents=[simple_document])
            common_assertions(parsed_nodes=parsed_nodes, source_document=simple_document)

            assert len(parsed_nodes) == 2
            root_1: LlamaBaseNode = parsed_nodes[0]

            assert root_1.get_content() == "# A document that is good for testing"

            assert root_1.metadata == {
                "docling_label": "title",
                "docling_ref": "#/texts/0",
                "headings": ["# A document that is good for testing"],
            }

            root_2: LlamaBaseNode = parsed_nodes[1]

            assert root_2.get_content() == "# A document with an h1 heading\n\nSome text under the first h1 heading"

            assert root_2.metadata == {
                "docling_label": "title",
                "docling_ref": "#/texts/1",
                "headings": ["# A document with an h1 heading"],
            }

        @pytest.fixture
        def mixed_document(self) -> LlamaDocument:
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

        def test_mixed(
            self,
            mixed_document: LlamaDocument,
            yaml_snapshot: SnapshotAssertion,
        ) -> None:
            docling_hierarchical_node_parser: DoclingHierarchicalNodeParser = DoclingHierarchicalNodeParser()
            parsed_nodes: list[LlamaBaseNode] = docling_hierarchical_node_parser.get_nodes_from_documents(documents=[mixed_document])
            common_assertions(parsed_nodes=parsed_nodes, source_document=mixed_document)

            assert len(parsed_nodes) == 12

            root_1: LlamaBaseNode = parsed_nodes[0]
            root_2: LlamaBaseNode = parsed_nodes[11]

            root_1_ideal_content: str = dedent(
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

            assert root_1.get_content() == root_1_ideal_content

            assert root_1.metadata == {
                "docling_label": "title",
                "docling_ref": "#/texts/1",
                "headings": ["# Main Heading"],
            }

            assert root_1.parent_node is None
            assert root_1.child_nodes is not None
            assert len(root_1.child_nodes) == 4

            root_2_ideal_content: str = dedent(
                text="""
                # Final Heading

                A final paragraph with an image and some text that should not be formatted: 5 * 3 = 15.
            """
            ).strip()

            assert root_2.get_content() == root_2_ideal_content

            assert root_2.metadata == {
                "docling_label": "title",
                "docling_ref": "#/texts/14",
                "headings": ["# Final Heading"],
            }

            assert root_2.prev_node == root_1.as_related_node_info()
            assert root_2.next_node is None
            assert root_2.parent_node is None
            assert root_2.child_nodes is None

            assert serialize_nodes_for_snapshot(nodes=parsed_nodes) == yaml_snapshot

        def test_mixed_no_chunking(
            self,
            mixed_document: LlamaDocument,
            yaml_snapshot: SnapshotAssertion,
        ) -> None:
            docling_hierarchical_node_parser: DoclingHierarchicalNodeParser = DoclingHierarchicalNodeParser(minimum_chunk_size=0)
            parsed_nodes: list[LlamaBaseNode] = docling_hierarchical_node_parser.get_nodes_from_documents(documents=[mixed_document])
            common_assertions(parsed_nodes=parsed_nodes, source_document=mixed_document)

            assert len(parsed_nodes) == 17

            root_1: LlamaBaseNode = parsed_nodes[0]
            root_1_ideal_content: str = dedent(
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

            assert root_1.get_content() == root_1_ideal_content

            assert root_1.metadata == {
                "docling_label": "title",
                "docling_ref": "#/texts/1",
                "headings": ["# Main Heading"],
            }

            assert root_1.parent_node is None
            assert root_1.child_nodes is not None
            assert len(root_1.child_nodes) == 4

            root_2: LlamaBaseNode = parsed_nodes[14]

            assert root_1.next_node == root_2.as_related_node_info()

            root_2_ideal_content: str = dedent(
                text="""
                # Final Heading

                A final paragraph with an image and some text that should not be formatted: 5 * 3 = 15.
            """
            ).strip()

            assert root_2.get_content() == root_2_ideal_content

            assert root_2.metadata == {
                "docling_label": "title",
                "docling_ref": "#/texts/14",
                "headings": ["# Final Heading"],
            }

            root_2_2: LlamaBaseNode = parsed_nodes[16]

            assert root_2_2.get_content() == "A final paragraph with an image and some text that should not be formatted: 5 * 3 = 15."

            assert root_2_2.metadata == {
                "docling_label": "text",
                "docling_ref": "#/texts/15",
                "headings": ["# Final Heading"],
            }

            assert organize_nodes_for_snapshot(nodes=parsed_nodes, extra_nodes=parsed_nodes) == yaml_snapshot


html_samples = get_docling_samples(sample_type="html")
markdown_samples = get_docling_samples(sample_type="markdown")

all_samples: list[DoclingSample] = html_samples + markdown_samples

test_case_ids: list[str] = [sample.name for sample in all_samples]


class TestIntegrationTests:
    @pytest.fixture
    def docling_hierarchical_node_parser(self) -> DoclingHierarchicalNodeParser:
        return DoclingHierarchicalNodeParser()

    @pytest.fixture
    def leaf_semantic_merger_node_parser(self) -> LeafSemanticMergerNodeParser:
        assert embedding_model is not None

        return LeafSemanticMergerNodeParser(
            embed_model=embedding_model,
        )

    @pytest.mark.parametrize(argnames=("sample"), argvalues=all_samples, ids=test_case_ids)
    class TestPipelineStages:
        def test_basic(
            self,
            sample: DoclingSample,
            yaml_snapshot: SnapshotAssertion,
            text_snapshot: SnapshotAssertion,
        ):
            node_parser: DoclingHierarchicalNodeParser = DoclingHierarchicalNodeParser()

            parsed_nodes: list[LlamaBaseNode] = node_parser.get_nodes_from_documents(documents=[sample.input_as_document()])
            validate_relationships(nodes=parsed_nodes)

            assert serialize_nodes_for_snapshot(nodes=parsed_nodes) == yaml_snapshot
            assert serialize_node_structure_for_snapshot(nodes=parsed_nodes) == text_snapshot(name="structure")
            assert parsed_nodes[0].get_content() == text_snapshot

        def test_custom_backend(
            self,
            sample: DoclingSample,
            yaml_snapshot: SnapshotAssertion,
            text_snapshot: SnapshotAssertion,
        ):
            # Now Generate the nodes with our custom HTML backend
            format_options: dict[InputFormat, FormatOption] = {
                InputFormat.HTML: FormatOption(
                    pipeline_cls=SimplePipeline,
                    backend=TrimmedHTMLDocumentBackend,
                ),
                InputFormat.MD: FormatOption(
                    pipeline_cls=SimplePipeline,
                    backend=GroupingMarkdownDocumentBackend,
                ),
            }

            node_parser: DoclingHierarchicalNodeParser = DoclingHierarchicalNodeParser(format_options=format_options)

            parsed_nodes: list[LlamaBaseNode] = node_parser.get_nodes_from_documents(documents=[sample.input_as_document()])
            validate_relationships(nodes=parsed_nodes)

            assert serialize_nodes_for_snapshot(nodes=parsed_nodes) == yaml_snapshot
            assert serialize_node_structure_for_snapshot(nodes=parsed_nodes) == text_snapshot(name="structure")

            assert parsed_nodes[0].get_content() == text_snapshot

        def test_leaf_semantic_merging(
            self,
            sample: DoclingSample,
            yaml_snapshot: SnapshotAssertion,
            text_snapshot: SnapshotAssertion,
            leaf_semantic_merger_node_parser: LeafSemanticMergerNodeParser,
        ):
            # Now Generate the nodes with our custom HTML backend
            format_options: dict[InputFormat, FormatOption] = {
                InputFormat.HTML: FormatOption(
                    pipeline_cls=SimplePipeline,
                    backend=TrimmedHTMLDocumentBackend,
                ),
                InputFormat.MD: FormatOption(
                    pipeline_cls=SimplePipeline,
                    backend=GroupingMarkdownDocumentBackend,
                ),
            }
            node_parser: DoclingHierarchicalNodeParser = DoclingHierarchicalNodeParser(format_options=format_options)

            parsed_nodes: list[LlamaBaseNode] = node_parser.get_nodes_from_documents(documents=[sample.input_as_document()])
            validate_relationships(nodes=parsed_nodes)

            leaf_nodes: list[LlamaBaseNode] = [leaf_node for leaf_node in parsed_nodes if leaf_node.child_nodes is None]

            assert embedding_model is not None
            _ = embedding_model(nodes=leaf_nodes)

            merged_nodes: list[LlamaBaseNode] = leaf_semantic_merger_node_parser._parse_nodes(nodes=parsed_nodes)  # pyright: ignore[reportPrivateUsage]
            merged_nodes = leaf_semantic_merger_node_parser._postprocess_parsed_nodes(nodes=merged_nodes, parent_doc_map={})  # pyright: ignore[reportPrivateUsage]

            validate_relationships(nodes=merged_nodes)

            assert serialize_nodes_for_snapshot(nodes=merged_nodes) == yaml_snapshot
            assert serialize_node_structure_for_snapshot(nodes=merged_nodes) == text_snapshot(name="structure")
            assert serialize_nodes_for_snapshot(nodes=leaf_nodes, extra_nodes=merged_nodes) == yaml_snapshot(name="chunks")

            assert merged_nodes[0].get_content() == text_snapshot


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
