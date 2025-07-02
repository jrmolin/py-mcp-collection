from typing import override

from bs4 import BeautifulSoup, Tag
from docling.backend.html_backend import HTMLDocumentBackend
from docling_core.types.doc.document import (
    ContentLayer,
    DoclingDocument,
)

CONVERT_TAGS = {
    "dl": "ol",
    "dd": "li",
    "dt": "li",
}
SKIP_TAGS = {"footer", "nav", "aside", "search", "video", "audio", "track", "script", "style"}


class TrimmedHTMLDocumentBackend(HTMLDocumentBackend):
    content_layer: ContentLayer
    level: int

    replacements: bool = False

    @override
    def walk(self, tag: Tag, doc: DoclingDocument) -> None:
        """Walk the HTML document and add the tags to the document."""

        if tag.name in SKIP_TAGS:
            return

        if not self.replacements:
            if not isinstance(self.soup, BeautifulSoup):
                return

            # Swap dl/dd tags for ol/li tags
            if dl_tags := tag.find_all(name="dl"):
                for dl_tag in dl_tags:
                    if isinstance(dl_tag, Tag):
                        dl_tag.name = "ul"
                        for dt_tag in dl_tag.find_all(name="dt"):
                            if isinstance(dt_tag, Tag):
                                dt_tag.name = "li"
                        for dd_tag in dl_tag.find_all(name="dd"):
                            if isinstance(dd_tag, Tag):
                                dd_tag.name = "li"
                                ul_tag = self.soup.new_tag("ul")
                                _ = dd_tag.wrap(ul_tag)

            self.replacements = True

        super().walk(tag=tag, doc=doc)

    # @override
    # def walk(self, tag: Tag, doc: DoclingDocument) -> None:
    #     move_tags_to_furniture: set[str] = {"footer", "nav"}

    #     was_in_body: bool = self.content_layer == ContentLayer.BODY

    #     if was_in_body and tag.name in move_tags_to_furniture:
    #         self.content_layer = ContentLayer.FURNITURE

    #     super().walk(tag=tag, doc=doc)

    #     if was_in_body and tag.name in move_tags_to_furniture:
    #         self.content_layer = ContentLayer.BODY

    # @override
    # def handle_header(self, element: Tag, doc: DoclingDocument) -> None:
    #     """Handles header tags (h1, h2, etc.)."""
    #     hlevel = int(element.name.replace("h", ""))

    #     text = element.text  # pyright: ignore[reportAny]

    #     if not isinstance(text, str):
    #         msg = f"Element text is not a string: {text}"
    #         raise TypeError(msg)

    #     text = text.strip()

    #     if self.content_layer == ContentLayer.FURNITURE:
    #         is_in_footer = element.find_parents("footer", limit=1)
    #         is_in_nav = element.find_parents("nav", limit=1)
    #         if not is_in_footer and not is_in_nav:
    #             self.content_layer = ContentLayer.BODY

    #     if hlevel == 1:
    #         for key in self.parents:
    #             self.parents[key] = None

    #         self.level = 1
    #         self.parents[self.level] = doc.add_text(
    #             parent=self.parents[0],
    #             label=DocItemLabel.TITLE,
    #             text=text,
    #             content_layer=self.content_layer,
    #         )
    #     else:
    #         if hlevel > self.level:
    #             # add invisible group
    #             for i in range(self.level + 1, hlevel):
    #                 self.parents[i] = doc.add_group(
    #                     name=f"header-{i}",
    #                     label=GroupLabel.SECTION,
    #                     parent=self.parents[i - 1],
    #                     content_layer=self.content_layer,
    #                 )
    #             self.level = hlevel

    #         elif hlevel < self.level:
    #             # remove the tail
    #             for key in self.parents:
    #                 if key > hlevel:
    #                     self.parents[key] = None
    #             self.level = hlevel

    #         self.parents[hlevel] = doc.add_heading(
    #             parent=self.parents[hlevel - 1],
    #             text=text,
    #             level=hlevel - 1,
    #             content_layer=self.content_layer,
    #         )
