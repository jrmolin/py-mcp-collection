import asyncio
import json
from collections.abc import Iterable, Sequence
from io import BytesIO
from typing import Any

from docling.datamodel.base_models import InputFormat, OutputFormat
from docling.document_converter import DocumentConverter, FormatOption
from docling_core.types.io import DocumentStream
from llama_index.core.node_parser import NodeParser
from llama_index.core.schema import BaseNode, Document, MediaResource, MetadataMode
from llama_index.core.utils import get_tqdm_iterable
from pydantic import ConfigDict, Field, PrivateAttr

from knowledge_base_mcp.utils.logging import BASE_LOGGER

logger = BASE_LOGGER.getChild(__name__)


class DocumentToDoclingDocumentNodeParser(NodeParser):
    """
    Document to Docling document node parser.
    """

    model_config = ConfigDict(use_attribute_docstrings=True, arbitrary_types_allowed=True)

    input_formats: list[InputFormat] = Field(default_factory=lambda: list(InputFormat))
    """The allowed input formats."""

    format_options: dict[InputFormat, FormatOption] = Field(default_factory=dict)
    """The options to use for different input formats."""

    output_format: OutputFormat = Field(default=OutputFormat.JSON)
    """The format to export the Docling document to. This is what will be in the produced Text Nodes."""

    _document_converter: DocumentConverter = PrivateAttr()

    def model_post_init(self, __context: Any) -> None:
        self._document_converter = DocumentConverter(allowed_formats=self.input_formats, format_options=self.format_options)

    async def _aparse_nodes(
        self,
        nodes: Sequence[BaseNode],
        show_progress: bool = False,
        **kwargs: Any,
    ) -> list[BaseNode]:
        return await asyncio.to_thread(self._parse_nodes, nodes, show_progress=show_progress, **kwargs)

    def _parse_nodes(
        self,
        nodes: Sequence[BaseNode],
        show_progress: bool = False,
        **kwargs: Any,  # noqa: ARG002
    ) -> list[BaseNode]:
        nodes_with_progress: Iterable[BaseNode] = get_tqdm_iterable(items=nodes, show_progress=show_progress, desc="Parsing nodes")

        new_nodes = []

        for original_node in nodes_with_progress:
            node_content = original_node.get_content(metadata_mode=MetadataMode.NONE)

            name: str = "unknown"

            if url := original_node.metadata.get("url"):
                name = url
            elif file_name := original_node.metadata.get("file_name"):
                name = file_name

            document_stream = DocumentStream(
                name=name,
                stream=BytesIO(node_content.encode("utf-8")),
            )

            try:
                converted_result = self._document_converter.convert(document_stream)
            except Exception:
                logger.exception(f"An error occured converting the document: {original_node.metadata}")
                continue

            text: str
            mimetype: str | None = None

            match self.output_format:
                case OutputFormat.JSON:
                    text = json.dumps(converted_result.document.export_to_dict())
                    mimetype = "application/json"
                case OutputFormat.MARKDOWN:
                    text = converted_result.document.export_to_markdown()
                    mimetype = "text/markdown"
                case OutputFormat.HTML:
                    text = converted_result.document.export_to_html()
                    mimetype = "text/html"
                case OutputFormat.HTML_SPLIT_PAGE:
                    text = converted_result.document.export_to_html(split_page_view=True)
                    mimetype = "text/html"
                case OutputFormat.TEXT:
                    text = converted_result.document.export_to_text()
                    mimetype = "text/plain"
                case OutputFormat.DOCTAGS:
                    text = converted_result.document.export_to_doctags()
                case _:
                    msg = f"Unsupported output format: {self.output_format}"
                    raise NotImplementedError(msg)

            # relationships: dict[NodeRelationship, RelatedNodeType] = {}

            if isinstance(original_node, Document):
                original_node.text_resource = MediaResource(text=text, mimetype=mimetype)
                # relationships[NodeRelationship.SOURCE] = original_node.as_related_node_info()

            # new_node = Node(
            #     relationships=relationships,
            #     text_resource=MediaResource(text=text, mimetype=mimetype),
            # )
            new_nodes.append(original_node)

        return new_nodes
