import time
from functools import cached_property
from logging import Logger
from typing import TYPE_CHECKING, Any, override

from fastmcp.server.server import FastMCP
from fastmcp.tools import Tool as FastMCPTool
from llama_index.core.postprocessor import SentenceTransformerRerank
from llama_index.core.postprocessor.types import BaseNodePostprocessor

from knowledge_base_mcp.llama_index.post_processors.flash_rerank import FlashRankRerank
from knowledge_base_mcp.llama_index.post_processors.get_parent_nodes import GetParentNodesPostprocessor
from knowledge_base_mcp.llama_index.post_processors.get_sibling_nodes import GetSiblingNodesPostprocessor
from knowledge_base_mcp.llama_index.post_processors.remove_duplicate_nodes import RemoveDuplicateNodesPostprocessor
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
    def get_search_tools(self) -> list[FastMCPTool]:
        """Get the search tools for the server."""
        return [
            FastMCPTool.from_function(fn=self.query),
        ]

    @override
    def as_search_server(self) -> FastMCP[Any]:
        """Convert the server to a FastMCP server."""

        mcp: FastMCP[Any] = FastMCP[Any](name=self.server_name)

        [mcp.add_tool(tool=tool) for tool in self.get_search_tools()]

        return mcp

    @override
    def result_post_processors(self) -> list[BaseNodePostprocessor]:
        # Bring in sibling nodes before reranking
        get_sibling_nodes_postprocessor = GetSiblingNodesPostprocessor(
            doc_store=self.knowledge_base_client.docstore,
        )

        rerank_nodes_postprocessor = self.knowledge_base_client.reranker

        # Replace child nodes with a parent node if we have enough of them
        get_parent_node_postprocessor = GetParentNodesPostprocessor(
            doc_store=self.knowledge_base_client.docstore,
            minimum_coverage=0.5,
            minimum_size=1024,
            maximum_size=4096,
            keep_child_nodes=False,
        )

        # Remove duplicate nodes
        duplicate_node_postprocessor = RemoveDuplicateNodesPostprocessor(
            by_id=True,
            by_hash=True,
        )

        return [
            duplicate_node_postprocessor,
            get_sibling_nodes_postprocessor,
            get_parent_node_postprocessor,
            duplicate_node_postprocessor,
            rerank_nodes_postprocessor,
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
