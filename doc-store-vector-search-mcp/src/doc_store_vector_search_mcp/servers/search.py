from fastmcp.contrib.mcp_mixin.mcp_mixin import MCPMixin, mcp_tool
from langchain_core.documents import Document
from pydantic import BaseModel

from doc_store_vector_search_mcp.etl.store import ProjectVectorStoreManager, SearchResult

from doc_store_vector_search_mcp.logging.util import BASE_LOGGER

logger = BASE_LOGGER.getChild("search")


# class SearchResult(BaseModel):
#     content: str
#     title: str
#     url: str
#     score: float

#     @classmethod
#     def from_document(cls, document: Document) -> "SearchResult":
#         return cls(
#             content=document.page_content,
#             title=document.metadata.get("title", "<no title>"),
#             url=document.metadata.get("url", "<no url>"),
#             score=document.metadata.get("_similarity_score", 0),
#         )

class SearchServer(MCPMixin):
    def __init__(self, project_name: str, project_vectorstore: ProjectVectorStoreManager):
        self.project_name = project_name
        self.project_vectorstore = project_vectorstore

    @mcp_tool()
    async def search_documents(self, query: str) -> list[SearchResult]:
        logger.info(f"Searching {self.project_name} documents for query: {query}")
        return await self.project_vectorstore.search_documents(query)

    # @mcp_tool()
    # async def search_code(self, query: str) -> list[SearchResult]:
    #     logger.info(f"Searching {self.project_name} code for query: {query}")
    #     return await self.project_vectorstore.search_code(query)
