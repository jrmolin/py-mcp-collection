from abc import ABC, abstractmethod
from typing import Any, TypeAlias

import langchain_text_splitters
from bs4.element import Tag
from langchain_core.documents import Document
from langchain_core.embeddings.embeddings import Embeddings
from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
    RecursiveJsonSplitter,
)
from typing_extensions import TypeVar

from doc_store_vector_search_mcp.summarization.text import clean_sentences, extract_sentences, remove_horrible_sentences

from .splitters.html import HTMLSemanticPreservingSplitter
from .splitters.semantic import SemanticChunker

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


class HtmlSplitter:
    def __init__(self):
        headers_to_split_on = [
            ("h1", "Header 1"),
            ("h2", "Header 2"),
        ]

        def code_handler(element: Tag) -> str:
            data_lang = element.get("data-lang")
            if len(element.get_text()) < 40:
                code_format = f"`{element.get_text()}`"
            else:
                code_format = f"<code:{data_lang}>\n...removed...\n</code>"

            return code_format

        self.splitter = HTMLSemanticPreservingSplitter(
            headers_to_split_on=headers_to_split_on,
            separators=["\n\n", "\n", ". ", "! ", "? "],
            max_chunk_size=4000,
            chunk_overlap=0,
            preserve_images=False,
            preserve_videos=False,
            elements_to_preserve=["table", "ul", "ol"],
            child_elements_to_preserve=["code"],
            denylist_tags=["script", "style", "head", "nav", "comment"],
            custom_handlers={},
        )

    def split_documents(self, documents: list[Document]) -> list[Document]:
        documents = self.splitter.transform_documents(documents)
        return tag_document_order(documents)

    def split_to_documents(self, to_split: str) -> list[Document]:
        documents = self.splitter.split_text(to_split)
        return tag_document_order(documents)


class JsonSplitter:
    def __init__(self):
        self.splitter = RecursiveJsonSplitter(
            max_chunk_size=2000,
            min_chunk_size=200,
        )

    def split_to_documents(self, to_split: dict[str, Any]) -> list[Document]:
        return tag_document_order(self.splitter.create_documents([to_split], convert_lists=True))


class MarkdownSplitter:
    def __init__(self):
        self.header_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=[
                ("#", "Header 1"),
                ("##", "Header 2"),
                ("###", "Header 3"),
            ],
            strip_headers=False,
        )
        self.chunk_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000,
            chunk_overlap=25,
        )

    # def split_documents(self, documents: list[Document]) -> list[Document]:
    #     return tag_document_order(self.chunk_splitter.split_documents(documents))

    def split_to_sections(self, text: str) -> list[Document]:
        return self.header_splitter.split_text(text)

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
            chunk_size=2000,
            chunk_overlap=25,
        )

    def split_to_documents(self, text: str) -> list[Document]:
        chunks = self.splitter.split_text(text)
        return tag_document_order(self.splitter.create_documents(chunks))


class SemanticSplitter:
    def __init__(self, embeddings: Embeddings):
        self.splitter = SemanticChunker(
            embeddings=embeddings,
            breakpoint_threshold_type="gradient",
            breakpoint_threshold_amount=96,
        )

    def split_documents(self, documents: list[Document]) -> list[Document]:
        new_documents: list[Document] = []

        for document in documents:
            doc_sentences = extract_sentences(document.page_content)
            doc_sentences = clean_sentences(doc_sentences)
            doc_sentences = move_references_to_previous_sentence(doc_sentences)
            #doc_sentences = remove_horrible_sentences(doc_sentences)
            # doc_sentences = remove_gibberish(doc_sentences)

            if len(doc_sentences) == 0:
                continue
            
            chunks: list[list[str]] = self.splitter.split_sentences(doc_sentences)
            chunks = ChunkSplitter.split_and_overlap_chunks(chunks)

            for chunk in chunks:
                new_document = Document(page_content=" ".join(chunk), metadata=document.metadata)
                new_documents.append(new_document)

        return tag_document_order(new_documents)

    # def sentences_to_chunks(self, sentences: list[str]) -> list[str]:
    #     return self.splitter.split_sentences(sentences)


class ChunkSplitter:
    @classmethod
    def split_and_overlap_chunks(cls, chunks: list[list[str]], max_chunk_size: int = 1200) -> list[list[str]]:
        new_chunks = []
        for chunk in chunks:
            new_chunks.extend(cls.split_and_overlap_chunk(chunk, max_chunk_size))
        return new_chunks

    @classmethod
    def split_and_overlap_chunk(cls, chunk: list[str], max_chunk_size: int = 1200) -> list[list[str]]:
        if sum(len(sentence) for sentence in chunk) <= max_chunk_size:
            return [chunk]

        # Split the chunk into chunks
        new_chunks = []

        sentences = [*chunk]

        while len(sentences) > 0:
            new_chunk = []
            new_chunk_size = 0
            while new_chunk_size < max_chunk_size and len(sentences) > 0:
                sentence = sentences.pop(0)
                new_chunk.append(sentence)
                new_chunk_size += len(sentence)

            new_chunks.append(new_chunk)

        # Overlap the chunks on both ends
        for i in range(1, len(new_chunks) - 1):
            previous_chunk = new_chunks[i - 1]
            current_chunk = new_chunks[i]
            previous_chunk_last_sentence = previous_chunk[-1]
            current_chunk_first_sentence = current_chunk[0]

            current_chunk = [previous_chunk_last_sentence, *current_chunk]
            previous_chunk = [*previous_chunk, current_chunk_first_sentence]

            new_chunks[i - 1] = previous_chunk
            new_chunks[i] = current_chunk

        return new_chunks


def move_references_to_previous_sentence(sentences: list[str]) -> list[str]:
    """If the sentence starts with a reference, move it to the previous sentence.

    References are defined as `(See reference ###)`
    """
    new_sentences = []

    for i, sentence in enumerate(sentences):
        if i > 0 and sentence.startswith("(See reference"):
            # Pull out the reference
            parts = sentence.split(")", 1)

            reference = parts[0] + ")"

            # Create the new current sentence
            new_sentence = parts[1].lstrip()

            # Update the previous sentence
            previous_sentence = sentences[i - 1]

            # Place the reference at the end of the previous sentence, before the punctuation
            new_previous_sentence = previous_sentence[:-1] + " " + reference
            new_previous_sentence += previous_sentence[-1]

            new_sentences[-1] = new_previous_sentence

            # Add the rest of the sentence to the new sentence
            new_sentences.append(new_sentence)
        else:
            new_sentences.append(sentence)

    return new_sentences
