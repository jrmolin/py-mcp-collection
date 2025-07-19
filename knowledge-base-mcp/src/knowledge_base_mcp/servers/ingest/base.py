import asyncio
import datetime
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator, Sequence
from contextlib import asynccontextmanager
from logging import Logger
from typing import Any

from anyio import ClosedResourceError, EndOfStream, create_memory_object_stream, create_task_group
from anyio.streams.memory import MemoryObjectReceiveStream, MemoryObjectSendStream
from fastmcp import Context, FastMCP
from fastmcp.tools import Tool as FastMCPTool
from llama_index.core.ingestion.pipeline import IngestionPipeline
from llama_index.core.schema import BaseNode, Document
from pydantic import Field, PrivateAttr
from pydantic.main import BaseModel

from knowledge_base_mcp.docling.md_backend import GroupingMarkdownDocumentBackend
from knowledge_base_mcp.llama_index.transformations.metadata import IncludeMetadata, RenameMetadata
from knowledge_base_mcp.servers.base import BaseKnowledgeBaseServer
from knowledge_base_mcp.utils.logging import BASE_LOGGER
from knowledge_base_mcp.utils.patches import apply_patches

apply_patches()


logger: Logger = BASE_LOGGER.getChild(suffix=__name__)


class IngestResult(BaseModel):
    """The result of an ingestion operation."""

    start_time: datetime.datetime = Field(default_factory=datetime.datetime.now, exclude=True)

    documents: int = Field(default=0, description="The number of documents ingested.")
    parsed_nodes: int = Field(default=0, description="The number of nodes ingested.")
    ingested_nodes: int = Field(default=0, description="The number of nodes ingested into the knowledge base.")
    errors: int = Field(default=0, description="The number of errors encountered while ingesting.")

    last_update: datetime.datetime = Field(default_factory=datetime.datetime.now, exclude=True)

    def merge(self, other: "IngestResult") -> "IngestResult":
        """Merge two ingestion results."""
        self.documents += other.documents
        self.parsed_nodes += other.parsed_nodes
        self.ingested_nodes += other.ingested_nodes
        self.errors += other.errors
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


class BaseIngestServer(BaseKnowledgeBaseServer, ABC):
    """A server for ingesting documentation."""

    workers: int = Field(default=4, description="The number of workers to use for ingestion.")

    knowledge_base_type: str

    _background_tasks: list[asyncio.Task[IngestResult]] = PrivateAttr(default_factory=list)

    @abstractmethod
    def get_ingest_tools(self) -> list[FastMCPTool]: ...

    def as_ingest_server(self) -> FastMCP[Any]:
        """Convert the server to a FastMCP server."""

        mcp: FastMCP[Any] = FastMCP[Any](name=self.server_name)

        [mcp.add_tool(tool=tool) for tool in self.get_ingest_tools()]

        return mcp

    async def _pipeline_worker(
        self,
        worker_id: int,
        pipeline: IngestionPipeline,
        batch_size: int,
        receive_stream: MemoryObjectReceiveStream[Sequence[BaseNode]],
        ingest_result: IngestResult,
    ) -> None:
        """A pipeline worker that processes nodes from a receive stream."""

        preamble = f"{pipeline.name} ({worker_id})"
        logger.info(f"{preamble} Starting...")

        async def _process_batch(batch_of_nodes: Sequence[BaseNode]) -> None:
            """Process a batch of nodes."""
            try:
                nodes = await pipeline.arun(nodes=batch_of_nodes)
            except Exception:
                logger.exception(f"{preamble} Received an unknown error while processing batch.")
                ingest_result.errors += 1
                return

            ingest_result.documents += len([node for node in nodes if isinstance(node, Document)])
            ingest_result.parsed_nodes += len([node for node in nodes if not isinstance(node, Document)])
            ingest_result.ingested_nodes += len(nodes)

        nodes_to_process: Sequence[BaseNode] = []

        async with receive_stream:
            try:
                async for item in receive_stream:
                    if len(item) == 0:
                        continue

                    nodes_to_process.extend(item)

                    if len(nodes_to_process) >= batch_size:
                        _ = await _process_batch(batch_of_nodes=nodes_to_process)
                        nodes_to_process.clear()

            except (EndOfStream, ClosedResourceError):
                logger.debug(f"{preamble} Received end of stream. Exiting.")

            except Exception:
                logger.exception(f"{preamble} Received an unknown error")

        if len(nodes_to_process) > 0:
            logger.debug(f"{preamble} Received end of stream. Flushing final batch.")
            _ = await _process_batch(batch_of_nodes=nodes_to_process)
            nodes_to_process.clear()

        logger.info(f"{preamble} Done.")

    @asynccontextmanager
    async def start_rumbling(
        self,
        hierarchical: bool = False,
    ) -> AsyncIterator[tuple[MemoryObjectSendStream[Sequence[BaseNode]], MemoryObjectSendStream[Sequence[Document]], IngestResult]]:
        """Start the rumbling process."""

        ingest_result: IngestResult = IngestResult()

        queue_nodes, process_queued_nodes = create_memory_object_stream[Sequence[BaseNode]](max_buffer_size=16)  # In Batches
        queue_documents, process_queued_documents = create_memory_object_stream[Sequence[Document]](
            max_buffer_size=256
        )  # This is a sequence but we will generally be passed sequences with 1 document in them

        async with create_task_group() as tg:
            for i in range(2):
                tg.start_soon(
                    self._pipeline_worker,
                    i,
                    self.knowledge_base_client.hierarchical_node_to_knowledge_base_pipeline
                    if hierarchical
                    else self.knowledge_base_client.node_to_knowledge_base_pipeline,
                    256,
                    process_queued_nodes,
                    ingest_result,
                    name=f"send_nodes_to_vector_store_{i}",
                )
                tg.start_soon(
                    self._pipeline_worker,
                    i,
                    self.knowledge_base_client.document_to_knowledge_base_pipeline,
                    16,
                    process_queued_documents,
                    ingest_result,
                    name=f"send_documents_to_docstore_{i}",
                )

            yield queue_nodes, queue_documents, ingest_result

            # The caller is exiting the context manager, so we need to close the sending queue
            await queue_nodes.aclose()
            await queue_documents.aclose()

    async def _log_info(self, context: Context | None, message: str) -> None:
        if context is not None:
            await context.info(message=message)
        logger.info(msg=message)

    @property
    def markdown_pipeline(self) -> IngestionPipeline:
        """A pipeline for parsing a webpage into a Docling document."""
        from docling.datamodel.base_models import InputFormat
        from docling.document_converter import FormatOption
        from docling.pipeline.simple_pipeline import SimplePipeline

        from knowledge_base_mcp.docling.html_backend import TrimmedHTMLDocumentBackend
        from knowledge_base_mcp.llama_index.hierarchical_node_parsers.docling_hierarchical_node_parser import DoclingHierarchicalNodeParser

        docling_hierarchical_node_parser: DoclingHierarchicalNodeParser = DoclingHierarchicalNodeParser(
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
                docling_hierarchical_node_parser,
                RenameMetadata(renames={"file_path": "source", "file_name": "title"}),  # For Files
                RenameMetadata(renames={"url": "source"}),  # For Webpages
                IncludeMetadata(embed_keys=[], llm_keys=[]),
                self.knowledge_base_client.duplicate_document_checker,
            ],
            # TODO https://github.com/run-llama/llama_index/issues/19277
            disable_cache=True,
        )

    @property
    def html_pipeline(self) -> IngestionPipeline:
        return self.markdown_pipeline

    async def get_completed_tasks(self) -> dict[str, Any]:
        """Get all completed tasks."""
        running = [task for task in self._background_tasks if not task.done()]
        completed = [task for task in self._background_tasks if task.done()]
        results = [task.result().model_dump() for task in completed]

        self._background_tasks = running

        logger.info(f"Running tasks: {len(running)}, Completed tasks: {len(completed)}")

        return {
            "running": len(running),
            "completed": len(completed),
            "results": results,
        }
