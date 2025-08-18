import os
from typing import override

from web_search_summary_mcp.clients.search.base import BaseSearchClient
from web_search_summary_mcp.clients.search.brave import BraveClient
from web_search_summary_mcp.models.search import SearchResponse


class AutoSearchClient(BaseSearchClient):
    client: BaseSearchClient

    def __init__(self):
        if os.getenv("BRAVE_API_KEY"):
            self.client = BraveClient(api_key=os.getenv("BRAVE_API_KEY"))
        else:
            msg = "Could not identify a search client"
            raise ValueError(msg)

    @override
    async def search(self, query: str, results: int = 5) -> SearchResponse:
        return await self.client.search(query, results=results)
