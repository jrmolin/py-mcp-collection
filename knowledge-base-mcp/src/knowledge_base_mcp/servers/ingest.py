import datetime
import tempfile
from functools import cached_property
from logging import Logger
from typing import Annotated

from fastmcp import Context
from fastmcp.tools import Tool as FastMCPTool
from git import Repo
from llama_index.core.ingestion.pipeline import IngestionPipeline
from llama_index.core.schema import Document
from pydantic import Field
from pydantic.main import BaseModel

from knowledge_base_mcp.clients.knowledge_base import KnowledgeBaseClient
from knowledge_base_mcp.docling.md_backend import GroupingMarkdownDocumentBackend
from knowledge_base_mcp.llama_index.readers.directory import FastDirectoryReader
from knowledge_base_mcp.llama_index.readers.web import RecursiveAsyncWebReader
from knowledge_base_mcp.llama_index.transformations.metadata import IncludeMetadata, RenameMetadata
from knowledge_base_mcp.utils.iterators import achunk
from knowledge_base_mcp.utils.logging import BASE_LOGGER
from knowledge_base_mcp.utils.models import BaseKBModel
from knowledge_base_mcp.utils.patches import apply_patches
from knowledge_base_mcp.utils.workers import worker_pool

apply_patches()


logger: Logger = BASE_LOGGER.getChild(suffix=__name__)


NewKnowledgeBaseField = Annotated[
    str,
    Field(
        description="The name of the Knowledge Base to create to store this webpage.",
        examples=["Python Language - 3.12", "Python Library - Pydantic - 2.11", "Python Library - FastAPI - 0.115"],
    ),
]

SeedPagesField = Annotated[
    list[str],
    Field(
        description="The seed URLs to crawl and add to the knowledge base. Only child pages of the provided URLs will be crawled.",
        examples=["https://www.python.org/docs/3.12/"],
    ),
]

URLExclusionsField = Annotated[
    list[str] | None,
    Field(
        description="The URLs to exclude from the crawl.",
        examples=["https://www.python.org/docs/3.12/library/typing.html"],
    ),
]

MaxPagesField = Annotated[
    int | None,
    Field(
        description="The maximum number of pages to crawl.",
        examples=[1000],
    ),
]

DirectoryPathField = Annotated[
    str,
    Field(
        description="The path to the directory to ingest.",
        examples=["/path/to/directory"],
    ),
]

DirectoryExcludeField = Annotated[
    list[str] | None,
    Field(
        description="File path globs to exclude from the crawl. Defaults to None.",
        examples=["*changelog*", "*.md", "*.txt", "*.html"],
    ),
]


DirectoryFilterExtensionsField = Annotated[
    list[str] | None,
    Field(
        description="The file extensions to gather. Only Markdown, AsciiDoc, and HTML files are supported. Defaults to AsciiDoc and Markdown",
        examples=[".md", ".ad", ".adoc", ".asc", ".asciidoc"],
    ),
]

DirectoryRecursiveField = Annotated[
    bool,
    Field(
        description="Whether to recursively gather files from the directory. Defaults to True.",
        examples=[True],
    ),
]


class IngestResult(BaseModel):
    """The result of an ingestion operation."""

    start_time: datetime.datetime = Field(default_factory=datetime.datetime.now, exclude=True)

    documents: int = Field(default=0, description="The number of documents ingested.")
    parsed_nodes: int = Field(default=0, description="The number of nodes ingested.")
    ingested_nodes: int = Field(default=0, description="The number of nodes ingested into the knowledge base.")

    last_update: datetime.datetime = Field(default_factory=datetime.datetime.now, exclude=True)

    def merge(self, other: "IngestResult") -> "IngestResult":
        """Merge two ingestion results."""
        self.documents += other.documents
        self.parsed_nodes += other.parsed_nodes
        self.ingested_nodes += other.ingested_nodes
        self.last_update = max(self.last_update, other.last_update)
        return self

    @classmethod
    def merge_results(cls, results: list["IngestResult"]) -> "IngestResult":
        """Merge a list of ingestion results."""

        if len(results) == 0:
            msg = "Cannot merge an empty list of results."
            raise ValueError(msg)

        if len(results) == 1:
            return results[0]

        merged_result: IngestResult = results[0]

        for result in results[1:]:
            merged_result = merged_result.merge(other=result)

        return merged_result

    def duration(self) -> datetime.timedelta:
        """The duration of the ingestion."""
        return self.last_update - self.start_time


class IngestServer(BaseKBModel):
    """A server for ingesting documentation."""

    knowledge_base_client: KnowledgeBaseClient

    workers: int = Field(default=4, description="The number of workers to use for ingestion.")

    def get_raw_tools(self) -> list[FastMCPTool]:
        return [
            FastMCPTool.from_function(fn=self.load_website),
            FastMCPTool.from_function(fn=self.load_directory),
            FastMCPTool.from_function(fn=self.load_git_repository),
        ]

    async def _log_info(self, context: Context, message: str) -> None:
        await context.info(message=message)
        logger.info(msg=message)

    @cached_property
    def _docling_documentation_pipeline(self) -> IngestionPipeline:
        """A pipeline for parsing a webpage into a Docling document."""
        from docling.datamodel.base_models import InputFormat
        from docling.document_converter import FormatOption
        from docling.pipeline.simple_pipeline import SimplePipeline

        from knowledge_base_mcp.docling.html_backend import TrimmedHTMLDocumentBackend
        from knowledge_base_mcp.llama_index.hierarchical_node_parsers.docling_hierarchical_node_parser import DoclingHierarchicalNodeParser

        hierarchical_node_parser: DoclingHierarchicalNodeParser = DoclingHierarchicalNodeParser(
            mutate_document_to_markdown=True,
            input_formats=[InputFormat.HTML, InputFormat.MD],
            format_options={
                InputFormat.HTML: FormatOption(
                    pipeline_cls=SimplePipeline,
                    backend=TrimmedHTMLDocumentBackend,
                ),
                InputFormat.MD: FormatOption(
                    pipeline_cls=SimplePipeline,
                    backend=GroupingMarkdownDocumentBackend,
                ),
            },
        )

        return IngestionPipeline(
            name="Docling Documentation Parser",
            transformations=[
                hierarchical_node_parser,
                RenameMetadata(renames={"file_path": "source", "file_name": "title"}),  # For Files
                RenameMetadata(renames={"url": "source"}),  # For Webpages
                IncludeMetadata(embed_keys=[], llm_keys=[]),
            ],
            # TODO https://github.com/run-llama/llama_index/issues/19277
            disable_cache=True,
        )

    async def _ingest_docs_factory(self, knowledge_base: str):
        """A worker pool for ingesting documents and nodes into the knowledge base."""

        knowledge_base_pipeline = await self.knowledge_base_client.new_knowledge_base_pipelines(knowledge_base=knowledge_base)

        ingest_result: IngestResult = IngestResult()

        async def ingest_docs_work_fn(documents: list[Document]) -> None:
            """Ingest HTML documents into the knowledge base."""

            docling_nodes = await self._docling_documentation_pipeline.arun(documents=documents)

            ingested_nodes = await knowledge_base_pipeline.arun(documents=documents, nodes=docling_nodes)

            _ = ingest_result.merge(
                other=IngestResult(
                    documents=len(documents),
                    parsed_nodes=len(docling_nodes),
                    ingested_nodes=len(ingested_nodes),
                )
            )

        return ingest_docs_work_fn, ingest_result

    async def load_website(
        self,
        context: Context,
        knowledge_base: NewKnowledgeBaseField,
        seed_urls: SeedPagesField,
        url_exclusions: URLExclusionsField = None,
        max_pages: MaxPagesField = None,
    ) -> IngestResult:
        """Create a new knowledge base from a website using seed URLs. If the knowledge base already exists, it will be replaced."""

        await self._log_info(context=context, message=f"Creating {knowledge_base} from {seed_urls}")

        reader = RecursiveAsyncWebReader(
            seed_urls=seed_urls,
            max_requests_per_crawl=max_pages or 1000,
            exclude_url_patterns=url_exclusions or [],
        )

        handle_docs, ingest_result = await self._ingest_docs_factory(knowledge_base=knowledge_base)

        async with worker_pool(pool_name="Website Ingest", work_function=handle_docs, workers=self.workers) as (work_queue, _):
            async for documents in achunk(async_iterable=reader.alazy_load_data(), size=3):
                document_names = [document.metadata.get("url") for document in documents]
                logger.info(f"Queuing {len(documents)} documents: {document_names} ({ingest_result.documents})")
                _ = await work_queue.put(item=documents)

        await self._log_info(
            context=context,
            message=f"Crawl for {knowledge_base} created {ingest_result.model_dump()} nodes",
        )

        return ingest_result

    async def load_directory(
        self,
        context: Context,
        knowledge_base: NewKnowledgeBaseField,
        path: DirectoryPathField,
        exclude: DirectoryExcludeField = None,
        extensions: DirectoryFilterExtensionsField = None,
        recursive: DirectoryRecursiveField = True,
    ) -> IngestResult:
        """Create a new knowledge base from a directory."""

        if extensions is None:
            extensions = [".md", ".ad", ".adoc", ".asc", ".asciidoc"]

        await self._log_info(context=context, message=f"Creating {knowledge_base} from {path} with {extensions} and {recursive}")

        reader = FastDirectoryReader(input_dir=path, required_exts=extensions, recursive=recursive, exclude=exclude)

        count = reader.count_files()

        handle_docs, ingest_result = await self._ingest_docs_factory(knowledge_base=knowledge_base)

        async with worker_pool(pool_name="Directory Ingest", work_function=handle_docs, workers=self.workers) as (work_queue, _):
            async for documents in achunk(async_iterable=reader.alazy_load_data(), size=3):
                document_names = [document.metadata.get("file_name") for document in documents]
                logger.info(f"Queuing {len(documents)} documents: {document_names} ({ingest_result.documents}/{count})")

                _ = await work_queue.put(item=documents)

            logger.info(f"Done queuing {work_queue.qsize()} documents to be processed")

        logger.info("Done with document processing")

        await self._log_info(
            context=context,
            message=f"Crawl for {knowledge_base} from {path} with {extensions} and recurse: {recursive} created {ingest_result.model_dump()} nodes",
        )

        return ingest_result

    async def load_git_repository(
        self,
        context: Context,
        knowledge_base: NewKnowledgeBaseField,
        repository_url: Annotated[str, Field(description="The URL of the git repository to clone.")],
        branch: Annotated[str, Field(description="The branch to clone.")],
        path: Annotated[str, Field(description="The path in the repository to ingest.")],
        exclude: DirectoryExcludeField = None,
        extensions: DirectoryFilterExtensionsField = None,
    ) -> IngestResult:
        """Create a new knowledge base from a git repository."""

        await self._log_info(
            context=context, message=f"Creating {knowledge_base} from {repository_url} at {path} with {extensions} and {exclude}"
        )

        if extensions is None:
            extensions = [".md", ".ad", ".adoc", ".asc", ".asciidoc"]

        with tempfile.TemporaryDirectory() as temp_dir:
            await self._log_info(context=context, message=f"Cloning {repository_url} to {temp_dir}")
            repo = Repo.clone_from(url=repository_url, to_path=temp_dir, depth=1, single_branch=True)
            _ = repo.git.checkout(branch)  # pyright: ignore[reportAny]
            await self._log_info(context=context, message=f"Done cloning {repository_url} to {temp_dir}")

            return await self.load_directory(
                context=context,
                knowledge_base=knowledge_base,
                path=temp_dir,
                extensions=extensions,
                recursive=True,
                exclude=exclude,
            )
