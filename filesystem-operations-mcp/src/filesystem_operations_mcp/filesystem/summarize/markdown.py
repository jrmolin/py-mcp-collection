from typing import Any, ClassVar, cast

from mistune import Markdown
from mistune.core import BaseRenderer, BlockState
from mistune.plugins.table import table


class SimpleRenderer(BaseRenderer):
    """A renderer to re-format Markdown text."""

    NAME: ClassVar[str] = "simple"

    def render_children(self, token: dict[str, Any], state: BlockState) -> str:
        children = token["children"]  # pyright: ignore[reportAny]
        return self.render_tokens(children, state)  # pyright: ignore[reportAny]

    def text(self, token: dict[str, Any], state: BlockState) -> str:  # pyright: ignore[reportUnusedParameter]
        return cast("str", token["raw"])

    def emphasis(self, token: dict[str, Any], state: BlockState) -> str:  # pyright: ignore[reportUnusedParameter]
        return ""

    def strong(self, token: dict[str, Any], state: BlockState) -> str:  # pyright: ignore[reportUnusedParameter]
        return ""

    def link(self, token: dict[str, Any], state: BlockState) -> str:
        return self.render_children(token, state)

    def image(self, token: dict[str, Any], state: BlockState) -> str:  # pyright: ignore[reportUnusedParameter]
        return ""

    def codespan(self, token: dict[str, Any], state: BlockState) -> str:  # pyright: ignore[reportUnusedParameter]
        return "`" + cast("str", token["raw"]) + "`"

    def linebreak(self, token: dict[str, Any], state: BlockState) -> str:  # pyright: ignore[reportUnusedParameter]
        return "  \n"

    def softbreak(self, token: dict[str, Any], state: BlockState) -> str:  # pyright: ignore[reportUnusedParameter]
        return "\n"

    def blank_line(self, token: dict[str, Any], state: BlockState) -> str:  # pyright: ignore[reportUnusedParameter]
        return ""

    def inline_html(self, token: dict[str, Any], state: BlockState) -> str:  # pyright: ignore[reportUnusedParameter]
        return ""

    def paragraph(self, token: dict[str, Any], state: BlockState) -> str:
        text = self.render_children(token, state)
        return text + "\n\n"

    def heading(self, token: dict[str, Any], state: BlockState) -> str:
        # level = cast("int", token["attrs"]["level"])
        # marker = "#" * level
        text = self.render_children(token, state)
        return text + ": "

    def thematic_break(self, token: dict[str, Any], state: BlockState) -> str:  # pyright: ignore[reportUnusedParameter]
        return ""

    def block_text(self, token: dict[str, Any], state: BlockState) -> str:
        return self.render_children(token, state) + "\n"

    def block_code(self, token: dict[str, Any], state: BlockState) -> str:  # pyright: ignore[reportUnusedParameter]
        return ""

    def block_quote(self, token: dict[str, Any], state: BlockState) -> str:  # pyright: ignore[reportUnusedParameter]
        return ""

    def block_html(self, token: dict[str, Any], state: BlockState) -> str:  # pyright: ignore[reportUnusedParameter]
        return ""

    def block_error(self, token: dict[str, Any], state: BlockState) -> str:  # pyright: ignore[reportUnusedParameter]
        return ""

    def list(self, token: dict[str, Any], state: BlockState) -> str:  # pyright: ignore[reportUnusedParameter]
        return ""

    def table(self, token: dict[str, Any], state: BlockState) -> str:  # pyright: ignore[reportUnusedParameter]
        return ""


def summarize_markdown(text: str) -> str:
    rendered = SimpleRenderer()
    markdown = Markdown(renderer=rendered, plugins=[table])
    result = markdown(text)

    if not isinstance(result, str):
        msg = "Result is not a string"
        raise TypeError(msg)

    return result
