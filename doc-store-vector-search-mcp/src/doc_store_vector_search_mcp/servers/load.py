from collections.abc import AsyncGenerator
from datetime import UTC, datetime

from fastmcp.contrib.mcp_mixin.mcp_mixin import MCPMixin, mcp_tool
from html_to_markdown import markdownify
from langchain_core.documents import Document
from pydantic import BaseModel, Field, HttpUrl, field_serializer

from doc_store_vector_search_mcp.etl.load import DirectoryLoader, RecursiveWebLoader, WebPageLoader
from doc_store_vector_search_mcp.etl.split import HtmlSplitter, MarkdownSplitter, SemanticSplitter
from doc_store_vector_search_mcp.etl.store import KnowledgeBaseVectorStoreManager, ProjectVectorStoreManager
from doc_store_vector_search_mcp.logging.util import BASE_LOGGER

logger = BASE_LOGGER.getChild("load")


class StartLoad(BaseModel):
    start_time: datetime = Field(default_factory=lambda: datetime.now(UTC))


class LoadSummary(BaseModel):
    source_documents: int
    documents: int
    took: float

    @classmethod
    def from_start_load(cls, start_load: StartLoad, source_documents: int, documents: int) -> "LoadSummary":
        return cls(
            source_documents=source_documents,
            documents=documents,
            took=(datetime.now(UTC) - start_load.start_time).total_seconds(),
        )


class DocumentKnowledgeBaseMetadata(BaseModel):
    knowledge_base: str
    project: str


class DocumentMetadata(DocumentKnowledgeBaseMetadata):
    target: str
    fetched: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @field_serializer("fetched")
    def serialize_fetched(self, fetched: datetime, _info):
        return fetched.timestamp()

    @classmethod
    def from_document(cls, kb_metadata: DocumentKnowledgeBaseMetadata, target: str, fetched: datetime) -> "DocumentMetadata":
        return cls(knowledge_base=kb_metadata.knowledge_base, project=kb_metadata.project, target=target, fetched=fetched)


class DocumentServer(MCPMixin):
    def __init__(self, project_name: str, project_vectorstore: ProjectVectorStoreManager):
        self.project_name = project_name
        self.project_vectorstore = project_vectorstore
        self.underlying_vector_store = project_vectorstore.document_vector_store

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
                await knowledge_base_vectorstore.add_markdown_documents(
                    split_documents,
                    {
                        **document_metadata.model_dump(),
                        **document.metadata,
                    },
                )

        load_summary = LoadSummary.from_start_load(start_load, source_documents, document_count)
        logger.info(f"Load summary: {load_summary}")

        return load_summary

    async def process_web_document(self, html_splitter: HtmlSplitter, document: Document) -> list[Document]:
        split_lines = document.page_content.splitlines()
        split_lines = [line for line in split_lines if line.strip() != ""]
        # remove consecutive duplicate lines
        split_lines = [line for i, line in enumerate(split_lines) if i == 0 or line != split_lines[i - 1]]

        new_documents = html_splitter.split_to_documents("\n".join(split_lines))
        [new_document.metadata.update(document.metadata) for new_document in new_documents]
        return new_documents

    async def process_web_document_as_markdown(self, markdown_splitter: MarkdownSplitter, document: Document) -> list[Document]:
        markdown = markdownify(document.page_content)
        print(f"Markdown: {markdown}")
        new_documents = markdown_splitter.split_to_documents(markdown)
        [print(f"New document: {new_document.page_content}") for new_document in new_documents]
        [new_document.metadata.update(document.metadata) for new_document in new_documents]
        return new_documents

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

        html_splitter = HtmlSplitter()
        semantic_splitter = SemanticSplitter(self.underlying_vector_store.document_semantic_splitter.embeddings)

        loader = WebPageLoader if not recursive else RecursiveWebLoader

        for url in urls:
            async for raw_html_document in loader.load(url=str(url)):
                source_documents += 1
                document_metadata = DocumentMetadata.from_document(kb_metadata, str(url), datetime.now(UTC))

                html_documents = html_splitter.split_documents([raw_html_document])

                semantically_grouped_html_documents = semantic_splitter.split_documents(html_documents)

                prepared_documents = [
                    self.underlying_vector_store.prepare_document_for_embedding(document)
                    for document in semantically_grouped_html_documents
                ]

                document_count += len(prepared_documents)

                if len(prepared_documents) == 0:
                    logger.warning(f"No documents to add for {url}")
                    continue

                logger.info(f"Adding {len(prepared_documents)} chunks to knowledge base {knowledge_base} in project {self.project_name}")
                await knowledge_base_vectorstore.add_markdown_documents(
                    prepared_documents,
                    {
                        **document_metadata.model_dump(),
                        **raw_html_document.metadata,
                    },
                )

        return LoadSummary.from_start_load(start_load, source_documents, document_count)
