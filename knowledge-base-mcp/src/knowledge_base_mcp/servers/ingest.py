from logging import Logger
from typing import TYPE_CHECKING, Annotated

from fastmcp import Context
from fastmcp.tools import Tool as FastMCPTool
from llama_index.core.ingestion.pipeline import IngestionPipeline
from llama_index.core.schema import TransformComponent
from pydantic import Field

from knowledge_base_mcp.clients.knowledge_base import KnowledgeBaseClient
from knowledge_base_mcp.llama_index.readers.web import RecursiveAsyncWebReader
from knowledge_base_mcp.llama_index.transformations.metadata import IncludeMetadata, RenameMetadata
from knowledge_base_mcp.utils.iterators import achunk
from knowledge_base_mcp.utils.logging import BASE_LOGGER
from knowledge_base_mcp.utils.models import BaseKBModel

if TYPE_CHECKING:
    from collections.abc import Sequence

    from llama_index.core.schema import BaseNode

    from knowledge_base_mcp.llama_index.ingestion_pipelines.batching import PipelineGroup


def docling_webpage_parser() -> TransformComponent:
    """A pipeline for parsing a webpage into a Docling document."""
    from docling.datamodel.base_models import InputFormat
    from docling.document_converter import FormatOption
    from docling.pipeline.simple_pipeline import SimplePipeline

    from knowledge_base_mcp.docling.html_backend import TrimmedHTMLDocumentBackend
    from knowledge_base_mcp.llama_index.hierarchical_node_parsers.docling_hierarchical_node_parser import DoclingHierarchicalNodeParser

    return DoclingHierarchicalNodeParser(
        mutate_document_to_markdown=True,
        collapse_nodes=True,
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


class IngestServer(BaseKBModel):
    """A server for ingesting documentation."""

    knowledge_base_client: KnowledgeBaseClient

    def get_raw_tools(self) -> list[FastMCPTool]:
        return [
            FastMCPTool.from_function(fn=self.load_website),
        ]

    async def _log_info(self, context: Context, message: str) -> None:
        await context.info(message=message)
        logger.info(msg=message)

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

        pipeline_group: PipelineGroup = await self.knowledge_base_client.new_knowledge_base(
            knowledge_base=knowledge_base,
            pre_pipelines=[
                IngestionPipeline(
                    name="Docling Webpage Parser",
                    transformations=[
                        docling_webpage_parser(),
                        RenameMetadata(renames={"url": "source"}),
                        IncludeMetadata(embed_keys=[], llm_keys=[]),
                    ],
                    # TODO https://github.com/run-llama/llama_index/issues/19277
                    disable_cache=True,
                )
            ],
        )

        node_count = 0

        async for documents in achunk(async_iterable=reader.alazy_load_data(), size=3):
            nodes: Sequence[BaseNode] = await pipeline_group.arun(documents=documents)

            await self.knowledge_base_client.add_documents_to_knowledge_base(knowledge_base=knowledge_base, documents=documents)

            node_count += len(nodes)
            await self._log_info(context=context, message=f"Website Crawl has processed {node_count} nodes")

        await self._log_info(
            context=context, message=f"Created {knowledge_base} from {seed_urls} with max {max_pages} pages and {node_count} nodes"
        )

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
