from logging import Logger


from typing import TYPE_CHECKING, override

from fastmcp.tools import Tool as FastMCPTool
from llama_index.core.postprocessor import SentenceTransformerRerank
from llama_index.core.postprocessor.types import BaseNodePostprocessor
import time

from knowledge_base_mcp.llama_index.post_processors.duplicate_node import DuplicateNodePostprocessor
from knowledge_base_mcp.llama_index.post_processors.parent_context import ParentContextNodePostprocessor
from knowledge_base_mcp.servers.models.documentation import (
    KnowledgeBaseSummary,
    SearchResponseWithSummary,
    TreeSearchResponse,
)
from knowledge_base_mcp.servers.search.base import BaseSearchServer, QueryKnowledgeBasesField, QueryStringField

from knowledge_base_mcp.utils.logging import BASE_LOGGER

logger: Logger = BASE_LOGGER.getChild(suffix="DocumentationSearchServer")

if TYPE_CHECKING:
    from llama_index.core.schema import NodeWithScore


class DocumentationSearchServer(BaseSearchServer):
    """A server for searching documentation."""

    server_name: str = "Documentation Search Server"

    knowledge_base_type: str = "documentation"

    reranker_model: str

    @override
    def get_tools(self) -> list[FastMCPTool]:
        """Get the tools for the server."""
        return [
            FastMCPTool.from_function(fn=self.query),
        ]

    @override
    def result_post_processors(self, result_count: int = 3) -> list[BaseNodePostprocessor]:
        reranker = SentenceTransformerRerank(model=self.reranker_model, top_n=result_count * 3)

        # Always bring in the parent node
        parent_context_postprocessor = ParentContextNodePostprocessor(
            doc_store=self.knowledge_base_client.docstore,
            threshold=0.0,
        )

        # Sometimes bring in the grandaprent node
        grandparent_context_postprocessor = ParentContextNodePostprocessor(
            doc_store=self.knowledge_base_client.docstore,
            threshold=0.5,
        )

        duplicate_node_postprocessor = DuplicateNodePostprocessor()

        return [
            #parent_context_postprocessor,
            duplicate_node_postprocessor,
            reranker,
            #grandparent_context_postprocessor,
            reranker,
            duplicate_node_postprocessor,
        ]

    async def query(self, query: QueryStringField, knowledge_bases: QueryKnowledgeBasesField | None = None) -> SearchResponseWithSummary:
        """Query the documentation"""

        start_time = time.perf_counter()
        raw_results: list[NodeWithScore] = await self.get_results(query, knowledge_bases=knowledge_bases)
        results: TreeSearchResponse = TreeSearchResponse.from_nodes(nodes=raw_results)
        results_time = time.perf_counter()

        summary: KnowledgeBaseSummary = await self.get_summary(query, knowledge_bases=knowledge_bases)

        summary_time = time.perf_counter()

        results_duration = results_time - start_time
        summary_duration = summary_time - results_time

        logger.info(f"Search took: {results_duration:.2f}s for results and {summary_duration:.2f}s for summary")

        return SearchResponseWithSummary(query=query, summary=summary, results=results)
