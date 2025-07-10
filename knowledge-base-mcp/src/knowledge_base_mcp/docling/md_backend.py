"""
Base parser
"""

import logging
import re
from copy import deepcopy
from io import BytesIO
from pathlib import Path
from typing import Optional, override

import marko
import marko.element
import marko.inline
from docling.backend.html_backend import HTMLDocumentBackend
from docling.backend.md_backend import (
    MarkdownDocumentBackend,
    _CreationPayload,
    _HeadingCreationPayload,
    _ListItemCreationPayload,
)
from docling.datamodel.base_models import InputFormat
from docling.datamodel.document import InputDocument
from docling_core.types.doc import (
    DocItemLabel,
    DoclingDocument,
    DocumentOrigin,
    NodeItem,
    TextItem,
)
from docling_core.types.doc.document import Formatting
from marko import Markdown
from pydantic import AnyUrl, TypeAdapter

from knowledge_base_mcp.docling.marko_grouping_parser import GroupingParser

_MARKER_BODY = "DOCLING_DOC_MD_HTML_EXPORT"
_START_MARKER = f"#_#_{_MARKER_BODY}_START_#_#"
_STOP_MARKER = f"#_#_{_MARKER_BODY}_STOP_#_#"

_log = logging.getLogger(__name__)


class GroupingMarkdownDocumentBackend(MarkdownDocumentBackend):
    @override
    def convert(self) -> DoclingDocument:
        _log.debug("converting Markdown...")

        origin = DocumentOrigin(
            filename=self.file.name or "file",
            mimetype="text/markdown",
            binary_hash=self.document_hash,  # pyright: ignore[reportArgumentType]
        )

        doc = DoclingDocument(name=self.file.stem or "file", origin=origin)

        if self.is_valid():
            # Parse the markdown into an abstract syntax tree (AST)
            marko_parser = Markdown(parser=GroupingParser)
            parsed_ast = marko_parser.parse(self.markdown)
            # Start iterating from the root of the AST
            self._iterate_elements(
                element=parsed_ast,
                depth=0,
                doc=doc,
                parent_item=None,
                visited=set(),
                creation_stack=[],
                list_ordered_flag_by_ref={},
            )
            self._close_table(doc=doc)  # handle any last hanging table

            # if HTML blocks were detected, export to HTML and delegate to HTML backend
            if self._html_blocks > 0:
                # export to HTML
                html_backend_cls = HTMLDocumentBackend
                html_str = doc.export_to_html()

                def _restore_original_html(txt, regex):
                    _txt, count = re.subn(regex, "", txt)
                    if count != self._html_blocks:
                        msg = "An internal error has occurred during Markdown conversion."
                        raise RuntimeError(msg)
                    return _txt

                # restore original HTML by removing previously added markers
                for regex in [
                    rf"<pre>\s*<code>\s*{_START_MARKER}",
                    rf"{_STOP_MARKER}\s*</code>\s*</pre>",
                ]:
                    html_str = _restore_original_html(txt=html_str, regex=regex)
                self._html_blocks: int = 0

                # delegate to HTML backend
                stream = BytesIO(bytes(html_str, encoding="utf-8"))
                in_doc = InputDocument(
                    path_or_stream=stream,
                    format=InputFormat.HTML,
                    backend=html_backend_cls,
                    filename=self.file.name,
                )
                html_backend_obj = html_backend_cls(in_doc=in_doc, path_or_stream=stream)
                doc = html_backend_obj.convert()
        else:
            msg = f"Cannot convert md with {self.document_hash} because the backend failed to init."
            raise RuntimeError(msg)
        return doc

    @override
    def _iterate_elements(
        self,
        *,
        element: marko.element.Element,
        depth: int,
        doc: DoclingDocument,
        visited: set[marko.element.Element],
        creation_stack: list[_CreationPayload],  # stack for lazy item creation triggered deep in marko's AST (on RawText)
        list_ordered_flag_by_ref: dict[str, bool],
        parent_item: NodeItem | None = None,
        formatting: Formatting | None = None,
        hyperlink: AnyUrl | Path | None = None,
    ):
        if element in visited:
            return

        # Iterates over all elements in the AST
        # Check for different element types and process relevant details
        if isinstance(element, marko.block.Heading) and len(element.children) > 0:
            self._close_table(doc)
            _log.debug(
                f" - Heading level {element.level}, content: {element.children[0].children}"  # type: ignore
            )

            # if len(element.children) > 1:  # inline group will be created further down
            parent_item = self._create_heading_item(
                doc=doc,
                parent_item=parent_item,
                text="",
                level=element.level,
                formatting=formatting,
                hyperlink=hyperlink,
            )

            creation_stack.append(_HeadingCreationPayload(level=element.level))

        elif isinstance(element, marko.block.List):
            has_non_empty_list_items = False
            for child in element.children:
                if isinstance(child, marko.block.ListItem) and len(child.children) > 0:
                    has_non_empty_list_items = True
                    break

            self._close_table(doc)
            _log.debug(f" - List {'ordered' if element.ordered else 'unordered'}")
            if has_non_empty_list_items:
                parent_item = doc.add_list_group(name="list", parent=parent_item)
                list_ordered_flag_by_ref[parent_item.self_ref] = element.ordered

        elif (
            isinstance(element, marko.block.ListItem)
            and len(element.children) == 1
            and isinstance((child := element.children[0]), marko.block.Paragraph)
            and len(child.children) > 0
        ):
            self._close_table(doc)
            _log.debug(" - List item")

            enumerated = list_ordered_flag_by_ref.get(parent_item.self_ref, False) if parent_item else False
            if len(child.children) > 1:  # inline group will be created further down
                parent_item = self._create_list_item(
                    doc=doc,
                    parent_item=parent_item,
                    text="",
                    enumerated=enumerated,
                    formatting=formatting,
                    hyperlink=hyperlink,
                )
            else:
                creation_stack.append(_ListItemCreationPayload(enumerated=enumerated))

        elif isinstance(element, marko.inline.Image):
            self._close_table(doc)
            _log.debug(f" - Image with alt: {element.title}, url: {element.dest}")

            fig_caption: TextItem | None = None
            if element.title is not None and element.title != "":
                fig_caption = doc.add_text(
                    label=DocItemLabel.CAPTION,
                    text=element.title,
                    formatting=formatting,
                    hyperlink=hyperlink,
                )

            doc.add_picture(parent=parent_item, caption=fig_caption)

        elif isinstance(element, marko.inline.Emphasis):
            _log.debug(f" - Emphasis: {element.children}")
            formatting = deepcopy(formatting) if formatting else Formatting()
            formatting.italic = True

        elif isinstance(element, marko.inline.StrongEmphasis):
            _log.debug(f" - StrongEmphasis: {element.children}")
            formatting = deepcopy(formatting) if formatting else Formatting()
            formatting.bold = True

        elif isinstance(element, marko.inline.Link):
            _log.debug(f" - Link: {element.children}")
            hyperlink = TypeAdapter(Optional[AnyUrl | Path]).validate_python(element.dest)

        elif isinstance(element, marko.inline.RawText):
            _log.debug(f" - Paragraph (raw text): {element.children}")
            snippet_text = element.children.strip()
            # Detect start of the table:
            if "|" in snippet_text or self.in_table:
                # most likely part of the markdown table
                self.in_table = True
                if len(self.md_table_buffer) > 0:
                    self.md_table_buffer[len(self.md_table_buffer) - 1] += snippet_text
                else:
                    self.md_table_buffer.append(snippet_text)
            elif snippet_text:
                self._close_table(doc)

                if creation_stack:
                    while len(creation_stack) > 0:
                        to_create = creation_stack.pop()
                        if isinstance(to_create, _ListItemCreationPayload):
                            enumerated = list_ordered_flag_by_ref.get(parent_item.self_ref, False) if parent_item else False
                            parent_item = self._create_list_item(
                                doc=doc,
                                parent_item=parent_item,
                                text=snippet_text,
                                enumerated=enumerated,
                                formatting=formatting,
                                hyperlink=hyperlink,
                            )
                        elif isinstance(to_create, _HeadingCreationPayload):
                            # not keeping as parent_item as logic for correctly tracking
                            # that not implemented yet (section components not captured
                            # as heading children in marko)
                            # Set the text of the parent item (the heading)
                            parent_item.text = snippet_text
                            # parent_item = self._create_heading_item(
                            #     doc=doc,
                            #     parent_item=parent_item,
                            #     text=snippet_text,
                            #     level=to_create.level,
                            #     formatting=formatting,
                            #     hyperlink=hyperlink,
                            # )
                else:
                    doc.add_text(
                        label=DocItemLabel.TEXT,
                        parent=parent_item,
                        text=snippet_text,
                        formatting=formatting,
                        hyperlink=hyperlink,
                    )

        elif isinstance(element, marko.inline.CodeSpan):
            self._close_table(doc)
            _log.debug(f" - Code Span: {element.children}")
            snippet_text = str(element.children).strip()
            doc.add_code(
                parent=parent_item,
                text=snippet_text,
                formatting=formatting,
                hyperlink=hyperlink,
            )

        elif (
            isinstance(element, (marko.block.CodeBlock, marko.block.FencedCode))
            and len(element.children) > 0
            and isinstance((child := element.children[0]), marko.inline.RawText)
            and len(snippet_text := (child.children.strip())) > 0
        ):
            self._close_table(doc)
            _log.debug(f" - Code Block: {element.children}")
            doc.add_code(
                parent=parent_item,
                text=snippet_text,
                formatting=formatting,
                hyperlink=hyperlink,
            )

        elif isinstance(element, marko.inline.LineBreak):
            if self.in_table:
                _log.debug("Line break in a table")
                self.md_table_buffer.append("")

        elif isinstance(element, marko.block.HTMLBlock):
            self._html_blocks += 1
            self._close_table(doc)
            _log.debug(f"HTML Block: {element}")
            if len(element.body) > 0:  # If Marko doesn't return any content for HTML block, skip it
                html_block = element.body.strip()

                # wrap in markers to enable post-processing in convert()
                text_to_add = f"{_START_MARKER}{html_block}{_STOP_MARKER}"
                doc.add_code(
                    parent=parent_item,
                    text=text_to_add,
                    formatting=formatting,
                    hyperlink=hyperlink,
                )
        elif not isinstance(element, str):
            self._close_table(doc)
            _log.debug(f"Some other element: {element}")

        if isinstance(element, (marko.block.Paragraph)) and len(element.children) > 1:
            parent_item = doc.add_inline_group(parent=parent_item)

        processed_block_types = (
            marko.block.CodeBlock,
            marko.block.FencedCode,
            marko.inline.RawText,
        )

        # Iterate through the element's children (if any)
        if hasattr(element, "children") and not isinstance(element, processed_block_types):
            for child in element.children:
                self._iterate_elements(
                    element=child,
                    depth=depth + 1,
                    doc=doc,
                    visited=visited,
                    creation_stack=creation_stack,
                    list_ordered_flag_by_ref=list_ordered_flag_by_ref,
                    parent_item=parent_item,
                    formatting=formatting,
                    hyperlink=hyperlink,
                )
