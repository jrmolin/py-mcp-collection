from textwrap import dedent
from typing import TYPE_CHECKING, override
from unittest.mock import AsyncMock

import pytest
from aioresponses import aioresponses
from fastmcp import FastMCP
from fastmcp.client import Client
from fastmcp.tools import Tool
from mcp.types import CreateMessageResult, TextContent

from web_search_summary_mcp.clients.search.base import BaseSearchClient
from web_search_summary_mcp.models.search import SearchResponse, SearchResult
from web_search_summary_mcp.servers.summarize import SummarizeServer

if TYPE_CHECKING:
    from fastmcp.client.client import CallToolResult


def test_init():
    assert SummarizeServer()


class MockSearchClient(BaseSearchClient):
    @override
    async def search(self, query: str, results: int = 5) -> SearchResponse:
        return SearchResponse(results=[SearchResult(title="Test", url="https://test.com", snippet="Test snippet")])


@pytest.fixture
def search_client():
    return MockSearchClient()


@pytest.fixture
def mock_sampling_handler():
    return AsyncMock(
        return_value=CreateMessageResult(
            role="assistant", model="gpt-4o-mini", content=TextContent(type="text", text="This is a test summary")
        )
    )


@pytest.fixture
def search_server():
    return SummarizeServer(search_client=MockSearchClient())


@pytest.fixture
def fastmcp_server(mock_sampling_handler: AsyncMock, search_server: SummarizeServer):
    fastmcp = FastMCP[None](sampling_handler=mock_sampling_handler)
    fastmcp.add_tool(Tool.from_function(search_server.search, name="search"))
    fastmcp.add_tool(Tool.from_function(search_server.summarize, name="summarize"))
    return fastmcp


@pytest.fixture
def fastmcp_client(fastmcp_server: FastMCP[None]):
    return Client(transport=fastmcp_server)


async def test_search(search_server: SummarizeServer):
    response = await search_server.search("What is the latest version of Python?")
    assert len(response.results) == 1
    assert response.results[0].title == "Test"
    assert response.results[0].url == "https://test.com"
    assert response.results[0].snippet == "Test snippet"


@pytest.fixture
def simple_html_page():
    html_page = """
    <html>
        <body>
            <h1>Test</h1>
            <p>Test snippet</p>
        </body>
    </html>
    """

    return dedent(html_page).strip()


async def test_fetch_no_convert(search_server: SummarizeServer, simple_html_page: str):
    with aioresponses() as m:
        m.get("https://test.com", body=simple_html_page)
        response = await search_server.fetch("https://test.com", convert=False)
        assert response == simple_html_page


async def test_fetch_convert(search_server: SummarizeServer, simple_html_page: str):
    convert_result = dedent("""
        Test
        ====

        Test snippet

        """).lstrip()
    with aioresponses() as m:
        m.get("https://test.com", body=simple_html_page)
        response = await search_server.fetch("https://test.com", convert=True)
        assert response == convert_result


async def test_summarize(fastmcp_client: Client, simple_html_page: str):
    with aioresponses() as m:
        m.get("https://test.com", body=simple_html_page)
        async with fastmcp_client as client:
            response: CallToolResult = await client.call_tool(
                "summarize", arguments={"query": "What is the latest version of Python?", "include_results": True}
            )
            assert len(response.data.results) == 1
            assert response.data.results[0].title == "Test"
            assert response.data.results[0].url == "https://test.com"
            assert response.data.results[0].snippet == "Test snippet"
            assert response.data.results[0].content is not None
