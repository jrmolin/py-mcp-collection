import logging
from collections.abc import AsyncGenerator
from datetime import UTC, datetime

from fastmcp import FastMCP
from fastmcp.contrib.mcp_mixin.mcp_mixin import MCPMixin, mcp_tool
from langchain_core.documents import Document
from pydantic import BaseModel, Field, HttpUrl
from unstructured_client import Any

from doc_store_vector_search_mcp.etl.load import DirectoryLoader, RecursiveWebLoader, WebPageLoader
from doc_store_vector_search_mcp.etl.split import HtmlSplitter, MarkdownSplitter
from doc_store_vector_search_mcp.etl.store import KnowledgeBaseVectorStoreManager, ProjectVectorStoreManager
from html_to_markdown import markdownify

logger = logging.getLogger(__name__)


class StartLoad(BaseModel):
    start_time: datetime = Field(default_factory=lambda: datetime.now(UTC))


class LoadSummary(BaseModel):
    source_documents: int
    documents: int
    chunks: int
    took: float

    @classmethod
    def from_start_load(cls, start_load: StartLoad, source_documents: int, documents: int, chunks: int) -> "LoadSummary":
        return cls(
            source_documents=source_documents,
            documents=documents,
            chunks=chunks,
            took=(datetime.now(UTC) - start_load.start_time).total_seconds(),
        )


class DocumentKnowledgeBaseMetadata(BaseModel):
    knowledge_base: str
    project: str


class DocumentMetadata(DocumentKnowledgeBaseMetadata):
    source: str
    fetched: datetime = Field(default_factory=datetime.now)

    @classmethod
    def from_document(cls, kb_metadata: DocumentKnowledgeBaseMetadata, source: str, fetched: datetime) -> "DocumentMetadata":
        return cls(
            knowledge_base=kb_metadata.knowledge_base,
            project=kb_metadata.project,
            source=source,
            fetched=fetched,
        )


class DocumentServer(MCPMixin, FastMCP):
    def __init__(self, project_name: str, project_vectorstore: ProjectVectorStoreManager):
        self.project_name = project_name
        self.project_vectorstore = project_vectorstore

    def _get_started(self, knowledge_base: str) -> tuple[KnowledgeBaseVectorStoreManager, StartLoad, DocumentKnowledgeBaseMetadata]:
        knowledge_base_vectorstore = KnowledgeBaseVectorStoreManager.from_project_vector_store(knowledge_base, self.project_vectorstore)
        start_load = StartLoad()
        kb_metadata = DocumentKnowledgeBaseMetadata(knowledge_base=knowledge_base, project=self.project_name)

        logger.info(f"Starting load for knowledge base {knowledge_base} in project {self.project_name}")

        return knowledge_base_vectorstore, start_load, kb_metadata

    @classmethod
    async def load_directory(
        cls, directory: str
    ) -> AsyncGenerator[
        Document,
        None,
    ]:
        async for document in DirectoryLoader.load(directory_path=directory, glob=["**/*.md", "**/*.txt", "**/*.mdx"]):
            yield document

    @mcp_tool()
    async def load_directories(self, knowledge_base: str, directories: list[str]) -> LoadSummary:
        """Loads all documents in the given directories into the knowledge base.

        Args:
            knowledge_base: The name of theknowledge base to load the documents into.
            directories: The directories to load the documents from.

        Returns:
            A summary of the load including the number of source documents, documents, and chunks.
        """

        logger.info(f"Loading directories {directories} for knowledge base {knowledge_base} in project {self.project_name}")

        knowledge_base_vectorstore, start_load, kb_metadata = self._get_started(knowledge_base)

        source_documents = 0
        document_count = 0
        chunk_count = 0

        splitter = MarkdownSplitter()

        for directory in directories:
            async for document in self.load_directory(directory):
                source_documents += 1

                document_metadata = DocumentMetadata.from_document(kb_metadata, directory, datetime.now(UTC))
                split_documents = splitter.split_to_documents(document.page_content)

                document_count += 1
                chunk_count += len(split_documents)

                logger.info(f"Adding {len(split_documents)} chunks to knowledge base {knowledge_base} in project {self.project_name}")
                await knowledge_base_vectorstore.add_markdown_documents(split_documents, document_metadata.model_dump())

        load_summary = LoadSummary.from_start_load(start_load, source_documents, document_count, chunk_count)
        logger.info(f"Load summary: {load_summary}")

        return load_summary

    async def process_web_document(self, html_splitter: HtmlSplitter, document: Document) -> list[Document]:
        split_lines = document.page_content.splitlines()
        split_lines = [line for line in split_lines if line.strip() != ""]
        # remove consecutive duplicate lines
        split_lines = [line for i, line in enumerate(split_lines) if i == 0 or line != split_lines[i - 1]]

        return html_splitter.split_to_documents("\n".join(split_lines))

    @mcp_tool()
    async def load_webpage(self, knowledge_base: str, urls: list[HttpUrl], recursive: bool = False) -> LoadSummary:
        """Loads the given URLs into the knowledge base.

        Args:
            knowledge_base: The name of the knowledge base to load the documents into.
            urls: The URLs to load the documents from.
            recursive: Whether to follow links on the page and load them recursively.

        Returns:
            A summary of the load including the number of source documents, documents, and chunks.
        """

        logger.info(f"Loading {len(urls)} URLs for knowledge base {knowledge_base} in project {self.project_name}")

        knowledge_base_vectorstore, start_load, kb_metadata = self._get_started(knowledge_base)

        source_documents = 0
        document_count = 0
        chunk_count = 0

        html_splitter = HtmlSplitter()

        loader = WebPageLoader if not recursive else RecursiveWebLoader

        for url in urls:
            document_metadata = DocumentMetadata.from_document(kb_metadata, str(url), datetime.now(UTC))

            async for document in loader.load(url=str(url)):
                source_documents += 1

                split_documents = await self.process_web_document(html_splitter, document)

                document_count += 1
                chunk_count += len(split_documents)

                logger.info(f"Adding {len(split_documents)} chunks to knowledge base {knowledge_base} in project {self.project_name}")
                await knowledge_base_vectorstore.add_markdown_documents(split_documents, document_metadata.model_dump())

        return LoadSummary.from_start_load(start_load, source_documents, document_count, chunk_count)
