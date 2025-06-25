"""Markdown node parser."""

from collections.abc import Callable, Sequence
from typing import Any

from llama_index.core.bridge.pydantic import BaseModel, Field, PrivateAttr
from llama_index.core.callbacks.base import CallbackManager
from llama_index.core.node_parser.interface import NodeParser
from llama_index.core.node_parser.node_utils import build_nodes_from_splits
from llama_index.core.schema import BaseNode, MetadataMode, TextNode
from llama_index.core.utils import get_tqdm_iterable
from mistune import create_markdown
from mistune.core import BlockState
from mistune.markdown import Markdown as MarkdownParser
from mistune.renderers.markdown import MarkdownRenderer

from knowledge_base_mcp.utils.logging import BASE_LOGGER

logger = BASE_LOGGER.getChild(__name__)
ALLOWED_ELEMENTS = {"list", "thematic_break", "table", "def_list", "block_html", "block_code", "block_quote", "block_math", "block_image"}
DEFAULT_ELEMENTS = ["table"]

DEFAULT_PLUGINS = [
    "table",
]

AstNode = dict[str, Any]


class HeaderPath(BaseModel):
    level: int
    text: str

    @property
    def text_str(self) -> str:
        """Get the text for the header path."""
        return self.text.lstrip("#").lstrip().rstrip()


class HeaderPathStack(BaseModel):
    path: list[HeaderPath] = Field(default_factory=list)
    path_separator: str = Field(default="/")

    @property
    def level(self) -> int:
        """Get the maximum level of the header path stack."""
        return max(h.level for h in self.path)

    @property
    def path_str(self) -> str:
        """Get the text of the header path stack, separated by the path separator."""
        return "/" + self.path_separator.join([part.text_str for part in self.path])

    def pop_level(self, level: int):
        """Pop headers at the same or deeper level from the header path stack."""
        self.path = [h for h in self.path if h.level < level]

    def push_header_path(self, header_path: HeaderPath):
        """Push a header path onto the header path stack.

        Adding a header with a more nested level will pop all headers at the same or deeper level.
        """
        self.pop_level(header_path.level)
        self.path.append(header_path)


class TextNodeAccumulator(BaseModel):
    """An accumulator for text that can be flushed to a callback."""

    ideal_chunk_size: int = Field(default=1200, description="Ideal size of a chunk of text to be returned as a TextNode.")
    flush_callback: Callable[[str], None] = Field(default=lambda x: None, description="Callback to call when the accumulator is flushed.")  # noqa: ARG005
    _text: list[str] = PrivateAttr(default_factory=list)

    @property
    def text(self) -> list[str]:
        return self._text

    @property
    def is_empty(self) -> bool:
        return len(self.text) == 0

    @property
    def size(self) -> int:
        return sum(len(t) for t in self.text)

    def should_flush(self, text: str) -> bool:
        """Check if adding text to the accumulator would overflow the ideal chunk size."""

        if self.is_empty:
            return False

        return self.size + len(text) > self.ideal_chunk_size

    def append(self, text: str) -> None:
        if self.should_flush(text):
            self.flush()

        self._text.append(text)

    def flush(self) -> None:
        if self.is_empty:
            return

        texts = self.text
        self._text = []
        return_text = "".join([text + "\n" for text in texts])
        self.flush_callback(return_text)


def ast_to_markdown(plugins: list[str] | None = None) -> MarkdownRenderer:
    """
    Create a Markdown renderer with the given plugins.
    """
    parser = create_markdown(renderer=MarkdownRenderer(), plugins=plugins or DEFAULT_PLUGINS)

    renderer = parser.renderer
    if not isinstance(renderer, MarkdownRenderer):
        msg = f"Renderer is not a MarkdownRenderer: {renderer}"
        raise TypeError(msg)

    def render_table(renderer: MarkdownRenderer, node: dict[str, Any], block_state: BlockState) -> str:
        rows = [renderer.render_token(child, block_state) for child in node.get("children", [])]
        return "\n".join(rows)

    def render_table_head(renderer: MarkdownRenderer, node: dict[str, Any], block_state: BlockState) -> str:
        first_row = render_table_row(renderer, node, block_state)

        # Take the first row and replace everything but the | with dashes
        second_row = "".join(["-" if c != "|" else c for c in first_row])

        return "\n".join([first_row, second_row])

    def render_table_body(renderer: MarkdownRenderer, node: dict[str, Any], block_state: BlockState) -> str:
        return "\n".join([renderer.render_token(child, block_state) for child in node.get("children", [])])

    def render_table_row(renderer: MarkdownRenderer, node: dict[str, Any], block_state: BlockState) -> str:
        cells = [renderer.render_token(child, block_state) for child in node.get("children", [])]
        return "| " + " | ".join(cells) + " |"

    def render_table_cell(renderer: MarkdownRenderer, node: dict[str, Any], block_state: BlockState) -> str:
        return renderer.render_tokens(node.get("children", []), block_state)

    renderer.register("table", render_table)
    renderer.register("table_head", render_table_head)
    renderer.register("table_body", render_table_body)
    renderer.register("table_row", render_table_row)
    renderer.register("table_cell", render_table_cell)

    return renderer


def markdown_to_ast(plugins: list[str] | None = None) -> MarkdownParser:
    """
    Create a Markdown parser with the given plugins.
    """
    return create_markdown(renderer="ast", plugins=plugins or DEFAULT_PLUGINS)


class MarkdownElementNodeParser(NodeParser):
    """
    Markdown element node parser that extracts TextNodes for headers, tables, and any other elements
    that are specified.
    """

    header_path_separator: str = Field(default="/", description="Separator char used for section header paths.")

    split_on_headers: list[int] = Field(default_factory=lambda: [1], description="List of header levels to always split on.")

    elements: list[str] = Field(
        default_factory=lambda: DEFAULT_ELEMENTS,
        description="List of elements to extract as standalone TextNodes regardless of chunk size.",
    )
    # elements_to_parsers: dict[str, NodeParser] = Field(default_factory=dict, description="Map of elements to parsers.")

    markdown_parser: MarkdownParser = Field(default_factory=lambda: markdown_to_ast())

    markdown_renderer: MarkdownRenderer = Field(default_factory=lambda: ast_to_markdown())

    ideal_chunk_size: int = Field(default=1200, description="Ideal size of a chunk of text to be returned as a TextNode.")

    @classmethod
    def from_defaults(
        cls,
        callback_manager: CallbackManager | None = None,
        include_metadata: bool = True,
        include_prev_next_rel: bool = True,
        header_path_separator: str = "/",
    ) -> "MarkdownElementNodeParser":
        callback_manager = callback_manager or CallbackManager([])
        return cls(
            include_metadata=include_metadata,
            include_prev_next_rel=include_prev_next_rel,
            header_path_separator=header_path_separator,
            callback_manager=callback_manager,
        )

    def _parse_nodes(
        self,
        nodes: Sequence[BaseNode],
        show_progress: bool = False,
        **kwargs: Any,  # noqa: ARG002
    ) -> list[BaseNode]:
        """Parse nodes."""
        all_nodes: list[BaseNode] = []
        nodes_with_progress = get_tqdm_iterable(nodes, show_progress, "Parsing nodes")

        for node in nodes_with_progress:
            nodes = self.get_nodes_from_node(node)
            all_nodes.extend(nodes)

        return all_nodes

    def get_nodes_from_node(self, node: BaseNode) -> list[TextNode]:
        """
        Parse a LLamaIndex Node containing Markdown into a list of TextNodes, each representing a block of content
        with header path metadata.
        """
        markdown_text = node.get_content(metadata_mode=MetadataMode.NONE)
        parser_response: tuple[str | list[dict[str, Any]], BlockState] = self.markdown_parser.parse(markdown_text)

        result, block_state = parser_response

        if isinstance(result, str):
            logger.warning(f"Markdown parse response is a string?! {result}")
            return []

        md_ast_nodes: list[AstNode] = result

        return self._convert_ast(
            llama_node=node,
            md_ast_nodes=md_ast_nodes,
            block_state=block_state,
        )

    def _convert_ast(self, llama_node: BaseNode, md_ast_nodes: list[AstNode], block_state: BlockState) -> list[TextNode]:
        """
        Walk the Markdown AST and return a list of TextNodes with header and type information as metadata
        """

        if len(md_ast_nodes) == 0:
            return []

        text_nodes: list[TextNode] = []

        header_path_stack = HeaderPathStack(path_separator=self.header_path_separator)

        # We will use an accumulator to accumulate text responses from the ast parser
        # The AST parser will return strings for blocks we can concatenate and TextNodes
        # for blocks we want to extract as standalone TextNodes.
        accumulator = TextNodeAccumulator(
            flush_callback=lambda x: text_nodes.append(self._build_text_node(x, llama_node, header_path_stack, "text")),
            ideal_chunk_size=self.ideal_chunk_size,
        )

        for md_ast_node in md_ast_nodes:
            node_type = md_ast_node["type"]

            match node_type:
                case "heading":
                    header_str = self.markdown_renderer.render_token(md_ast_node, block_state)
                    header_level = md_ast_node.get("attrs", {}).get("level")

                    if header_level in self.split_on_headers:
                        accumulator.flush()
                        header_path_stack.push_header_path(HeaderPath(level=header_level, text=header_str))
                    else:
                        accumulator.append(header_str + "\n")

                case "blank_line":
                    continue

                # If this node is an element we are interested in, create a TextNode
                case x if x in self.elements:
                    accumulator.flush()
                    if text_node := self._ast_node_to_textnode(llama_node, md_ast_node, header_path_stack, block_state):
                        text_nodes.append(text_node)

                # Node is not an element we are interested in, accumulate the content.
                case _:
                    accumulator.append(self.markdown_renderer.render_token(md_ast_node, block_state))

        # Flush any remaining text that has accumulated.
        accumulator.flush()

        return text_nodes

    def _ast_node_to_textnode(
        self, llama_node: BaseNode, md_ast_node: AstNode, header_path_stack: HeaderPathStack, block_state: BlockState
    ) -> TextNode:
        """Create a TextNode from an AST node by re-rendering the AST Token and building a TextNode from the content."""
        content = self.markdown_renderer.render_token(md_ast_node, block_state)

        return self._build_text_node(content, llama_node, header_path_stack, md_ast_node["type"])

    def _build_text_node(self, content: str, llama_node: BaseNode, header_path_stack: HeaderPathStack, markdown_type: str) -> TextNode:
        """Build a TextNode from content."""
        text_node = build_nodes_from_splits([content], llama_node, id_func=self.id_func)[0]
        text_node.mimetype = "text/markdown"

        if len(text_node.text) == 0:
            logger.warning(f"Text node has no text: {text_node}")

        text_node.metadata["header_path"] = header_path_stack.path_str
        text_node.metadata["markdown_type"] = markdown_type

        return text_node
