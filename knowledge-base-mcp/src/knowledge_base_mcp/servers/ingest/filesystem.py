import asyncio
import tempfile
from logging import Logger
from types import CoroutineType
from typing import TYPE_CHECKING, Annotated, Any, override

from fastmcp import Context
from fastmcp.tools import Tool as FastMCPTool
from git import Repo
from pydantic import Field

from knowledge_base_mcp.llama_index.readers.directory import FastDirectoryReader
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


class FilesystemIngestServer(BaseIngestServer):
    """A server for ingesting documentation from a directory."""

    server_name: str = "Directory Ingest Server"

    knowledge_base_type: str = "documentation"

    @override
    def get_ingest_tools(self) -> list[FastMCPTool]:
        return [
            FastMCPTool.from_function(fn=self.load_directory),
            FastMCPTool.from_function(fn=self.load_git_repository),
        ]

    async def load_directory(
        self,
        knowledge_base: NewKnowledgeBaseField,
        path: DirectoryPathField,
        exclude: DirectoryExcludeField = None,
        extensions: DirectoryFilterExtensionsField = None,
        recursive: DirectoryRecursiveField = True,
        background: bool = True,
        context: Context | None = None,
    ) -> IngestResult | None:
        """Create a new knowledge base from a directory."""

        coro: CoroutineType[Any, Any, IngestResult] = self._load_directory(
            context=context,
            knowledge_base=knowledge_base,
            path=path,
            exclude=exclude,
            extensions=extensions,
            recursive=recursive,
        )

        if background:
            self._background_tasks.append(asyncio.create_task(coro))
            return None

        return await coro

    async def _load_directory(
        self,
        knowledge_base: NewKnowledgeBaseField,
        path: DirectoryPathField,
        exclude: DirectoryExcludeField = None,
        extensions: DirectoryFilterExtensionsField = None,
        recursive: DirectoryRecursiveField = True,
        context: Context | None = None,
    ) -> IngestResult:
        """Create a new knowledge base from a directory."""

        if extensions is None:
            extensions = [".md", ".ad", ".adoc", ".asc", ".asciidoc"]

        log_msg = f"Creating {knowledge_base} from {path} with {extensions} and {recursive}"

        await self._log_info(context=context, message=log_msg)

        reader = FastDirectoryReader(input_dir=path, required_exts=extensions, recursive=recursive, exclude=exclude)

        async with self.start_rumbling(hierarchical=True) as (queue_nodes, queue_documents, ingest_result):
            async for documents in achunk(async_iterable=reader.alazy_load_data(), size=5):
                document_names = [document.metadata.get("file_name") for document in documents]

                logger.info(f"Queuing {len(documents)} documents: {document_names} ({ingest_result.documents})")

                for document in documents:
                    document.metadata["knowledge_base"] = knowledge_base
                    document.metadata["knowledge_base_type"] = self.knowledge_base_type

                    if nodes := await self.markdown_pipeline.arun(documents=[document]):
                        _ = await queue_nodes.send(item=nodes)
                        _ = await queue_documents.send(item=[document])

        await self._log_info(
            context=context,
            message=f"{log_msg} created {ingest_result.model_dump()} nodes in {ingest_result.duration()}s",
        )

        return ingest_result

    async def load_git_repository(
        self,
        knowledge_base: NewKnowledgeBaseField,
        repository_url: Annotated[str, Field(description="The URL of the git repository to clone.")],
        branch: Annotated[str, Field(description="The branch to clone.")],
        path: Annotated[str, Field(description="The path in the repository to ingest.")],
        background: bool = True,
        context: Context | None = None,
    ) -> IngestResult | None:
        """Create a new knowledge base from a git repository."""

        coro: CoroutineType[Any, Any, IngestResult] = self._load_git_repository(
            context=context,
            knowledge_base=knowledge_base,
            repository_url=repository_url,
            branch=branch,
            path=path,
        )

        if background:
            self._background_tasks.append(asyncio.create_task(coro))
            return None

        return await coro

    async def _load_git_repository(
        self,
        knowledge_base: NewKnowledgeBaseField,
        repository_url: Annotated[str, Field(description="The URL of the git repository to clone.")],
        branch: Annotated[str, Field(description="The branch to clone.")],
        path: Annotated[str, Field(description="The path in the repository to ingest.")],
        exclude: DirectoryExcludeField = None,
        extensions: DirectoryFilterExtensionsField = None,
        context: Context | None = None,
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

            return await self._load_directory(
                context=context,
                knowledge_base=knowledge_base,
                path=temp_dir,
                extensions=extensions,
                exclude=exclude,
                recursive=True,
            )
