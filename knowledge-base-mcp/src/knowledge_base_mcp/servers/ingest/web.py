import asyncio
from logging import Logger
from types import CoroutineType
from typing import TYPE_CHECKING, Annotated, Any, override

from fastmcp import Context
from fastmcp.tools import Tool as FastMCPTool
from pydantic import Field

from knowledge_base_mcp.llama_index.readers.web import RecursiveAsyncWebReader
from knowledge_base_mcp.servers.ingest.base import BaseIngestServer, IngestResult
from knowledge_base_mcp.utils.iterators import achunk
from knowledge_base_mcp.utils.logging import BASE_LOGGER
from knowledge_base_mcp.utils.patches import apply_patches

if TYPE_CHECKING:
    from types import CoroutineType

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
        description="The file extensions to gather. Defaults to AsciiDoc and Markdown",
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


class WebIngestServer(BaseIngestServer):
    """A server for ingesting documentation from a directory."""

    server_name: str = "Web Ingest Server"

    knowledge_base_type: str = "documentation"

    @override
    def get_ingest_tools(self) -> list[FastMCPTool]:
        return [
            FastMCPTool.from_function(fn=self.load_website),
        ]

    async def load_website(
        self,
        knowledge_base: NewKnowledgeBaseField,
        seed_urls: SeedPagesField,
        url_exclusions: URLExclusionsField = None,
        max_pages: MaxPagesField = None,
        background: bool = True,
        context: Context | None = None,
    ) -> IngestResult | None:
        """Create a new knowledge base from a website using seed URLs. If the knowledge base already exists, it will be replaced."""

        coro: CoroutineType[Any, Any, IngestResult] = self._load_website(
            context=context,
            knowledge_base=knowledge_base,
            seed_urls=seed_urls,
            url_exclusions=url_exclusions,
            max_pages=max_pages,
        )

        if background:
            self._background_tasks.append(asyncio.create_task(coro))
            return None

        return await coro

    async def _load_website(
        self,
        knowledge_base: NewKnowledgeBaseField,
        seed_urls: SeedPagesField,
        url_exclusions: URLExclusionsField = None,
        max_pages: MaxPagesField = None,
        context: Context | None = None,
    ) -> IngestResult:
        """Create a new knowledge base from a website using seed URLs. If the knowledge base already exists, it will be replaced."""

        await self._log_info(context=context, message=f"Creating {knowledge_base} from {seed_urls}")

        reader = RecursiveAsyncWebReader(
            seed_urls=seed_urls,
            max_requests_per_crawl=max_pages or 1000,
            exclude_url_patterns=url_exclusions or [],
        )

        async with self.start_rumbling(hierarchical=True) as (queue_nodes, queue_documents, ingest_result):
            async for documents in achunk(async_iterable=reader.alazy_load_data(), size=5):
                document_names = [document.metadata.get("url") for document in documents]

                logger.info(f"Queuing {len(documents)} documents: {document_names} ({ingest_result.documents})")

                for document in documents:
                    document.metadata["knowledge_base"] = knowledge_base
                    document.metadata["knowledge_base_type"] = self.knowledge_base_type

                    if nodes := await self.html_pipeline.arun(documents=[document]):
                        _ = await queue_nodes.send(item=nodes)
                        _ = await queue_documents.send(item=[document])

        await self._log_info(
            context=context,
            message=f"Crawl for KB: `{knowledge_base}` created {ingest_result.model_dump()} nodes in {ingest_result.duration()}s",
        )

        return ingest_result
