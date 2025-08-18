from pydantic import BaseModel


class SearchResult(BaseModel):
    title: str
    url: str
    snippet: str
    content: str | None = None
    date: str | None = None
    author: str | None = None


class SearchResponse(BaseModel):
    results: list[SearchResult]


class SummaryResponse(BaseModel):
    summary: str
    results: list[SearchResult] | None = None
