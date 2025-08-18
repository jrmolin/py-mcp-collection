import asyncio
import os
from typing import Literal

from aiohttp import ClientResponseError, ClientSession
from aiohttp.web_exceptions import HTTPTooManyRequests
from pydantic import BaseModel

from web_search_summary_mcp.clients.search.base import BaseSearchClient
from web_search_summary_mcp.models.search import SearchResponse, SearchResult


class BraveSearchResultProfile(BaseModel):
    name: str
    url: str
    long_name: str
    img: str


class BraveSearchResult(BaseModel):
    title: str
    url: str
    is_source_local: bool
    is_source_both: bool
    description: str
    profile: BraveSearchResultProfile

    def to_search_result(self) -> SearchResult:
        return SearchResult(
            title=self.title,
            url=self.url,
            snippet=self.description,
        )


class BraveSearchResults(BaseModel):
    results: list[BraveSearchResult]


class BraveSearchResponse(BaseModel):
    type: Literal["search"]
    web: BraveSearchResults

    def to_search_response(self) -> SearchResponse:
        return SearchResponse(
            results=[result.to_search_result() for result in self.web.results],
        )


class BraveClient(BaseSearchClient):
    session: ClientSession | None

    def __init__(self, api_key: str | None = None, session: ClientSession | None = None):
        if not (brave_api_key := api_key or os.getenv("BRAVE_API_KEY")):
            msg = "BRAVE_API_KEY is not set"
            raise ValueError(msg)

        self.api_key = brave_api_key
        self.session = session

    async def brave_search(self, query: str, count: int = 5, country: str = "us", search_lang: str = "en") -> BraveSearchResponse:
        if self.session is None:
            self.session = ClientSession()

        for _ in range(3):
            response = await self.session.get(
                url="https://api.search.brave.com/res/v1/web/search",
                headers={
                    "X-Subscription-Token": self.api_key,
                },
                params={"q": query, "count": count, "country": country, "search_lang": search_lang},
            )

            try:
                response.raise_for_status()
            except ClientResponseError as e:
                if e.status == HTTPTooManyRequests.status_code:
                    await asyncio.sleep(0.5)
                    continue
                raise

            return BraveSearchResponse.model_validate(await response.json())

        msg = "Failed to get search results"
        raise RuntimeError(msg)

    async def search(self, query: str, results: int = 5) -> SearchResponse:
        response = await self.brave_search(query, count=results)
        return response.to_search_response()
