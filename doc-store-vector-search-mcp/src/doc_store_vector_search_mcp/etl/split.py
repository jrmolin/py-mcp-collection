from abc import ABC, abstractmethod
from typing import Any, TypeAlias

import langchain_text_splitters
from langchain_core.documents import Document
from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
    RecursiveJsonSplitter,
)
from typing_extensions import TypeVar

T = TypeVar("T")


class Splitter(ABC):
    @abstractmethod
    def split_to_documents(self, to_split: T) -> list[Document]:
        pass


CodeSplitterLanguage: TypeAlias = langchain_text_splitters.Language  # noqa: UP040


def tag_document_order(documents: list[Document]) -> list[Document]:
    for i, document in enumerate(documents):
        document.metadata["order"] = i
    return documents


class JsonSplitter(Splitter):
    def __init__(self):
        self.splitter = RecursiveJsonSplitter(
            max_chunk_size=500,
            min_chunk_size=25,
        )

    def split_to_documents(self, to_split: dict[str, Any]) -> list[Document]:
        return tag_document_order(self.splitter.create_documents([to_split], convert_lists=True))


class MarkdownSplitter:
    def __init__(self):
        self.header_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=[
                ("#", "Header 1"),
                ("##", "Header 2"),
            ],
            strip_headers=False,
        )
        self.chunk_splitter = RecursiveCharacterTextSplitter(
            chunk_size=300,
            chunk_overlap=25,
        )

    def split_to_documents(self, text: str) -> list[Document]:
        per_header_documents: list[Document] = self.header_splitter.split_text(text)
        chunked_documents: list[Document] = []

        for document in per_header_documents:
            chunked_documents.extend(self.chunk_splitter.split_documents([document]))

        return tag_document_order(chunked_documents)


class CodeSplitter:
    def __init__(self, language: CodeSplitterLanguage):
        self.splitter = RecursiveCharacterTextSplitter.from_language(
            language,
            chunk_size=300,
            chunk_overlap=25,
        )

    def split_to_documents(self, text: str) -> list[Document]:
        chunks = self.splitter.split_text(text)
        return tag_document_order(self.splitter.create_documents(chunks))
