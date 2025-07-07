import asyncio
from collections.abc import AsyncIterator, Sequence
from contextlib import asynccontextmanager
from functools import cached_property
from logging import Logger
from typing import Annotated, ClassVar

from fastmcp import Context
from fastmcp.tools import Tool as FastMCPTool
from llama_index.core.ingestion.pipeline import IngestionPipeline
from llama_index.core.schema import BaseNode, Document, TransformComponent
from pydantic import ConfigDict, Field, PrivateAttr
from pydantic.main import BaseModel

from knowledge_base_mcp.clients.knowledge_base import KnowledgeBaseClient
from knowledge_base_mcp.llama_index.ingestion_pipelines.batching import PipelineGroup
from knowledge_base_mcp.llama_index.readers.web import RecursiveAsyncWebReader
from knowledge_base_mcp.llama_index.transformations.metadata import IncludeMetadata, RenameMetadata
from knowledge_base_mcp.utils.logging import BASE_LOGGER
from knowledge_base_mcp.utils.models import BaseKBModel
from knowledge_base_mcp.utils.timer import TimerGroup
from knowledge_base_mcp.utils.workers import batch_worker_pool, gather_results_from_queue, worker_pool


def docling_documentation_parser() -> TransformComponent:
    """A pipeline for parsing a webpage into a Docling document."""
    from docling.datamodel.base_models import InputFormat
    from docling.document_converter import FormatOption
    from docling.pipeline.simple_pipeline import SimplePipeline

    from knowledge_base_mcp.docling.html_backend import TrimmedHTMLDocumentBackend
    from knowledge_base_mcp.llama_index.hierarchical_node_parsers.docling_hierarchical_node_parser import DoclingHierarchicalNodeParser

    return DoclingHierarchicalNodeParser(
        mutate_document_to_markdown=True,
        input_formats=[InputFormat.HTML, InputFormat.MD],
        format_options={
            InputFormat.HTML: FormatOption(
                pipeline_cls=SimplePipeline,
                backend=TrimmedHTMLDocumentBackend,
            ),
        },
    )


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

    documents: int = Field(default=0, description="The number of documents ingested.")
    parsed_nodes: int = Field(default=0, description="The number of nodes ingested.")
    ingested_nodes: int = Field(default=0, description="The number of nodes ingested into the knowledge base.")
    timers: TimerGroup = Field(..., description="The timers for the ingestion operation.")

    def merge(self, other: "IngestResult") -> "IngestResult":
        """Merge two ingestion results."""
        return IngestResult(
            documents=self.documents + other.documents,
            parsed_nodes=self.parsed_nodes + other.parsed_nodes,
            ingested_nodes=self.ingested_nodes + other.ingested_nodes,
            timers=self.timers.merge(other=other.timers),
        )

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


class IngestQueues(BaseModel):
    """The queues for ingestion."""

    model_config: ClassVar[ConfigDict] = ConfigDict(arbitrary_types_allowed=True)

    documents_in: asyncio.Queue[Document] = Field(default_factory=asyncio.Queue)
    nodes_in: asyncio.Queue[Sequence[BaseNode]] = Field(default_factory=asyncio.Queue)

    results: asyncio.Queue[IngestResult] = Field(default_factory=asyncio.Queue)
    errors: asyncio.Queue[tuple[list[Document], Exception]] = Field(default_factory=asyncio.Queue)

    _documents_out: asyncio.Queue[Document] = PrivateAttr(default=asyncio.Queue())


class IngestServer(BaseKBModel):
    """A server for ingesting documentation."""

    knowledge_base_client: KnowledgeBaseClient

    workers: int = Field(default=4, description="The number of workers to use for ingestion.")

    def get_raw_tools(self) -> list[FastMCPTool]:
        return [
            FastMCPTool.from_function(fn=self.load_website),
            # FastMCPTool.from_function(fn=self.load_directory),
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

    @cached_property
    def _docling_documentation_pipeline_group(self) -> PipelineGroup:
        """A pipeline group for parsing a webpage into a Docling document."""
        return PipelineGroup(
            name="Docling Documentation Parser",
            pipelines=[
                self._docling_documentation_pipeline,
            ],
        )

    # async def _ingest_docs_and_nodes(
    #     self,
    #     documents: Sequence[Document],
    #     vector_store_pipeline: PipelineGroup,
    #     document_store_pipeline: PipelineGroup,
    # ) -> int:
    #     """Ingest documentation into a knowledge base."""

    #     node_count = 0

    #     tasks = [
    #         vector_store_pipeline.arun(nodes=nodes),
    #         document_store_pipeline.arun(documents=documents),
    #     ]

    #     async with self._semaphore:
    #         results = await asyncio.gather(*tasks)

    #     node_count += len(results)

    #     return node_count

    # async def _ingest_docs_work_fn_factory(
    #     self, knowledge_base: str
    # ) -> Callable[[list[tuple[list[Document], Sequence[BaseNode]]]], Coroutine[Any, Any, IngestResult]]:
    #     """A factory for creating worker functions that ingest documents into the knowledge base."""

    #     vector_store_pipeline, document_store_pipeline = await self.knowledge_base_client.new_knowledge_base(knowledge_base=knowledge_base)

    #     async def ingest_docs_work_fn(work: list[tuple[list[Document], Sequence[BaseNode]]]) -> IngestResult:
    #         """Ingest HTML documents into the knowledge base."""

    #         documents: list[Document] = []
    #         nodes: list[BaseNode] = []

    #         for documents_batch, nodes_batch in work:
    #             documents.extend(documents_batch)
    #             nodes.extend(nodes_batch)

    #         trimmed_nodes, vector_store_timers = await vector_store_pipeline.arun_with_timers(nodes=nodes)
    #         _, document_store_timers = await document_store_pipeline.arun_with_timers(documents=documents)

    #         combined_timers: TimerGroup = vector_store_timers.merge(other=document_store_timers)

    #         return IngestResult(node_count=len(trimmed_nodes), timers=combined_timers)

    #     return ingest_docs_work_fn

    @asynccontextmanager
    async def _ingest_docs(self, knowledge_base: str) -> AsyncIterator[IngestQueues]:
        """A worker pool for ingesting documents and nodes into the knowledge base."""

        vector_store_pipeline, document_store_pipeline = await self.knowledge_base_client.new_knowledge_base(knowledge_base=knowledge_base)

        ingest_queues: IngestQueues = IngestQueues(documents_in=asyncio.Queue(maxsize=4))

        async def parse_docs(document: Document) -> IngestResult:
            """Ingest HTML documents into the knowledge base."""

            nodes, timers = await self._docling_documentation_pipeline_group.arun_with_timers(documents=[document])

            result: IngestResult = IngestResult(documents=1, parsed_nodes=len(nodes), ingested_nodes=0, timers=timers)

            ingest_queues.nodes_in.put_nowait(item=nodes)
            ingest_queues._documents_out.put_nowait(item=document)  # pyright: ignore[reportPrivateUsage]

            return result

        async def publish_docs(documents: list[Document]) -> IngestResult:
            """Ingest HTML documents into the knowledge base."""

            _, document_store_timers = await document_store_pipeline.arun_with_timers(documents=documents)

            result: IngestResult = IngestResult(documents=len(documents), timers=document_store_timers)

            return result

        async def publish_nodes(batches_of_batches: Sequence[Sequence[BaseNode]]) -> IngestResult:
            """Ingest nodes into the knowledge base."""

            nodes: list[BaseNode] = [node for batch in batches_of_batches for node in batch]

            trimmed_nodes, vector_store_timers = await vector_store_pipeline.arun_with_timers(nodes=nodes)

            return IngestResult(documents=0, ingested_nodes=len(trimmed_nodes), timers=vector_store_timers)

        parse_docs_pool = worker_pool(
            work_type=Document,
            work_function=parse_docs,
            workers=2,
            work_queue=ingest_queues.documents_in,
            result_type=IngestResult,
            result_queue=ingest_queues.results,
        )

        publish_docs_pool = batch_worker_pool(
            work_type=Document,
            work_function=publish_docs,
            workers=1,
            result_type=IngestResult,
            work_queue=ingest_queues._documents_out,  # pyright: ignore[reportPrivateUsage]
            result_queue=ingest_queues.results,
            error_queue=ingest_queues.errors,
            minimum_cost=10,
        )

        publish_nodes_pool = batch_worker_pool(
            work_type=Sequence[BaseNode],
            work_function=publish_nodes,
            workers=self.workers,
            result_type=IngestResult,
            work_queue=ingest_queues.nodes_in,
            result_queue=ingest_queues.results,
            minimum_cost=250,
            cost_function=lambda nodes: len(nodes),
        )

        async with parse_docs_pool, publish_docs_pool, publish_nodes_pool:
            yield ingest_queues

            # The caller is trying to exit the context manager, so we need to join the queues
            # to ensure any work that is in the queues is processed.
            await ingest_queues.documents_in.join()
            ingest_queues.documents_in.shutdown()
            ingest_queues._documents_out.shutdown()
            ingest_queues.nodes_in.shutdown()

    async def load_website(
        self,
        context: Context,
        knowledge_base: NewKnowledgeBaseField,
        seed_urls: SeedPagesField,
        url_exclusions: URLExclusionsField = None,
        max_pages: MaxPagesField = None,
    ) -> None:
        """Create a new knowledge base from a website using seed URLs. If the knowledge base already exists, it will be replaced."""

        await self._log_info(context=context, message=f"Creating {knowledge_base} from {seed_urls}")

        reader = RecursiveAsyncWebReader(
            seed_urls=seed_urls,
            max_requests_per_crawl=max_pages or 1000,
            exclude_url_patterns=url_exclusions or [],
        )

        async with self._ingest_docs(knowledge_base=knowledge_base) as ingest_queues:
            async for documents in reader.alazy_load_data():
                await ingest_queues.documents_in.put(item=documents)

        results: list[IngestResult] = await gather_results_from_queue(queue=ingest_queues.results)

        merged_result: IngestResult = IngestResult.merge_results(results=results)

        await self._log_info(
            context=context,
            message=f"Crawl for {knowledge_base} has processed {merged_result.model_dump()} nodes",
        )

    # async def load_directory(
    #     self,
    #     context: Context,
    #     knowledge_base: NewKnowledgeBaseField,
    #     path: DirectoryPathField,
    #     extensions: DirectoryFilterExtensionsField = None,
    #     recursive: DirectoryRecursiveField = True,
    # ) -> None:
    #     """Create a new knowledge base from a directory."""

    #     if extensions is None:
    #         extensions = [".md", ".ad", ".adoc", ".asc", ".asciidoc"]

    #     await self._log_info(context=context, message=f"Creating {knowledge_base} from {path} with {extensions} and {recursive}")

    #     reader = SimpleDirectoryReader(input_dir=path, required_exts=extensions, recursive=recursive)

    #     pipeline_group: PipelineGroup = await self.knowledge_base_client.new_knowledge_base(
    #         knowledge_base=knowledge_base,
    #         pre_pipelines=[
    #             self._docling_documentation_pipeline,
    #         ],
    #     )

    #     node_count = 0

    #     for documents in chunk(iterable=reader.iter_data(), size=3):
    #         flattened_documents: list[Document] = [document for sublist in documents for document in sublist]
    #         nodes: Sequence[BaseNode] = await pipeline_group.arun(documents=flattened_documents)

    #         await self.knowledge_base_client.add_documents_to_knowledge_base(knowledge_base=knowledge_base, documents=flattened_documents)

    #         node_count += len(nodes)
    #         await self._log_info(context=context, message=f"Directory Crawl has processed {node_count} nodes")

    #     await self._log_info(
    #         context=context,
    #         message=f"Created {knowledge_base} from {path} with {extensions} and {recursive} with {node_count} nodes",
    #     )

    # async def _run_web_pipeline(self, reader: LazyAsyncReaderConfig, knowledge_base: str) -> int:
    #     extra_pipelines = [
    #         IngestionPipeline(
    #             name="Docling Subsequent Code Block or Table",
    #             transformations=[DoclingSubsequentCodeBlockOrTable(metadata_matching=["parent_headings", "heading", "knowledge_base"])],
    #             disable_cache=True,
    #         )
    #     ]

    #     vector_store_pipeline = self.new_push_to_vector_store_pipeline(extra_pipelines=extra_pipelines)
    #     docs_ingest_pipeline = self.new_docs_ingest_pipeline()

    #     async with vector_store_pipeline.start() as input_queue:
    #         async for document in reader.aread():
    #             nodes = await docs_ingest_pipeline.arun(documents=[document])

    #             for node in nodes:
    #                 node.metadata["knowledge_base"] = knowledge_base

    #             await input_queue.put(nodes)

    #     docs_ingest_pipeline.print_total_times()
    #     vector_store_pipeline.print_total_times()

    #     return vector_store_pipeline.stats.output_nodes

    # async def load_directory(
    #     self,
    #     knowledge_base: NewKnowledgeBaseName,
    #     directory: Directory,
    #     include_extensions: DirectoryIncludeExtensions | None = None,
    #     recursive: DirectoryRecursive = True,
    # ) -> int:
    #     """Create a new knowledge base from a directory."""

    #     if include_extensions is None:
    #         include_extensions = [".md", ".txt"]

    #     extra_pipelines = [
    #         IngestionPipeline(
    #             name="Docling Subsequent Code Block or Table",
    #             transformations=[DoclingSubsequentCodeBlockOrTable(metadata_matching=["parent_headings", "heading", "knowledge_base"])],
    #             disable_cache=True,
    #         )
    #     ]

    #     reader = SimpleDirectoryReader(input_dir=directory, required_exts=include_extensions, recursive=recursive)

    #     vector_store_pipeline = self.new_push_to_vector_store_pipeline(extra_pipelines=extra_pipelines)
    #     docs_ingest_pipeline = self.new_docs_ingest_pipeline()

    #     async with vector_store_pipeline.start() as input_queue:
    #         documents = await reader.aload_data(num_workers=2)

    #         for document in documents:
    #             file_path = document.metadata.get("file_path")
    #             logger.info(f"Processing: {file_path} ")
    #             nodes = await docs_ingest_pipeline.arun(documents=[document])

    #             for node in nodes:
    #                 node.metadata["knowledge_base"] = knowledge_base
    #                 node.metadata["source"] = file_path

    #             await input_queue.put(nodes)

    #     docs_ingest_pipeline.print_total_times()
    #     vector_store_pipeline.print_total_times()

    #     return vector_store_pipeline.stats.output_nodes
