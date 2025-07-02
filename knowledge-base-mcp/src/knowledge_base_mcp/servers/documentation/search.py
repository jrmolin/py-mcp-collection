from logging import Logger
from typing import TYPE_CHECKING

from fastmcp.tools import Tool as FastMCPTool
from llama_index.core.base.base_query_engine import BaseQueryEngine
from llama_index.core.llms import MockLLM
from llama_index.core.postprocessor import SentenceTransformerRerank
from llama_index.core.query_engine.retriever_query_engine import RetrieverQueryEngine
from llama_index.core.response_synthesizers.no_text import NoText

from knowledge_base_mcp.clients.knowledge_base import KnowledgeBaseClient
from knowledge_base_mcp.llama_index.post_processors.duplicate_node import DuplicateNodePostprocessor
from knowledge_base_mcp.llama_index.post_processors.parent_context import ParentContextNodePostprocessor
from knowledge_base_mcp.servers.documentation.models.results import KnowledgeBaseSummary, SearchResponseWithSummary, TreeSearchResponse
from knowledge_base_mcp.utils.logging import BASE_LOGGER
from knowledge_base_mcp.utils.models import BaseKBModel

if TYPE_CHECKING:
    from llama_index.core.base.base_retriever import BaseRetriever

logger: Logger = BASE_LOGGER.getChild(suffix=__name__)


class KnowledgeBaseSearchServer(BaseKBModel):
    """A server for searching documentation."""

    knowledge_base_client: KnowledgeBaseClient
    reranker_model: str

    def get_raw_tools(self) -> list[FastMCPTool]:
        return [
            FastMCPTool.from_function(fn=self.query),
        ]

    # def _alt_query_engine(self, knowledge_base: list[str] | str | None = None, result_count: int = 5) -> BaseQueryEngine:
    #     synthesizer: NoText = NoText(llm=MockLLM())

    #     # storage_context: StorageContext = StorageContext.from_defaults(
    #     #     docstore=self.knowledge_base_client.vector_store_index.docstore,
    #     #     vector_store=self.knowledge_base_client.vector_store_index.vector_store,
    #     # )

    #     retriever: AutoMergingRetriever = AutoMergingRetriever(
    #         vector_retriever=self.knowledge_base_client.get_knowledge_base_retriever(knowledge_base=knowledge_base),
    #         storage_context=storage_context,
    #         simple_ratio_thresh=0.50,
    #     )

    #     reranker: SentenceTransformerRerank = SentenceTransformerRerank(model=self.reranker_model, top_n=result_count)

    #     return RetrieverQueryEngine(
    #         retriever=retriever,
    #         response_synthesizer=synthesizer,
    #         node_postprocessors=[
    #             reranker,
    #         ],
    #     )

    def _query_engine(self, knowledge_base: list[str] | str | None = None, result_count: int = 3) -> BaseQueryEngine:
        synthesizer = NoText(llm=MockLLM())

        # pre_rerank_expander = VectorPrevNextNodePostprocessor(
        #     vector_store=self.knowledge_base_client.vector_store_index.vector_store,
        #     num_nodes=5,
        #     mode="both",
        # )

        reranker = SentenceTransformerRerank(model=self.reranker_model, top_n=result_count * 3)

        parent_context_postprocessor = ParentContextNodePostprocessor(
            doc_store=self.knowledge_base_client.docstore,
            threshold=0.1,
        )

        duplicate_node_postprocessor = DuplicateNodePostprocessor()

        # post_rerank_expander = VectorPrevNextNodePostprocessor(
        #     vector_store=self.knowledge_base_client.vector_store_index.vector_store,
        #     num_nodes=1,
        #     mode="both",
        # )

        return RetrieverQueryEngine(
            retriever=self.knowledge_base_client.get_knowledge_base_retriever(knowledge_base=knowledge_base),
            node_postprocessors=[
                duplicate_node_postprocessor,
                reranker,
                parent_context_postprocessor,
                reranker,
                duplicate_node_postprocessor,
            ],
            response_synthesizer=synthesizer,
        )

    def _summary_query_engine(self, knowledge_base: list[str] | str | None = None) -> BaseQueryEngine:
        synthesizer: NoText = NoText(llm=MockLLM())

        retriever: BaseRetriever = self.knowledge_base_client.get_knowledge_base_retriever(knowledge_base=knowledge_base, top_k=1000)

        return RetrieverQueryEngine(
            retriever=retriever,
            response_synthesizer=synthesizer,
        )

    async def _get_summary(self, query: str, knowledge_base: list[str] | str | None = None) -> KnowledgeBaseSummary:
        """Identify result counts across selected knowledge bases"""
        response = await self._summary_query_engine(knowledge_base=knowledge_base).aquery(query)

        return KnowledgeBaseSummary.from_nodes(response.source_nodes)

    async def query(self, query: str, knowledge_base: list[str] | str | None = None) -> SearchResponseWithSummary:
        """Query all knowledge bases with a question."""
        # response = await self._query_engine(knowledge_base=knowledge_base).aquery(query)
        response = await self._query_engine(knowledge_base=knowledge_base).aquery(query)

        summary: KnowledgeBaseSummary = await self._get_summary(query, knowledge_base=None)

        return SearchResponseWithSummary(query=query, summary=summary, results=TreeSearchResponse.from_nodes(nodes=response.source_nodes))
