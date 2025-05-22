import logging
from collections.abc import AsyncGenerator
from datetime import datetime
from xml.dom.minidom import Document

from fastmcp import FastMCP
from fastmcp.contrib.mcp_mixin.mcp_mixin import MCPMixin, mcp_tool
from pydantic import BaseModel, Field
from unstructured_client import Any

from doc_store_vector_search_mcp.etl.load import DirectoryLoader
from doc_store_vector_search_mcp.etl.split import MarkdownSplitter
from doc_store_vector_search_mcp.etl.store import KnowledgeBaseVectorStoreManager, ProjectVectorStoreManager

logger = logging.getLogger(__name__)


class StartLoad(BaseModel):
    start_time: datetime = Field(default_factory=datetime.now)


class LoadSummary(BaseModel):
    source_documents: int
    documents: int
    chunks: int
    took: float

    @classmethod
    def from_start_load(cls, start_load: StartLoad) -> "LoadSummary":
        return cls(
            source_documents=start_load.source_documents,
            documents=0,
            chunks=0,
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
        knowledge_base_vectorstore = KnowledgeBaseVectorStoreManager.from_project_vectorstore(knowledge_base, self.project_vectorstore)
        start_load = StartLoad()
        kb_metadata = DocumentKnowledgeBaseMetadata(knowledge_base=knowledge_base, project=self.project_name)

        logger.info(f"Starting load for knowledge base {knowledge_base} in project {self.project_name}")

        return knowledge_base_vectorstore, start_load, kb_metadata

    @classmethod
    async def load_directory(cls, directory: str) -> AsyncGenerator[list[Document], None]:
        for document in await DirectoryLoader.load_directory(directory):
            yield document

    @mcp_tool
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
        documents = 0
        chunks = 0

        splitter = MarkdownSplitter()

        for directory in directories:
            async for document in self.load_directory(directory):
                source_documents += 1

                document_metadata = DocumentMetadata.from_document(kb_metadata, directory)
                chunks = splitter.split(document)

                documents += 1
                chunks += len(chunks)

                logger.info(f"Adding {len(chunks)} chunks to knowledge base {knowledge_base} in project {self.project_name}")
                knowledge_base_vectorstore.add_document(chunks, document_metadata.model_dump())

        load_summary = LoadSummary.from_start_load(start_load, source_documents, documents, chunks)
        logger.info(f"Load summary: {load_summary}")

        return load_summary

    @mcp_tool
    async def load_webpage(self, to_load: Any) -> LoadSummary:
        pass
