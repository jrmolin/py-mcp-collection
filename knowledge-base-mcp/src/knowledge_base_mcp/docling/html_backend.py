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
