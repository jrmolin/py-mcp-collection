from abc import ABC, abstractmethod

from web_search_summary_mcp.models.search import SearchResponse


class BaseSearchClient(ABC):
    @abstractmethod
    async def search(self, query: str, results: int = 5) -> SearchResponse: ...
