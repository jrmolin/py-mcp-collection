from pydantic import BaseModel


class SearchResult(BaseModel):
    title: str
    url: str
    snippet: str
    content: str | None = None
    date: str | None = None
    author: str | None = None


class SearchResponse(BaseModel):
    summary: str | None = None
    results: list[SearchResult]
