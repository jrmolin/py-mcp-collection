from __future__ import annotations

import copy
import pathlib
import re
from io import StringIO
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Optional,
    Sequence,
    Tuple,
    TypedDict,
    cast,
)

from bs4 import Comment
import requests
from langchain_core.documents import BaseDocumentTransformer, Document

from langchain_text_splitters.character import RecursiveCharacterTextSplitter


class ElementType(TypedDict):
    """Element type as typed dict."""

    url: str
    xpath: str
    content: str
    metadata: Dict[str, str]


class HTMLSemanticPreservingSplitter(BaseDocumentTransformer):
    """Split HTML content preserving semantic structure.

    Splits HTML content by headers into generalized chunks, preserving semantic
    structure. If chunks exceed the maximum chunk size, it uses
    RecursiveCharacterTextSplitter for further splitting.

    The splitter preserves full HTML elements (e.g., <table>, <ul>) and converts
    links to Markdown-like links. It can also preserve images, videos, and audio
    elements by converting them into Markdown format. Note that some chunks may
    exceed the maximum size to maintain semantic integrity.

    .. versionadded: 0.3.5

    Args:
        headers_to_split_on (List[Tuple[str, str]]): HTML headers (e.g., "h1", "h2")
            that define content sections.
        max_chunk_size (int): Maximum size for each chunk, with allowance for
            exceeding this limit to preserve semantics.
        chunk_overlap (int): Number of characters to overlap between chunks to ensure
            contextual continuity.
        separators (List[str]): Delimiters used by RecursiveCharacterTextSplitter for
            further splitting.
        elements_to_preserve (List[str]): HTML tags (e.g., <table>, <ul>) to remain
            intact during splitting.
        preserve_links (bool): Converts <a> tags to Markdown links ([text](url)).
        preserve_images (bool): Converts <img> tags to Markdown images (![alt](src)).
        preserve_videos (bool): Converts <video> tags to Markdown
        video links (![video](src)).
        preserve_audio (bool): Converts <audio> tags to Markdown
        audio links (![audio](src)).
        custom_handlers (Dict[str, Callable[[Any], str]]): Optional custom handlers for
            specific HTML tags, allowing tailored extraction or processing.
        stopword_removal (bool): Optionally remove stopwords from the text.
        stopword_lang (str): The language of stopwords to remove.
        normalize_text (bool): Optionally normalize text
            (e.g., lowercasing, removing punctuation).
        external_metadata (Optional[Dict[str, str]]): Additional metadata to attach to
            the Document objects.
        allowlist_tags (Optional[List[str]]): Only these tags will be retained in
            the HTML.
        denylist_tags (Optional[List[str]]): These tags will be removed from the HTML.
        preserve_parent_metadata (bool): Whether to pass through parent document
            metadata to split documents when calling
            ``transform_documents/atransform_documents()``.

    Example:
        .. code-block:: python

            from langchain_text_splitters.html import HTMLSemanticPreservingSplitter

            def custom_iframe_extractor(iframe_tag):
                ```
                Custom handler function to extract the 'src' attribute from an <iframe> tag.
                Converts the iframe to a Markdown-like link: [iframe:<src>](src).

                Args:
                    iframe_tag (bs4.element.Tag): The <iframe> tag to be processed.

                Returns:
                    str: A formatted string representing the iframe in Markdown-like format.
                ```
                iframe_src = iframe_tag.get('src', '')
                return f"[iframe:{iframe_src}]({iframe_src})"

            text_splitter = HTMLSemanticPreservingSplitter(
                headers_to_split_on=[("h1", "Header 1"), ("h2", "Header 2")],
                max_chunk_size=500,
                preserve_links=True,
                preserve_images=True,
                custom_handlers={"iframe": custom_iframe_extractor}
            )
    """  # noqa: E501, D214

    def __init__(
        self,
        headers_to_split_on: List[Tuple[str, str]],
        *,
        max_chunk_size: int = 1000,
        chunk_overlap: int = 0,
        separators: Optional[List[str]] = None,
        elements_to_preserve: Optional[List[str]] = None,
        child_elements_to_preserve: Optional[List[str]] = None,
        preserve_links: bool = False,
        preserve_images: bool = False,
        preserve_videos: bool = False,
        preserve_audio: bool = False,
        custom_handlers: Optional[Dict[str, Callable[[Any], str]]] = None,
        stopword_removal: bool = False,
        stopword_lang: str = "english",
        normalize_text: bool = False,
        external_metadata: Optional[Dict[str, str]] = None,
        allowlist_tags: Optional[List[str]] = None,
        denylist_tags: Optional[List[str]] = None,
        preserve_parent_metadata: bool = False,
    ):
        """Initialize splitter."""
        try:
            from bs4 import BeautifulSoup, Tag

            self._BeautifulSoup = BeautifulSoup
            self._Tag = Tag
        except ImportError:
            raise ImportError(
                "Could not import BeautifulSoup. "
                "Please install it with 'pip install bs4'."
            )

        self._headers_to_split_on = sorted(headers_to_split_on)
        self._max_chunk_size = max_chunk_size
        self._elements_to_preserve = elements_to_preserve or []
        self._child_elements_to_preserve = child_elements_to_preserve or []
        self._preserve_links = preserve_links
        self._preserve_images = preserve_images
        self._preserve_videos = preserve_videos
        self._preserve_audio = preserve_audio
        self._custom_handlers = custom_handlers or {}
        self._stopword_removal = stopword_removal
        self._stopword_lang = stopword_lang
        self._normalize_text = normalize_text
        self._external_metadata = external_metadata or {}
        self._allowlist_tags = allowlist_tags
        self._preserve_parent_metadata = preserve_parent_metadata
        if allowlist_tags:
            self._allowlist_tags = list(
                set(allowlist_tags + [header[0] for header in headers_to_split_on])
            )
        self._denylist_tags = denylist_tags
        if denylist_tags:
            self._denylist_tags = [
                tag
                for tag in denylist_tags
                if tag not in [header[0] for header in headers_to_split_on]
            ]
        if separators:
            self._recursive_splitter = RecursiveCharacterTextSplitter(
                separators=separators,
                chunk_size=max_chunk_size,
                chunk_overlap=chunk_overlap,
            )
        else:
            self._recursive_splitter = RecursiveCharacterTextSplitter(
                chunk_size=max_chunk_size, chunk_overlap=chunk_overlap
            )

        if self._stopword_removal:
            try:
                import nltk  # type: ignore
                from nltk.corpus import stopwords  # type: ignore

                nltk.download("stopwords")
                self._stopwords = set(stopwords.words(self._stopword_lang))
            except ImportError:
                raise ImportError(
                    "Could not import nltk. Please install it with 'pip install nltk'."
                )

    def split_text(self, text: str) -> List[Document]:
        """Splits the provided HTML text into smaller chunks based on the configuration.

        Args:
            text (str): The HTML content to be split.

        Returns:
            List[Document]: A list of Document objects containing the split content.
        """
        soup = self._BeautifulSoup(text, "html.parser")

        self._process_media(soup)

        if self._preserve_links:
            self._process_links(soup)

        if self._allowlist_tags or self._denylist_tags:
            self._filter_tags(soup)

        return self._process_html(soup)

    def transform_documents(
        self, documents: Sequence[Document], **kwargs: Any
    ) -> List[Document]:
        """Transform sequence of documents by splitting them."""
        transformed = []
        for doc in documents:
            splits = self.split_text(doc.page_content)
            if self._preserve_parent_metadata:
                splits = [
                    Document(
                        page_content=split_doc.page_content,
                        metadata={**doc.metadata, **split_doc.metadata},
                    )
                    for split_doc in splits
                ]
            transformed.extend(splits)
        return transformed

    def _process_media(self, soup: Any) -> None:
        """Processes the media elements.

        Process elements in the HTML content by wrapping them in a <media-wrapper> tag
        and converting them to Markdown format.

        Args:
            soup (Any): Parsed HTML content using BeautifulSoup.
        """
        if self._preserve_images:
            for img_tag in soup.find_all("img"):
                img_src = img_tag.get("src", "")
                markdown_img = f"![image:{img_src}]({img_src})"
                wrapper = soup.new_tag("media-wrapper")
                wrapper.string = markdown_img
                img_tag.replace_with(wrapper)

        if self._preserve_videos:
            for video_tag in soup.find_all("video"):
                video_src = video_tag.get("src", "")
                markdown_video = f"![video:{video_src}]({video_src})"
                wrapper = soup.new_tag("media-wrapper")
                wrapper.string = markdown_video
                video_tag.replace_with(wrapper)

        if self._preserve_audio:
            for audio_tag in soup.find_all("audio"):
                audio_src = audio_tag.get("src", "")
                markdown_audio = f"![audio:{audio_src}]({audio_src})"
                wrapper = soup.new_tag("media-wrapper")
                wrapper.string = markdown_audio
                audio_tag.replace_with(wrapper)

    def _process_links(self, soup: Any) -> None:
        """Processes the links in the HTML content.

        Args:
            soup (Any): Parsed HTML content using BeautifulSoup.
        """
        for a_tag in soup.find_all("a"):
            a_href = a_tag.get("href", "")
            a_text = a_tag.get_text(strip=True)
            markdown_link = f"[{a_text}]({a_href})"
            wrapper = soup.new_tag("link-wrapper")
            wrapper.string = markdown_link
            a_tag.replace_with(markdown_link)

    def _filter_tags(self, soup: Any) -> None:
        """Filters the HTML content based on the allowlist and denylist tags.

        Args:
            soup (Any): Parsed HTML content using BeautifulSoup.
        """
        if self._allowlist_tags:
            for tag in soup.find_all(True):
                if tag.name not in self._allowlist_tags:
                    tag.decompose()

        if self._denylist_tags:
            for tag in soup.find_all(self._denylist_tags):
                tag.decompose()

    def _normalize_and_clean_text(self, text: str) -> str:
        """Normalizes the text by removing extra spaces and newlines.

        Args:
            text (str): The text to be normalized.

        Returns:
            str: The normalized text.
        """
        if self._normalize_text:
            text = text.lower()
            text = re.sub(r"[^\w\s]", "", text)
            text = re.sub(r"\s+", " ", text).strip()

        if self._stopword_removal:
            text = " ".join(
                [word for word in text.split() if word not in self._stopwords]
            )

        return text

    def _process_html(self, soup: Any) -> List[Document]:
        """Processes the HTML content using BeautifulSoup and splits it using headers.

        Args:
            soup (Any): Parsed HTML content using BeautifulSoup.

        Returns:
            List[Document]: A list of Document objects containing the split content.
        """
        documents: List[Document] = []
        current_headers: Dict[str, str] = {}
        current_content: List[str] = []
        preserved_elements: Dict[str, str] = {}
        placeholder_count: int = 0

        def _get_element_text(element: Any) -> str:
            """Recursively extracts and processes the text of an element.

            Applies custom handlers where applicable, and ensures correct spacing.

            Args:
                element (Any): The HTML element to process.

            Returns:
                str: The processed text of the element.
            """
            if element.name in self._custom_handlers:
                return self._custom_handlers[element.name](element)

            element_text = element.get_text()

            #if "Notice the use of " in element_text:
                #print(element_text)

            # CUSTOM CHANGE TO LIBRARY TO NOT REPLACE DELAYED ELEMENTS
            if element.name in self._child_elements_to_preserve:
                nonlocal placeholder_count
                placeholder = f"(See reference {placeholder_count})"
                preserved_elements.setdefault(placeholder, "`" + "".join(list(element.strings)) + "`")
                placeholder_count += 1
                return placeholder

            text = ""

            if element.name is not None:
                for child in element.children:
                    # CUSTOM CHANGE TO LIBRARY TO IGNORE COMMENTS
                    if isinstance(child, Comment):
                        continue
                    child_text = _get_element_text(child).strip()
                    if text and child_text:
                        text += " "
                    text += child_text
            elif element.string:
                text += element.string

            return self._normalize_and_clean_text(text)

        elements = soup.find_all(recursive=False)

        def _process_element(
            element: List[Any],
            documents: List[Document],
            current_headers: Dict[str, str],
            current_content: List[str],
            preserved_elements: Dict[str, str],
            placeholder_count: int,
        ) -> Tuple[List[Document], Dict[str, str], List[str], Dict[str, str], int]:
            for elem in element:
                if elem.name.lower() in ["html", "body", "div", "main"]:
                    children = elem.find_all(recursive=False)
                    (
                        documents,
                        current_headers,
                        current_content,
                        preserved_elements,
                        placeholder_count,
                    ) = _process_element(
                        children,
                        documents,
                        current_headers,
                        current_content,
                        preserved_elements,
                        placeholder_count,
                    )
                    continue

                if elem.name in [h[0] for h in self._headers_to_split_on]:
                    if current_content:
                        documents.extend(
                            self._create_documents(
                                current_headers,
                                " ".join(current_content),
                                preserved_elements,
                            )
                        )
                        current_content.clear()
                        preserved_elements.clear()
                    header_name = elem.get_text(strip=True)
                    current_headers = {
                        dict(self._headers_to_split_on)[elem.name]: header_name
                    }
                elif elem.name in self._elements_to_preserve:
                    placeholder = f"PRESERVED_{placeholder_count}"
                    preserved_elements[placeholder] = _get_element_text(elem)
                    current_content.append(placeholder)
                    placeholder_count += 1
                else:
                    content = _get_element_text(elem)
                    if content:
                        current_content.append(content)

            return (
                documents,
                current_headers,
                current_content,
                preserved_elements,
                placeholder_count,
            )

        # Process the elements
        (
            documents,
            current_headers,
            current_content,
            preserved_elements,
            placeholder_count,
        ) = _process_element(
            elements,
            documents,
            current_headers,
            current_content,
            preserved_elements,
            placeholder_count,
        )

        # Handle any remaining content
        if current_content:
            documents.extend(
                self._create_documents(
                    current_headers,
                    " ".join(current_content),
                    preserved_elements,
                )
            )

        return documents

    def _create_documents(
        self, headers: dict, content: str, preserved_elements: dict
    ) -> List[Document]:
        """Creates Document objects from the provided headers, content, and elements.

        Args:
            headers (dict): The headers to attach as metadata to the Document.
            content (str): The content of the Document.
            preserved_elements (dict): Preserved elements to be reinserted
            into the content.

        Returns:
            List[Document]: A list of Document objects.
        """
        content = re.sub(r"\s+", " ", content).strip()

        metadata = {**headers, **self._external_metadata}

        if len(content) <= self._max_chunk_size:
            page_content, delayed_replacements = self._reinsert_preserved_elements(
                content, preserved_elements
            )
            metadata["delayed_replacements"] = delayed_replacements
            return [Document(page_content=page_content, metadata=metadata)]
        else:
            return self._further_split_chunk(content, metadata, preserved_elements)

    def _further_split_chunk(
        self, content: str, metadata: dict, preserved_elements: dict
    ) -> List[Document]:
        """Further splits the content into smaller chunks.

        Args:
            content (str): The content to be split.
            metadata (dict): Metadata to attach to each chunk.
            preserved_elements (dict): Preserved elements
            to be reinserted into each chunk.

        Returns:
            List[Document]: A list of Document objects containing the split content.
        """
        splits = self._recursive_splitter.split_text(content)
        result = []

        for split in splits:
            split_with_preserved, delayed_replacements = self._reinsert_preserved_elements(
                split, preserved_elements
            )
            # CUSTOM CHANGE TO LIBRARY TO STORE PRESERVED ELEMENTS
            metadata["delayed_replacements"] = delayed_replacements
            if split_with_preserved.strip():
                result.append(
                    Document(
                        page_content=split_with_preserved.strip(),
                        metadata=metadata,
                    )
                )

        return result

    def _reinsert_preserved_elements(
        self, content: str, preserved_elements: dict
    ) -> tuple[str, dict[str, str]]:
        """Reinserts preserved elements into the content into their original positions.

        Args:
            content (str): The content where placeholders need to be replaced.
            preserved_elements (dict): Preserved elements to be reinserted.

        Returns:
            str: The content with placeholders replaced by preserved elements.
        """
        delayed_replacements: dict[str, str] = {}

        # We need to enumerate the dictionary in reverse order to avoid replacing placeholders that are inside other placeholders
        for placeholder, preserved_content in reversed(preserved_elements.items()):
            # CUSTOM CHANGE TO LIBRARY TO NOT REPLACE DELAYED ELEMENTS
            if "(See reference " in placeholder and placeholder in content:
                delayed_replacements[placeholder] = preserved_content.strip()
                continue

            content = content.replace(placeholder, preserved_content.strip())
        return content, delayed_replacements


# %%
