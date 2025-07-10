"""Chunker implementation leveraging the document structure."""

from __future__ import annotations

import asyncio
from collections.abc import Iterable, Sequence
from io import BytesIO
from typing import TYPE_CHECKING, Any, Protocol, override, runtime_checkable
from uuid import uuid4

from docling.datamodel.base_models import ConversionStatus, InputFormat
from docling.document_converter import DocumentConverter, FormatOption
from docling_core.transforms.serializer.base import BaseDocSerializer, BaseSerializerProvider, SerializationResult
from docling_core.transforms.serializer.markdown import MarkdownDocSerializer, MarkdownParams
from docling_core.types.doc.base import ImageRefMode
from docling_core.types.doc.document import ContentLayer as DoclingContentLayer
from docling_core.types.doc.document import DocItem as DoclingDocItem
from docling_core.types.doc.document import GroupItem as DoclingGroupItem
from docling_core.types.doc.document import NodeItem as DoclingNodeItem
from docling_core.types.doc.document import SectionHeaderItem, TitleItem
from docling_core.types.io import DocumentStream
from llama_index.core.schema import BaseNode as LlamaBaseNode
from llama_index.core.schema import Document as LlamaDocument
from llama_index.core.schema import MediaResource
from llama_index.core.schema import Node as LlamaNode
from llama_index.core.schema import NodeRelationship as LlamaNodeRelationship
from llama_index.core.utils import get_tqdm_iterable  # pyright: ignore[reportUnknownVariableType]
from pydantic import Field, PrivateAttr

from knowledge_base_mcp.llama_index.hierarchical_node_parsers.hierarchical_node_parser import (
    HierarchicalNodeParser,
)
from knowledge_base_mcp.utils.logging import BASE_LOGGER

logger = BASE_LOGGER.getChild(__name__)

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence

    from docling.datamodel.document import ConversionResult
    from docling_core.types.doc.document import DoclingDocument


DEFAULT_MARKDOWN_PARAMS: MarkdownParams = MarkdownParams(
    image_mode=ImageRefMode.PLACEHOLDER,
    image_placeholder="",
    escape_underscores=False,
    escape_html=False,
    include_hyperlinks=False,
)

ALWAYS_REMOVE_CHARS: set[int] = {
    0x00B6,  # pilcrow sign
}

ALWAYS_REPLACE_CHARS: dict[int, str] = {
    0x0009: " ",  # tab
    0x000B: " ",  # vertical tab
    0x000C: " ",  # form feed
    0x000D: " ",  # carriage return
    0x000A: " ",  # new line
}


def _filter_nonlanguage_str(text: str) -> str:
    """Filter out non-language strings, i.e. anything not between 0000-FFFF unicode"""

    replaced_text: str = "".join(
        ALWAYS_REPLACE_CHARS.get(ord(char), char)
        for char in text
        if ord(char) in range(0x20, 0xFFFF) and ord(char) not in ALWAYS_REMOVE_CHARS
    )

    return replaced_text.strip()


class DefaultSerializerProvider(BaseSerializerProvider):
    """Serializer provider used for chunking purposes."""

    @override
    def get_serializer(self, doc: DoclingDocument) -> BaseDocSerializer:
        """Get the associated serializer."""
        return MarkdownDocSerializer(doc=doc, params=DEFAULT_MARKDOWN_PARAMS)


def _get_str_from_metadata(
    node: LlamaBaseNode,
    key: str,
) -> str | None:
    """Get a string from the metadata dictionary."""
    if not (value := node.metadata.get(key)):
        return None
    if not isinstance(value, str):
        msg: str = f"Value is not a string: {value}"
        raise TypeError(msg)
    return value


def _get_document_stream(document: LlamaDocument) -> DocumentStream:
    """Get a document stream from a Llama document."""

    raw_body, mimetype = _get_raw_body(document)

    fake_document_name: str = "make_docling_guess"

    match mimetype:
        case "text/markdown":
            fake_document_name = "markdown.md"
        case "text/html":
            fake_document_name = "html.html"
        case _:
            if file_name := _get_str_from_metadata(node=document, key="file_name"):
                fake_document_name = file_name
            elif source_url := _get_str_from_metadata(node=document, key="url"):
                fake_document_name = source_url.split("/")[-1]

    # if fake_document_name == "llms.txt":
    #     fake_document_name = "llms.md"

    return DocumentStream(
        name=fake_document_name,
        stream=BytesIO(initial_bytes=raw_body.encode(encoding="utf-8")),
    )


def _get_raw_body(document: LlamaDocument) -> tuple[str, str | None]:
    """Returns the mime type and raw body of a document."""
    if not (media_resource := document.text_resource):
        msg = "Document has no text resource"
        raise TypeError(msg)

    if not (raw_body := media_resource.text):
        msg = "Document has no raw body"
        raise TypeError(msg)

    return raw_body, media_resource.mimetype


def _document_iterable(
    documents: Sequence[LlamaBaseNode], show_progress: bool = False, desc: str = "Parsing out docling nodes"
) -> Iterable[LlamaDocument]:
    """An iterable that yields LlamaDocuments."""
    iterable: Iterable[Any] = get_tqdm_iterable(  # pyright: ignore[reportUnknownVariableType]
        items=documents,
        show_progress=show_progress,
        desc=desc,
    )

    for item in iterable:  # pyright: ignore[reportAny]
        if not isinstance(item, LlamaDocument):
            msg = "Node must be an instance of Document"
            raise TypeError(msg)

        yield item


def trim_headings(headings: list[str]) -> list[str]:
    """Trim all empty headings from anywhere in the list."""
    return [heading for heading in headings if heading.strip()]


def set_heading(headings: list[str], level: int, heading: str) -> list[str]:
    """Pad the headings to the given level. If we get level 5, then there should be 5 entries, even if some are empty.

    If we get a level 3, and we already have 5 entries, then we trim to 2 entries and add the new heading to the end."""

    if len(headings) > level:
        headings = headings[:level]

    for _ in range(len(headings), level + 1):
        headings.append("")

    headings[level] = "#" * level + " " + _filter_nonlanguage_str(text=heading)

    return headings


class DoclingHierarchicalNodeParser(HierarchicalNodeParser):
    """
    Docling Hierarchical Node parser.
    """

    serializer_provider: BaseSerializerProvider = Field(default_factory=DefaultSerializerProvider)

    input_formats: list[InputFormat] = Field(default_factory=lambda: list(InputFormat))
    """The allowed input formats."""

    format_options: dict[InputFormat, FormatOption] = Field(default_factory=dict)
    """The options to use for different input formats."""

    minimum_chunk_size: int = Field(default=256)
    """The minimum size of a chunk in characters. Smaller chunks may be produced but we will try to avoid them."""

    mutate_document_to_markdown: bool = Field(default=False)
    """Whether to mutate the body of the provided documents to markdown in addition to parsing out nodes."""

    _document_converter: DocumentConverter = PrivateAttr()

    @runtime_checkable
    class NodeIDGenCallable(Protocol):
        def __call__(self, i: int, node: LlamaBaseNode) -> str: ...

    @staticmethod
    def _uuid4_node_id_gen(i: int, node: LlamaBaseNode) -> str:  # pyright: ignore[reportUnusedParameter]  # noqa: ARG004
        return str(uuid4())

    id_func: NodeIDGenCallable = _uuid4_node_id_gen  # pyright: ignore[reportIncompatibleVariableOverride]

    @override
    def model_post_init(self, __context: Any) -> None:  # pyright: ignore[reportAny]
        self._document_converter = DocumentConverter(allowed_formats=self.input_formats, format_options=self.format_options)

    @override
    async def _aparse_nodes(
        self,
        nodes: Sequence[LlamaBaseNode],
        show_progress: bool = False,
        **kwargs: Any,  # pyright: ignore[reportAny]
    ) -> list[LlamaBaseNode]:
        return await asyncio.to_thread(self._parse_nodes, nodes=nodes, show_progress=show_progress, **kwargs)

    def _convert_document_stream_to_docling_document(self, document_stream: DocumentStream) -> DoclingDocument:
        """Converts a document stream to a docling document."""

        conversion_result: ConversionResult = self._document_converter.convert(source=document_stream)
        if conversion_result.status != ConversionStatus.SUCCESS:
            msg = f"Conversion failed for document: {document_stream}"
            raise ValueError(msg)

        return conversion_result.document

    @override
    def _parse_nodes(
        self,
        nodes: Sequence[LlamaBaseNode],
        show_progress: bool = False,
        **kwargs: Any,  # pyright: ignore[reportAny]
    ) -> list[LlamaBaseNode]:
        all_nodes: list[LlamaBaseNode] = []

        for document in _document_iterable(documents=nodes, show_progress=show_progress):
            document_stream: DocumentStream = _get_document_stream(document=document)

            try:
                docling_document: DoclingDocument = self._convert_document_stream_to_docling_document(document_stream=document_stream)
            except Exception:
                logger.exception(f"Error converting document stream to docling document {document.metadata}")
                continue

            all_nodes.extend(self._convert_llama_document(llama_document=document, docling_document=docling_document))

        return all_nodes

    def _mutate_document_to_markdown(self, llama_document: LlamaDocument, docling_document: DoclingDocument) -> None:
        llama_document.text_resource = MediaResource(text=docling_document.export_to_markdown(), mimetype="text/markdown")

    def _convert_llama_document(self, llama_document: LlamaDocument, docling_document: DoclingDocument) -> Sequence[LlamaBaseNode]:
        """Converts a Hierarchical DoclingDocument to a Hierarchical LlamaDocument."""

        serializer = self.serializer_provider.get_serializer(doc=docling_document)

        markdown_text: str = serializer.serialize(item=docling_document.body).text

        if self.mutate_document_to_markdown:
            llama_document.text_resource = MediaResource(text=markdown_text, mimetype="text/markdown")

        root_nodes, all_nodes = self._process_docling_node_children(
            llama_document=llama_document,
            docling_document=docling_document,
            docling_doc_item=docling_document.body,
            headings=[],
            doc_serializer=serializer,
            visited=set(),
        )

        self._establish_sibling_relationships(sibling_nodes=root_nodes)

        return all_nodes

    def _process_docling_node_children(
        self,
        llama_document: LlamaDocument,
        docling_document: DoclingDocument,
        docling_doc_item: DoclingDocItem | DoclingGroupItem,
        headings: list[str],
        doc_serializer: BaseDocSerializer,
        visited: set[str],
    ) -> tuple[list[LlamaNode], list[LlamaNode]]:
        """Converts a DoclingGroup to a Parent node and converts the docling node's children to child nodes recursively."

        Returns:
            A tuple containing first the direct member nodes and then all nodes (including the member nodes).
        """

        member_nodes: list[LlamaNode] = []
        all_nodes: list[LlamaNode] = []

        # original_headings: list[str] = headings.copy()

        for item in docling_doc_item.children:
            if item.cref in visited:
                continue

            # The items we're iterating through are really references, get the actual item
            resolved_item: Any = item.resolve(doc=docling_document)  # pyright: ignore[reportAny]

            # In Docling-lang, furniture is the stuff you don't want
            if isinstance(resolved_item, DoclingNodeItem) and resolved_item.content_layer == DoclingContentLayer.FURNITURE:
                continue

            # If this is a section, we'll make nodes recursively
            if isinstance(resolved_item, TitleItem | SectionHeaderItem):
                level: int = 1 if isinstance(resolved_item, TitleItem) else resolved_item.level + 1
                headings = set_heading(headings=headings, level=level, heading=resolved_item.text)

                parent_node, child_nodes = self._docling_node_item_to_llama_group_node(
                    llama_document=llama_document,
                    docling_document=docling_document,
                    docling_doc_item=resolved_item,
                    headings=headings,
                    doc_serializer=doc_serializer,
                    visited=visited,
                )

                if parent_node:
                    member_nodes.append(parent_node)
                    all_nodes.append(parent_node)

                if child_nodes:
                    all_nodes.extend(child_nodes)

            # Otherwise we'll just make a single node for the item
            elif isinstance(resolved_item, DoclingGroupItem | DoclingDocItem):
                member_node: LlamaNode | None = self._docling_node_item_to_llama_item(
                    llama_document=llama_document,
                    docling_doc_item=resolved_item,
                    headings=headings,
                    doc_serializer=doc_serializer,
                    visited=visited,
                )
                if member_node:
                    member_nodes.append(member_node)
                    all_nodes.append(member_node)

            else:
                msg: str = f"Item is not a DoclingGroupItem or DoclingDocItem: {resolved_item}"
                raise TypeError(msg)

        # headings = original_headings

        return member_nodes, all_nodes

    def _docling_node_item_to_llama_group_node(
        self,
        llama_document: LlamaDocument,
        docling_document: DoclingDocument,
        docling_doc_item: DoclingDocItem | DoclingGroupItem,
        headings: list[str],
        doc_serializer: BaseDocSerializer,
        visited: set[str],
    ) -> tuple[LlamaNode | None, Sequence[LlamaNode]]:
        """Converts a Docling item to a Parent node and converts the docling node's children to child nodes."""

        # We're serializing for a group node so we do not pass visited as it needs to contain a copy
        text: str = self.serialize_docling_item(
            doc_serializer=doc_serializer, docling_doc_item=docling_doc_item, visited=set(), recursive=True
        )

        if not text or not text.strip():
            return None, []

        # Don't bother building nodes recursively if the whole section is smaller than the minimum size
        # or if there are zero/one children (i.e. no need to build a dedicated heading node or a parent/child stack)
        if len(text) < self.minimum_chunk_size or len(docling_doc_item.children) <= 1:
            return self._docling_node_item_to_llama_item(
                llama_document=llama_document,
                docling_doc_item=docling_doc_item,
                headings=headings,
                doc_serializer=doc_serializer,
                visited=visited,
            ), []

        # We'll make the heading into its own node
        heading_node: LlamaBaseNode | None = LlamaNode(
            text_resource=MediaResource(text=headings[-1], mimetype="text/markdown"),
            relationships={LlamaNodeRelationship.SOURCE: llama_document.as_related_node_info()},
            extra_info={
                "docling_ref": docling_doc_item.self_ref,
                "docling_label": str(docling_doc_item.label),
                "headings": trim_headings(headings=headings),
                **llama_document.metadata,
            },
        )

        member_nodes, all_nodes = self._process_docling_node_children(
            llama_document=llama_document,
            docling_document=docling_document,
            docling_doc_item=docling_doc_item,
            headings=headings,
            doc_serializer=doc_serializer,
            visited=visited,
        )

        parent_node: LlamaNode = LlamaNode(
            text_resource=MediaResource(text=text, mimetype="text/markdown"),
            relationships={LlamaNodeRelationship.SOURCE: llama_document.as_related_node_info()},
            extra_info={
                "docling_ref": docling_doc_item.self_ref,
                "docling_label": str(docling_doc_item.label),
                "headings": heading_node.metadata["headings"],
                **llama_document.metadata,
            },
        )

        self._establish_parent_child_relationships(parent=parent_node, child_nodes=[heading_node, *member_nodes])

        return parent_node, [heading_node, *all_nodes]

    def _docling_node_item_to_llama_item(
        self,
        llama_document: LlamaDocument,
        docling_doc_item: DoclingDocItem | DoclingGroupItem,
        headings: list[str],
        doc_serializer: BaseDocSerializer,
        visited: set[str],
    ) -> LlamaNode | None:
        """Convert a DoclingItem and all of its children to a LlamaItem."""

        text: str = self.serialize_docling_item(
            doc_serializer=doc_serializer, docling_doc_item=docling_doc_item, visited=visited, recursive=True
        )

        if not text or not text.strip():
            return None

        return LlamaNode(
            text_resource=MediaResource(text=text, mimetype="text/markdown"),
            relationships={LlamaNodeRelationship.SOURCE: llama_document.as_related_node_info()},
            extra_info={
                "docling_ref": docling_doc_item.self_ref,
                "docling_label": str(docling_doc_item.label),
                "headings": trim_headings(headings=headings),
                **llama_document.metadata,
            },
        )

    def serialize_docling_item(
        self,
        doc_serializer: BaseDocSerializer,
        docling_doc_item: DoclingDocItem | DoclingGroupItem,
        visited: set[str],
        recursive: bool = False,
    ) -> str:
        """Serialize a DoclingItem to a string."""

        text: str

        if recursive:
            results: list[SerializationResult] = doc_serializer.get_parts(item=docling_doc_item, visited=visited)

            text = "\n\n".join([part.text for part in results if part.text])

        else:
            result: SerializationResult = doc_serializer.serialize(item=docling_doc_item, visited=visited)
            text = result.text

        return text
