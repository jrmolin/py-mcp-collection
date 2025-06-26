from re import Pattern
from typing import Annotated

from llama_index.core.base.base_query_engine import BaseQueryEngine
from llama_index.core.base.base_retriever import BaseRetriever
from llama_index.core.base.embeddings.base import BaseEmbedding
from llama_index.core.indices.vector_store import VectorStoreIndex
from llama_index.core.readers.file.base import SimpleDirectoryReader
from llama_index.core.vector_stores.types import (
    FilterCondition,
    MetadataFilter,
    MetadataFilters,
)
from pydantic import BaseModel, ConfigDict, Field

from knowledge_base_mcp.llama_index.ingestion_pipelines.batching import (
    IngestionPipeline,
    LazyAsyncReaderConfig,
    PipelineGroup,
    QueuingPipelineGroup,
)
from knowledge_base_mcp.llama_index.node_parsers.semantic_merger import SemanticMergerNodeParser
from knowledge_base_mcp.llama_index.readers.async_web import RecursiveAsyncWebReader
from knowledge_base_mcp.llama_index.transformations.docling_subsequent_code_block_or_table import DoclingSubsequentCodeBlockOrTable
from knowledge_base_mcp.llama_index.transformations.metadata_trimmer import MetadataTrimmer
from knowledge_base_mcp.pipelines.docling import docling_pipeline_factory
from knowledge_base_mcp.pipelines.retrieval import retriever_query_engine, summary_query_engine
from knowledge_base_mcp.servers.models.documentation import KnowledgeBaseSummary, SearchResponseWithSummary, TreeSearchResponse
from knowledge_base_mcp.utils.logging import BASE_LOGGER
from knowledge_base_mcp.vector_stores.duckdb import EnhancedDuckDBVectorStore
from knowledge_base_mcp.vector_stores.elasticsearch import EnhancedElasticsearchStore

logger = BASE_LOGGER.getChild(__name__)


KNOWLEDGE_BASE_DESCRIPTION = "The name of the Knowledge Base to create to store this webpage."
KNOWLEDGE_BASE_EXAMPLES = ["Python Language - 3.12", "Python Library - Pydantic - 2.11", "Python Library - FastAPI - 0.115"]
NewKnowledgeBaseName = Annotated[str, Field(description=KNOWLEDGE_BASE_DESCRIPTION, examples=KNOWLEDGE_BASE_EXAMPLES)]

CRAWL_URLS_DESCRIPTION = """
The seed URLs to crawl and add to the knowledge base. Only child pages of the provided URLs will be crawled.
For example if the seed url is https://www.python.org/docs/3.12/, only the pages that start with
https://www.python.org/docs/3.12/ will be crawled.
"""
CRAWL_URLS_EXAMPLES = ["https://www.python.org/docs/3.12/"]
CrawlUrls = Annotated[list[str], Field(description=CRAWL_URLS_DESCRIPTION, examples=CRAWL_URLS_EXAMPLES, min_length=1, max_length=100)]

MAX_PAGES_DESCRIPTION = "The maximum number of pages to crawl."
MAX_PAGES_EXAMPLES = [1000]
MaxPages = Annotated[int, Field(description=MAX_PAGES_DESCRIPTION, examples=MAX_PAGES_EXAMPLES, ge=1, le=10000)]

RECURSE_DESCRIPTION = "Crawl the webpage recursively. By default, only child pages of the provided URLs will be crawled."
Recurse = Annotated[bool, Field(description=RECURSE_DESCRIPTION)]

BACKGROUND_DESCRIPTION = "Run the crawl in the background. If false, wait for the crawl to complete before returning a response."
Background = Annotated[bool, Field(description=BACKGROUND_DESCRIPTION)]

MINIMUM_NODE_BATCH_SIZE = 48

URL_EXCLUSIONS_DESCRIPTION = "The URLs to exclude from the crawl."
URL_EXCLUSIONS_EXAMPLES = ["https://www.python.org/docs/3.12/library/typing.html"]
URL_EXCLUSIONS_DEFAULTS = ["/changelog", "/releasenotes", "/release-notes", "/releases"]
URLExclusions = Annotated[
    list[str | Pattern],
    Field(default_factory=lambda: URL_EXCLUSIONS_DEFAULTS.copy(), description=URL_EXCLUSIONS_DESCRIPTION, examples=URL_EXCLUSIONS_EXAMPLES),
]

DIRECTORY_INCLUDE_EXTENSIONS_DESCRIPTION = "The file extensions to include in the knowledge base."
DIRECTORY_INCLUDE_EXTENSIONS_EXAMPLES = ["md", "txt", "py", "ipynb"]
DirectoryIncludeExtensions = Annotated[
    list[str],
    Field(
        description=DIRECTORY_INCLUDE_EXTENSIONS_DESCRIPTION, examples=DIRECTORY_INCLUDE_EXTENSIONS_EXAMPLES, min_length=1, max_length=100
    ),
]

DIRECTORY_RECURSIVE_DESCRIPTION = "Whether to recursively include files in the knowledge base."
DIRECTORY_RECURSIVE_EXAMPLES = [True]
DirectoryRecursive = Annotated[bool, Field(description=DIRECTORY_RECURSIVE_DESCRIPTION, examples=DIRECTORY_RECURSIVE_EXAMPLES)]

DIRECTORY_DESCRIPTION = "The directory to load into the knowledge base."
DIRECTORY_EXAMPLES = ["."]
Directory = Annotated[str, Field(description=DIRECTORY_DESCRIPTION, examples=DIRECTORY_EXAMPLES)]


SearchQuery = Annotated[
    str,
    Field(
        description="The plain language question to ask the Knowledge Base",
        examples=["What is the capital of France?", "Why did the French Revolution happen?"],
        min_length=1,
        max_length=1000,
    ),
]

KnowledgeBases = Annotated[
    list[str],
    Field(
        description="The knowledge bases to search",
        min_length=1,
        max_length=100,
    ),
]


class DocumentationServer(BaseModel):
    """A server for the documentation MCP."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    vector_store_index: VectorStoreIndex
    reranker_model: str
    embeddings_pipeline: IngestionPipeline
    vector_store_pipeline: IngestionPipeline

    @property
    def vector_store(self) -> EnhancedDuckDBVectorStore | EnhancedElasticsearchStore:
        if not isinstance(self.vector_store_index.vector_store, EnhancedDuckDBVectorStore | EnhancedElasticsearchStore):
            msg = "Vector store is not supported"
            raise TypeError(msg)

        return self.vector_store_index.vector_store

    @property
    def embed_model(self) -> BaseEmbedding:
        return self.vector_store_index._embed_model

    def new_retriever(self) -> BaseRetriever:
        return self.vector_store_index.as_retriever(similarity_top_k=100000)

    def query_engine(self, filters: MetadataFilters | None = None) -> BaseQueryEngine:
        return retriever_query_engine(
            result_count=3,
            reranker_model=self.reranker_model,
            vector_store_index=self.vector_store_index,
            filters=filters,
        )

    def summary_engine(self, filters: MetadataFilters | None = None) -> BaseQueryEngine:
        return summary_query_engine(
            vector_store_index=self.vector_store_index,
            filters=filters,
        )

    def new_push_to_vector_store_pipeline(self, extra_pipelines: list[IngestionPipeline] | None) -> QueuingPipelineGroup:
        metadata_exclusions = IngestionPipeline(
            name="Documentation Metadata Exclusions",
            transformations=[
                MetadataTrimmer(
                    exclude_metadata_keys=[
                        "parent_headings",
                        "heading",
                        "url",
                        "title",
                        "knowledge_base",
                        "docling_item_label",
                        "file_name",
                        "file_path",
                        "file_type",
                        "file_size",
                        "creation_date",
                        "last_modified_date",
                    ],
                )
            ],
            disable_cache=True,
        )

        semantic_merging_pipeline = IngestionPipeline(
            name="Semantic Merger",
            transformations=[
                SemanticMergerNodeParser(
                    embed_model=self.embed_model,
                    metadata_matching=["parent_headings", "heading", "url", "title", "knowledge_base", "docling_item_label"],
                ),
                SemanticMergerNodeParser(
                    embed_model=self.embed_model,
                    metadata_matching=["parent_headings", "url", "title", "knowledge_base", "docling_item_label"],
                ),
            ],
            disable_cache=True,
        )

        return QueuingPipelineGroup(
            name="to_vector_store",
            pipelines=[
                self.embeddings_pipeline,
                semantic_merging_pipeline,
                metadata_exclusions,
                *(extra_pipelines or []),
                self.vector_store_pipeline,
            ],
            batch_size=MINIMUM_NODE_BATCH_SIZE,
            workers=4,
        )

    def new_docs_ingest_pipeline(self) -> PipelineGroup:
        return docling_pipeline_factory()

    def _knowledge_base_filters(self, knowledge_bases: list[str] | str) -> MetadataFilters:
        if isinstance(knowledge_bases, str):
            return MetadataFilters(filters=[MetadataFilter(key="knowledge_base", value=knowledge_bases)])

        return MetadataFilters(
            condition=FilterCondition.OR, filters=[MetadataFilter(key="knowledge_base", value=kb) for kb in knowledge_bases]
        )

    def remove_knowledge_base(self, knowledge_base: str) -> str:
        """Remove a knowledge base from the vector store."""

        nodes = self.vector_store.get_nodes(filters=self._knowledge_base_filters(knowledge_base))

        self.vector_store_index.delete_nodes(node_ids=[node.node_id for node in nodes])

        return f"Knowledge base {knowledge_base} removed."

    def remove_all_knowledge_bases(self) -> str:
        """Remove all knowledge bases from the vector store."""

        self.vector_store_index.vector_store.clear()

        return "All knowledge bases removed"

    async def get_knowledge_bases(self) -> dict[str, int]:
        """Get all knowledge bases from the vector store."""

        return await self.vector_store.metadata_agg("knowledge_base")

    async def _get_summary(self, query: str, filters: MetadataFilters | None = None) -> KnowledgeBaseSummary:
        """Identify result counts across selected knowledge bases"""
        response = await self.summary_engine(filters).aquery(query)

        return KnowledgeBaseSummary.from_nodes(response.source_nodes)

    async def query(self, query: str) -> SearchResponseWithSummary:
        """Query all knowledge bases with a question."""
        response = await self.query_engine().aquery(query)

        summary = await self._get_summary(query)

        return SearchResponseWithSummary(
            query=query, summary=summary, results=TreeSearchResponse.from_nodes(query=query, nodes=response.source_nodes)
        )

    async def query_knowledge_bases(self, query: SearchQuery, knowledge_bases: KnowledgeBases) -> TreeSearchResponse:
        """Query specific knowledge bases with a question."""
        filters = self._knowledge_base_filters(knowledge_bases)

        response = await self.query_engine(filters=filters).aquery(query)

        return TreeSearchResponse.from_nodes(query=query, nodes=response.source_nodes)

    # @mcp_tool()
    # async def query_vector_store(self, metadata_key: str, metadata_value: str):
    #     """Get the reference document information"""
    #     vector_store_query = VectorStoreQuery(
    #         filters=MetadataFilters(
    #             filters=[
    #                 MetadataFilter(key=metadata_key, value=metadata_value),
    #             ],
    #         ),
    #     )
    #     return self.vector_store_index.vector_store.query(query=vector_store_query)

    # @mcp_tool()
    # async def load_webpage(self, knowledge_base: str, urls: list[str]):
    #     reader_pipeline = self.docling_pipeline.pipelines[0]

    #     total_nodes: int = 0

    #     async for batch in reader_pipeline.alazy_run():
    #         for node in batch:
    #             node.metadata["knowledge_base"] = knowledge_base

    #         nodes, timers = await self.to_vector_store_pipeline.arun_with_timers(nodes=batch)

    #         total_nodes += len(nodes) + len(batch)

    #         # logger.info(f"Loaded {len(nodes)} nodes from {urls} in {timers}")

    #     logger.info(f"Done loading {total_nodes} nodes from {urls}")

    async def load_website(
        self,
        knowledge_base: NewKnowledgeBaseName,
        seed_urls: CrawlUrls,
        url_exclusions: URLExclusions | None,
        max_pages: MaxPages = 1000,
    ) -> int:
        """Create a new knowledge base from a website using seed URLs. If the knowledge base already exists, it will be replaced.

        Returns:
            The number of nodes loaded into the knowledge base.
        """
        if url_exclusions is None:
            url_exclusions = []

        try:
            self.remove_knowledge_base(knowledge_base)
        except Exception as e:
            logger.warning(f"Error removing knowledge base {knowledge_base}: {e}")

        logger.info(f"Creating new knowledge base {knowledge_base} from {seed_urls} with max {max_pages} pages")

        reader = LazyAsyncReaderConfig(
            reader=RecursiveAsyncWebReader(
                seed_urls=seed_urls,
                max_requests_per_crawl=max_pages,
                exclude_url_patterns=url_exclusions,
            )
        )

        count = await self._run_web_pipeline(
            reader=reader,
            knowledge_base=knowledge_base,
        )

        logger.info(f"Done loading {count} nodes from {seed_urls} into {knowledge_base}")

        return count

    async def load_directory(
        self,
        knowledge_base: NewKnowledgeBaseName,
        directory: Directory,
        include_extensions: DirectoryIncludeExtensions | None = None,
        recursive: DirectoryRecursive = True,
    ) -> int:
        """Create a new knowledge base from a directory."""

        if include_extensions is None:
            include_extensions = [".md", ".txt"]

        extra_pipelines = [
            IngestionPipeline(
                name="Docling Subsequent Code Block or Table",
                transformations=[DoclingSubsequentCodeBlockOrTable(metadata_matching=["parent_headings", "heading", "knowledge_base"])],
                disable_cache=True,
            )
        ]

        reader = SimpleDirectoryReader(input_dir=directory, required_exts=include_extensions, recursive=recursive)

        vector_store_pipeline = self.new_push_to_vector_store_pipeline(extra_pipelines=extra_pipelines)
        docs_ingest_pipeline = self.new_docs_ingest_pipeline()

        async with vector_store_pipeline.start() as input_queue:
            documents = await reader.aload_data(num_workers=2)

            for document in documents:
                file_path = document.metadata.get("file_path")
                logger.info(f"Processing: {file_path} ")
                nodes = await docs_ingest_pipeline.arun(documents=[document])

                for node in nodes:
                    node.metadata["knowledge_base"] = knowledge_base
                    node.metadata["source"] = file_path

                await input_queue.put(nodes)

        docs_ingest_pipeline.print_total_times()
        vector_store_pipeline.print_total_times()

        return vector_store_pipeline.stats.output_nodes

    async def _run_web_pipeline(self, reader: LazyAsyncReaderConfig, knowledge_base: str) -> int:
        extra_pipelines = [
            IngestionPipeline(
                name="Docling Subsequent Code Block or Table",
                transformations=[DoclingSubsequentCodeBlockOrTable(metadata_matching=["parent_headings", "heading", "knowledge_base"])],
                disable_cache=True,
            )
        ]

        vector_store_pipeline = self.new_push_to_vector_store_pipeline(extra_pipelines=extra_pipelines)
        docs_ingest_pipeline = self.new_docs_ingest_pipeline()

        async with vector_store_pipeline.start() as input_queue:
            async for document in reader.aread():
                nodes = await docs_ingest_pipeline.arun(documents=[document])

                for node in nodes:
                    node.metadata["knowledge_base"] = knowledge_base

                await input_queue.put(nodes)

        docs_ingest_pipeline.print_total_times()
        vector_store_pipeline.print_total_times()

        return vector_store_pipeline.stats.output_nodes
