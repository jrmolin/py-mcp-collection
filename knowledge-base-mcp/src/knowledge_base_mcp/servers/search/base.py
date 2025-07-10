from abc import ABC, abstractmethod
from logging import Logger
from typing import TYPE_CHECKING, Annotated, Any, ClassVar

from fastmcp import FastMCP
from fastmcp.tools import Tool as FastMCPTool
from llama_index.core.base.base_query_engine import BaseQueryEngine
from llama_index.core.base.base_retriever import BaseRetriever
from llama_index.core.bridge.pydantic import Field
from llama_index.core.llms import MockLLM
from llama_index.core.postprocessor.types import BaseNodePostprocessor
from llama_index.core.response_synthesizers.no_text import NoText
from llama_index.core.schema import NodeWithScore
from llama_index.core.vector_stores.types import MetadataFilters
from pydantic import BaseModel, ConfigDict

from knowledge_base_mcp.clients.knowledge_base import KnowledgeBaseClient
from knowledge_base_mcp.llama_index.post_processors.remove_duplicate_nodes import RemoveDuplicateNodesPostprocessor
from knowledge_base_mcp.llama_index.query_engine.timing_retriever_query_engine import TimingRetrieverQueryEngine
from knowledge_base_mcp.servers.base import BaseKnowledgeBaseServer
from knowledge_base_mcp.servers.models.documentation import (
    DocumentResponse,
    KnowledgeBaseSummary,
)
from knowledge_base_mcp.utils.logging import BASE_LOGGER

if TYPE_CHECKING:
    from llama_index.core.base.response.schema import RESPONSE_TYPE
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


class SearchResponse(BaseModel):
    """A response to a search query"""

    model_config: ClassVar[ConfigDict] = ConfigDict(arbitrary_types_allowed=True)

    query: QueryStringField
    summary: BaseModel
    results: BaseModel


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

    def retriever(self, knowledge_base: list[str] | str | None = None, top_k: int = 50) -> BaseRetriever:
        return self.knowledge_base_client.get_knowledge_base_retriever(
            knowledge_base_types=[self.knowledge_base_type], knowledge_base=knowledge_base, top_k=top_k
        )

    def result_post_processors(self) -> list[BaseNodePostprocessor]:
        post_processors: list[BaseNodePostprocessor] = []

        post_processors.append(RemoveDuplicateNodesPostprocessor(by_id=True, by_hash=True))

        return post_processors

    def result_query_engine(
        self, knowledge_base: list[str] | str | None = None, extra_filters: MetadataFilters | None = None, top_k: int = 50
    ) -> BaseQueryEngine:
        synthesizer: NoText = NoText(llm=MockLLM())

        post_processors: list[BaseNodePostprocessor] = self.result_post_processors()

        return TimingRetrieverQueryEngine(
            retriever=self.knowledge_base_client.get_knowledge_base_retriever(
                knowledge_base_types=[self.knowledge_base_type], knowledge_base=knowledge_base, extra_filters=extra_filters, top_k=top_k
            ),
            node_postprocessors=post_processors,
            response_synthesizer=synthesizer,
        )

    def summary_query_engine(self, knowledge_base: list[str] | str | None = None) -> BaseQueryEngine:
        synthesizer: NoText = NoText(llm=MockLLM())

        retriever: BaseRetriever = self.knowledge_base_client.get_knowledge_base_retriever(
            knowledge_base_types=[self.knowledge_base_type], knowledge_base=knowledge_base, top_k=500
        )

        return TimingRetrieverQueryEngine(
            retriever=retriever,
            response_synthesizer=synthesizer,
        )

    async def get_results(
        self,
        query: QueryStringField,
        knowledge_bases: QueryKnowledgeBasesField | None = None,
        extra_filters: MetadataFilters | None = None,
        count: int = 50,
    ) -> list[NodeWithScore]:
        """Get the results from the query engine"""
        response: RESPONSE_TYPE = await self.result_query_engine(
            knowledge_base=knowledge_bases, extra_filters=extra_filters, top_k=count
        ).aquery(query)

        return response.source_nodes[:count]

    # def format_results(self, results: list[NodeWithScore]) -> BaseModel: ...
    #     """Format the results"""

    #     # return TreeSearchResponse.from_nodes(nodes=results)

    async def get_summary(self, query: QueryStringField, knowledge_bases: QueryKnowledgeBasesField | None = None) -> KnowledgeBaseSummary:
        """Get the summary from the query engine"""
        response: RESPONSE_TYPE = await self.summary_query_engine(knowledge_base=knowledge_bases).aquery(query)

        return KnowledgeBaseSummary.from_nodes(response.source_nodes)

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
