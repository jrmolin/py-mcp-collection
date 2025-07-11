from functools import cached_property
from logging import Logger
from typing import Any, override

from fastmcp.server.server import FastMCP
from fastmcp.tools import Tool as FastMCPTool
from llama_index.core.postprocessor.types import BaseNodePostprocessor
from pydantic import Field

from knowledge_base_mcp.llama_index.post_processors.get_parent_nodes import GetParentNodesPostprocessor
from knowledge_base_mcp.llama_index.post_processors.get_sibling_nodes import GetSiblingNodesPostprocessor
from knowledge_base_mcp.llama_index.post_processors.remove_duplicate_nodes import RemoveDuplicateNodesPostprocessor
from knowledge_base_mcp.servers.models.documentation import (
    TreeSearchResponse,
)
from knowledge_base_mcp.servers.search.base import (
    BaseSearchResponse,
    BaseSearchServer,
    QueryKnowledgeBasesField,
    QueryStringField,
    SearchResponse,
)
from knowledge_base_mcp.utils.logging import BASE_LOGGER
from knowledge_base_mcp.utils.patches import TimerGroup

logger: Logger = BASE_LOGGER.getChild(suffix="DocumentationSearchServer")


class DocumentationSearchResponse(BaseSearchResponse):
    """A response to a search query with a summary"""

    results: TreeSearchResponse = Field(description="The results of the search")


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

    @cached_property
    @override
    def result_post_processors(self) -> list[BaseNodePostprocessor]:
        # Bring in sibling nodes before reranking
        get_sibling_nodes_postprocessor = GetSiblingNodesPostprocessor(
            doc_store=self.knowledge_base_client.docstore,
            vector_store=self.knowledge_base_client.vector_store,  # pyright: ignore[reportArgumentType]
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

    @override
    async def query(
        self, query: QueryStringField, knowledge_bases: QueryKnowledgeBasesField | None = None, result_count: int = 20
    ) -> DocumentationSearchResponse:
        """Query the documentation"""
        timer_group: TimerGroup = TimerGroup(name="DocumentationSearchServer.query")

        with timer_group.time(name="fetch_results"):
            base_result: BaseSearchResponse = await super().query(query=query, knowledge_bases=knowledge_bases)

        if not isinstance(base_result, SearchResponse):
            msg = f"Expected a SearchResponse, got {type(base_result)}"
            raise TypeError(msg)

        nodes_with_scores = base_result.results.nodes_with_scores[: result_count * 2]

        with timer_group.time(name="apply_post_processors"):
            nodes_with_scores = await self.apply_post_processors(
                query=query,
                nodes_with_scores=nodes_with_scores,
                post_processors=self.result_post_processors,
            )

        logger.info(f"Query took: {timer_group.model_dump()}")

        nodes_with_scores = nodes_with_scores[:result_count]

        tree_search_response: TreeSearchResponse = TreeSearchResponse.from_nodes(nodes=nodes_with_scores)

        return DocumentationSearchResponse(query=query, summary=base_result.summary, results=tree_search_response)

    # async def query(self, query: QueryStringField, knowledge_bases: QueryKnowledgeBasesField | None = None) -> SearchResponseWithSummary:
    #     """Query the documentation"""

    #     start_time = time.perf_counter()
    #     raw_results: list[NodeWithScore] = await self.get_results(query, knowledge_bases=knowledge_bases, count=20)
    #     results: TreeSearchResponse = TreeSearchResponse.from_nodes(nodes=raw_results)
    #     results_time = time.perf_counter()

    #     summary: KnowledgeBaseSummary = await self.get_summary(query, knowledge_bases=knowledge_bases)

    #     summary_time = time.perf_counter()

    #     results_duration = results_time - start_time
    #     summary_duration = summary_time - results_time

    #     logger.info(f"Search took: {results_duration:.2f}s for results and {summary_duration:.2f}s for summary")

    #     return SearchResponseWithSummary(query=query, summary=summary, results=results)
