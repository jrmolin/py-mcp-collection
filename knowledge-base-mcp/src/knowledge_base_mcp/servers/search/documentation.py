# from logging import Logger
# from typing import TYPE_CHECKING, Annotated, ClassVar

# from fastmcp.tools import Tool as FastMCPTool
# from llama_index.core.base.base_query_engine import BaseQueryEngine
# from llama_index.core.base.response.schema import RESPONSE_TYPE
# from llama_index.core.bridge.pydantic import Field
# from llama_index.core.llms import MockLLM
# from llama_index.core.postprocessor import SentenceTransformerRerank
# from llama_index.core.query_engine.retriever_query_engine import RetrieverQueryEngine
# from llama_index.core.response_synthesizers.no_text import NoText
# from pydantic import BaseModel, ConfigDict

# from knowledge_base_mcp.clients.knowledge_base import KnowledgeBaseClient
# from knowledge_base_mcp.llama_index.post_processors.duplicate_node import DuplicateNodePostprocessor
# from knowledge_base_mcp.llama_index.post_processors.parent_context import ParentContextNodePostprocessor
# from knowledge_base_mcp.servers.models.documentation import (
#     DocumentResponse,
#     KnowledgeBaseSummary,
#     SearchResponseWithSummary,
#     TreeSearchResponse,
# )
# from knowledge_base_mcp.utils.logging import BASE_LOGGER

# if TYPE_CHECKING:
#     from llama_index.core.base.base_retriever import BaseRetriever
#     from llama_index.core.schema import BaseNode

# logger: Logger = BASE_LOGGER.getChild(suffix=__name__)


# QueryStringField = Annotated[
#     str,
#     Field(
#         description="The plain language query to search the knowledge base for.",
#         examples=["What is the Python Language?", "What is the FastAPI library?", "What is the Pydantic library?"],
#     ),
# ]


# QueryKnowledgeBasesField = Annotated[
#     list[str],
#     Field(
#         description="The optional name of the Knowledge Bases to restrict searches to. If not provided, searches all knowledge bases.",
#         examples=["Python Language - 3.12", "Python Library - Pydantic - 2.11", "Python Library - FastAPI - 0.115"],
#     ),
# ]

# DocumentKnowledgeBaseField = Annotated[
#     str,
#     Field(
#         description="The name of the Knowledge Base that the document belongs to.",
#         examples=["Python Language - 3.12", "Python Library - Pydantic - 2.11", "Python Library - FastAPI - 0.115"],
#     ),
# ]

# DocumentTitleField = Annotated[
#     str,
#     Field(
#         description="The title of the document to fetch. After running a general query, you may be interested in a specific document.",
#         examples=["doctest — Test interactive Python examples", "JSON Schema", "Name-based Virtual Host Support"],
#     ),
# ]


# class DocumentationSearchServer(BaseModel):
#     """A server for searching documentation."""

#     model_config: ClassVar[ConfigDict] = ConfigDict(arbitrary_types_allowed=True)

#     knowledge_base_client: KnowledgeBaseClient

#     reranker_model: str

#     def get_raw_tools(self) -> list[FastMCPTool]:
#         return [
#             FastMCPTool.from_function(fn=self.query),
#             FastMCPTool.from_function(fn=self.get_document),
#         ]

#     # def _alt_query_engine(self, knowledge_base: list[str] | str | None = None, result_count: int = 5) -> BaseQueryEngine:
#     #     synthesizer: NoText = NoText(llm=MockLLM())

#     #     # storage_context: StorageContext = StorageContext.from_defaults(
#     #     #     docstore=self.knowledge_base_client.vector_store_index.docstore,
#     #     #     vector_store=self.knowledge_base_client.vector_store_index.vector_store,
#     #     # )

#     #     retriever: AutoMergingRetriever = AutoMergingRetriever(
#     #         vector_retriever=self.knowledge_base_client.get_knowledge_base_retriever(knowledge_base=knowledge_base),
#     #         storage_context=storage_context,
#     #         simple_ratio_thresh=0.50,
#     #     )

#     #     reranker: SentenceTransformerRerank = SentenceTransformerRerank(model=self.reranker_model, top_n=result_count)

#     #     return RetrieverQueryEngine(
#     #         retriever=retriever,
#     #         response_synthesizer=synthesizer,
#     #         node_postprocessors=[
#     #             reranker,
#     #         ],
#     #     )

#     def _query_engine(
#         self, knowledge_base_types: list[str] | str | None = None, knowledge_base: list[str] | str | None = None, result_count: int = 3
#     ) -> BaseQueryEngine:
#         synthesizer = NoText(llm=MockLLM())

#         # pre_rerank_expander = VectorPrevNextNodePostprocessor(
#         #     vector_store=self.knowledge_base_client.vector_store_index.vector_store,
#         #     num_nodes=5,
#         #     mode="both",
#         # )

#         reranker = SentenceTransformerRerank(model=self.reranker_model, top_n=result_count * 3)

#         # Always bring in the parent node
#         parent_context_postprocessor = ParentContextNodePostprocessor(
#             doc_store=self.knowledge_base_client.docstore,
#             threshold=0.0,
#         )

#         # Sometimes bring in the grandaprent node
#         grandparent_context_postprocessor = ParentContextNodePostprocessor(
#             doc_store=self.knowledge_base_client.docstore,
#             threshold=0.5,
#         )

#         duplicate_node_postprocessor = DuplicateNodePostprocessor()

#         # post_rerank_expander = VectorPrevNextNodePostprocessor(
#         #     vector_store=self.knowledge_base_client.vector_store_index.vector_store,
#         #     num_nodes=1,
#         #     mode="both",
#         # )

#         return RetrieverQueryEngine(
#             retriever=self.knowledge_base_client.get_knowledge_base_retriever(
#                 knowledge_base_types=knowledge_base_types, knowledge_base=knowledge_base
#             ),
#             node_postprocessors=[
#                 parent_context_postprocessor,
#                 duplicate_node_postprocessor,
#                 reranker,
#                 grandparent_context_postprocessor,
#                 reranker,
#                 duplicate_node_postprocessor,
#             ],
#             response_synthesizer=synthesizer,
#         )

#     def _summary_query_engine(
#         self, knowledge_base_types: list[str] | str | None = None, knowledge_base: list[str] | str | None = None
#     ) -> BaseQueryEngine:
#         synthesizer: NoText = NoText(llm=MockLLM())

#         retriever: BaseRetriever = self.knowledge_base_client.get_knowledge_base_retriever(
#             knowledge_base_types=knowledge_base_types, knowledge_base=knowledge_base, top_k=1000
#         )

#         return RetrieverQueryEngine(
#             retriever=retriever,
#             response_synthesizer=synthesizer,
#         )

#     async def _get_summary(
#         self, query: str, knowledge_base_types: list[str] | str | None = None, knowledge_base: list[str] | str | None = None
#     ) -> KnowledgeBaseSummary:
#         """Identify result counts across selected knowledge bases"""
#         response: RESPONSE_TYPE = await self._summary_query_engine(
#             knowledge_base_types=knowledge_base_types, knowledge_base=knowledge_base
#         ).aquery(query)

#         return KnowledgeBaseSummary.from_nodes(response.source_nodes)

#     async def get_document(self, knowledge_base: DocumentKnowledgeBaseField, title: DocumentTitleField) -> DocumentResponse:
#         """Get a document from the knowledge base"""
#         document: BaseNode = await self.knowledge_base_client.get_document(knowledge_base=knowledge_base, title=title)
#         return DocumentResponse.from_node(node=document)

#     async def query(self, query: QueryStringField, knowledge_bases: QueryKnowledgeBasesField | None = None) -> SearchResponseWithSummary:
#         """Query all knowledge bases with a question."""
#         # response = await self._query_engine(knowledge_base=knowledge_base).aquery(query)
#         logger.info(f"Querying {knowledge_bases} with {query}")
#         response = await self._query_engine(knowledge_base_types=knowledge_bases, knowledge_base=None).aquery(query)

#         logger.info(f"Producing a summary for query {query}")

#         summary: KnowledgeBaseSummary = await self._get_summary(query, knowledge_base_types=knowledge_bases, knowledge_base=None)

#         logger.info(f"Returning {len(response.source_nodes)} results for query {query}")

#         return SearchResponseWithSummary(query=query, summary=summary, results=TreeSearchResponse.from_nodes(nodes=response.source_nodes))
