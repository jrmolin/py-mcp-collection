from abc import ABC, abstractmethod
from functools import cached_property
from logging import Logger
from typing import TYPE_CHECKING, Annotated, Any, ClassVar

from fastmcp import FastMCP
from fastmcp.tools import Tool as FastMCPTool
from llama_index.core.bridge.pydantic import Field
from llama_index.core.postprocessor.types import BaseNodePostprocessor
from llama_index.core.schema import NodeWithScore
from pydantic import BaseModel, ConfigDict
from pydantic.root_model import RootModel

from knowledge_base_mcp.clients.knowledge_base import KnowledgeBaseClient
from knowledge_base_mcp.servers.base import BaseKnowledgeBaseServer
from knowledge_base_mcp.servers.models.documentation import (
    DocumentResponse,
)
from knowledge_base_mcp.utils.logging import BASE_LOGGER
from knowledge_base_mcp.utils.patches import TimerGroup

if TYPE_CHECKING:
    from llama_index.core.schema import BaseNode

logger: Logger = BASE_LOGGER.getChild(suffix=__name__)


QueryStringField = Annotated[
    str,
    Field(
        description="The plain language query to search the knowledge base for.",
        examples=["What is the Python Language?", "What is the FastAPI library?", "What is the Pydantic library?"],
    ),
]


QueryKnowledgeBasesField = Annotated[
    list[str],
    Field(
        description="The optional name of the Knowledge Bases to restrict searches to. If not provided, searches all knowledge bases.",
        examples=["Python Language - 3.12", "Python Library - Pydantic - 2.11", "Python Library - FastAPI - 0.115"],
    ),
]

DocumentKnowledgeBaseField = Annotated[
    str,
    Field(
        description="The name of the Knowledge Base that the document belongs to.",
        examples=["Python Language - 3.12", "Python Library - Pydantic - 2.11", "Python Library - FastAPI - 0.115"],
    ),
]

DocumentTitleField = Annotated[
    str,
    Field(
        description="The title of the document to fetch. After running a general query, you may be interested in a specific document.",
        examples=["doctest — Test interactive Python examples", "JSON Schema", "Name-based Virtual Host Support"],
    ),
]


class BaseSummaryResult(RootModel[dict[str, int]]):
    """A high level summary of relevant documents across all knowledge bases"""

    root: dict[str, int] = Field(default_factory=dict, description="The number of documents in each knowledge base")

    @classmethod
    def from_nodes(cls, nodes: list[NodeWithScore]) -> "BaseSummaryResult":
        """Convert a list of nodes to a summary"""
        results: dict[str, int] = {}

        for node in nodes:
            knowledge_base: str | None = node.node.metadata.get("knowledge_base")

            if knowledge_base is None:
                logger.warning(f"Retrieved Node {node.node_id} has no knowledge base")
                continue

            results[knowledge_base] = results.get(knowledge_base, 0) + 1

        return cls(root=results)


class BaseSearchResult(BaseModel):
    """A result from a search query"""

    nodes_with_scores: list[NodeWithScore]


class BaseSearchResponse(BaseModel):
    """A base class for responses to a search query"""

    query: QueryStringField
    summary: BaseSummaryResult


class SearchResponse(BaseSearchResponse):
    """A response to a search query that includes a simple list of results"""

    results: BaseSearchResult


# class SearchResponse(BaseModel):
#     """A response to a search query"""

#     model_config: ClassVar[ConfigDict] = ConfigDict(arbitrary_types_allowed=True)

#     query: QueryStringField
#     summary: BaseModel
#     results: BaseModel


class BaseSearchServer(BaseKnowledgeBaseServer, ABC):
    """A server for searching documentation."""

    model_config: ClassVar[ConfigDict] = ConfigDict(arbitrary_types_allowed=True)

    knowledge_base_client: KnowledgeBaseClient

    knowledge_base_type: str

    @abstractmethod
    def get_search_tools(self) -> list[FastMCPTool]: ...

    def as_search_server(self) -> FastMCP[Any]:
        """Convert the server to a FastMCP server."""

        mcp: FastMCP[Any] = FastMCP[Any](name=self.server_name)

        [mcp.add_tool(tool=tool) for tool in self.get_search_tools()]

        return mcp

    async def get_document(self, knowledge_base: DocumentKnowledgeBaseField, title: DocumentTitleField) -> DocumentResponse:
        """Get a document from the knowledge base"""

        document: BaseNode = await self.knowledge_base_client.get_document(
            knowledge_base_type=self.knowledge_base_type, knowledge_base=knowledge_base, title=title
        )

        return DocumentResponse.from_node(node=document)

    # def retriever(self, knowledge_base: list[str] | str | None = None, top_k: int = 50) -> BaseRetriever:
    #     return self.knowledge_base_client.get_knowledge_base_retriever(
    #         knowledge_base_types=[self.knowledge_base_type], knowledge_base=knowledge_base, top_k=top_k
    #     )

    @cached_property
    @abstractmethod
    def result_post_processors(self) -> list[BaseNodePostprocessor]: ...

    # def result_query_engine(
    #     self, knowledge_base: list[str] | str | None = None, extra_filters: MetadataFilters | None = None, top_k: int = 50
    # ) -> BaseQueryEngine:
    #     synthesizer: NoText = NoText(llm=MockLLM())

    #     post_processors: list[BaseNodePostprocessor] = self.result_post_processors()

    #     return TimingRetrieverQueryEngine(
    #         retriever=self.knowledge_base_client.get_knowledge_base_retriever(
    #             knowledge_base_types=[self.knowledge_base_type], knowledge_base=knowledge_base, extra_filters=extra_filters, top_k=top_k
    #         ),
    #         node_postprocessors=post_processors,
    #         response_synthesizer=synthesizer,
    #     )

    # def summary_query_engine(self, knowledge_base: list[str] | str | None = None) -> BaseQueryEngine:
    #     synthesizer: NoText = NoText(llm=MockLLM())

    #     retriever: BaseRetriever = self.knowledge_base_client.get_knowledge_base_retriever(
    #         knowledge_base_types=[self.knowledge_base_type], knowledge_base=knowledge_base, top_k=500
    #     )

    #     return TimingRetrieverQueryEngine(
    #         retriever=retriever,
    #         response_synthesizer=synthesizer,
    #     )

    @classmethod
    async def apply_post_processors(
        cls, query: str, nodes_with_scores: list[NodeWithScore], post_processors: list[BaseNodePostprocessor]
    ) -> list[NodeWithScore]:
        """Apply the post processors to the nodes"""
        processed_nodes: list[NodeWithScore] = nodes_with_scores.copy()

        timer_group: TimerGroup = TimerGroup(name="BaseSearchServer.apply_post_processors")

        for post_processor in post_processors:
            start_node_count: int = len(processed_nodes)

            with timer_group.time(name=f"{post_processor.__class__.__name__} with {start_node_count} nodes"):
                processed_nodes = await post_processor.apostprocess_nodes(nodes=processed_nodes, query_str=query)

        logger.info(f"Post processors took: {timer_group}s")

        return processed_nodes

    @classmethod
    def format_summary(cls, nodes_with_scores: list[NodeWithScore]):
        """Format the summary"""
        return BaseSummaryResult.from_nodes(nodes=nodes_with_scores)

    @classmethod
    def format_results(cls, nodes_with_scores: list[NodeWithScore]) -> BaseSearchResult:
        """Format the results"""
        return BaseSearchResult(nodes_with_scores=nodes_with_scores)

    async def query(
        self, query: QueryStringField, knowledge_bases: QueryKnowledgeBasesField | None = None, result_count: int = 200
    ) -> BaseSearchResponse:
        """Query the knowledge base"""

        nodes_with_scores: list[NodeWithScore] = await self.knowledge_base_client.aretrieve(
            query=query, knowledge_base=knowledge_bases, top_k=result_count
        )

        summary: BaseSummaryResult = self.format_summary(nodes_with_scores=nodes_with_scores)

        # processed_nodes: list[NodeWithScore] = await self.apply_post_processors(
        #     query=query,
        #     nodes_with_scores=nodes_with_scores,
        #     post_processors=self.result_post_processors,
        # )

        result: BaseSearchResult = self.format_results(nodes_with_scores=nodes_with_scores)

        return SearchResponse(query=query, summary=summary, results=result)

    # async def get_results(
    #     self,
    #     query: QueryStringField,
    #     knowledge_bases: QueryKnowledgeBasesField | None = None,
    #     extra_filters: MetadataFilters | None = None,
    #     count: int = 50,
    # ) -> list[NodeWithScore]:
    #     """Get the results from the query engine"""
    #     response: RESPONSE_TYPE = await self.result_query_engine(
    #         knowledge_base=knowledge_bases, extra_filters=extra_filters, top_k=count
    #     ).aquery(query)

    #     return response.source_nodes[:count]

    # # def format_results(self, results: list[NodeWithScore]) -> BaseModel: ...
    # #     """Format the results"""

    # #     # return TreeSearchResponse.from_nodes(nodes=results)

    # async def get_summary(self, query: QueryStringField, knowledge_bases: QueryKnowledgeBasesField | None = None) -> KnowledgeBaseSummary:
    #     """Get the summary from the query engine"""
    #     response: RESPONSE_TYPE = await self.summary_query_engine(knowledge_base=knowledge_bases).aquery(query)

    #     return KnowledgeBaseSummary.from_nodes(response.source_nodes)

    # def format_search_response(self, query: QueryStringField, raw_results: list[NodeWithScore], summary: BaseModel): ...

    #     # formatted_results: BaseModel = self.format_results(results=raw_results)

    #     # return SearchResponse(query=query, summary=summary, results=formatted_results)

    # @abstractmethod
    # async def query(self, query: QueryStringField, knowledge_bases: QueryKnowledgeBasesField | None = None):
    #     """Query all knowledge bases with a question."""
    #     # logger.info(f"Querying {knowledge_bases} with {query}")

    #     # raw_results = await self.get_results(query, knowledge_bases=knowledge_bases)

    #     # summary: BaseModel = await self.get_summary(query, knowledge_bases=knowledge_bases)

    #     # return self.format_search_response(query=query, raw_results=raw_results, summary=summary)
