import os
from typing import TYPE_CHECKING

import pytest
from fastmcp import FastMCP
from fastmcp.client import Client
from fastmcp.contrib.llm_sampling_handler import OpenAISamplingHandler
from fastmcp.contrib.llm_sampling_handler.openai_sampling_handler import OpenAI
from fastmcp.tools import Tool

from web_search_summary_mcp.clients.search.brave import BraveClient
from web_search_summary_mcp.servers.summarize import SummarizeServer

if TYPE_CHECKING:
    from fastmcp.client.client import CallToolResult


def test_init():
    assert SummarizeServer()


@pytest.fixture
async def search_client():
    return BraveClient()


@pytest.fixture
def search_server():
    return SummarizeServer()


@pytest.fixture
def fastmcp_server(search_server: SummarizeServer):
    openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("OPENAI_BASE_URL"))

    fastmcp = FastMCP[None](sampling_handler=OpenAISamplingHandler(default_model="gemini-2.5-flash-lite", client=openai))  # pyright: ignore[reportArgumentType]

    fastmcp.add_tool(Tool.from_function(search_server.search, name="search"))
    fastmcp.add_tool(Tool.from_function(search_server.summarize, name="summarize"))

    return fastmcp


@pytest.fixture
def fastmcp_client(fastmcp_server: FastMCP[None]):
    return Client(transport=fastmcp_server)

@pytest.mark.not_on_ci
async def test_search(search_server: SummarizeServer):
    response = await search_server.search("What is the latest version of Python?")
    assert response.summary is None
    assert len(response.results) == 5

@pytest.mark.not_on_ci
async def test_summarize_latest_python(fastmcp_client: Client):
    async with fastmcp_client as client:
        response: CallToolResult = await client.call_tool("summarize", arguments={"query": "What is the latest version of Python?"})
        assert response.data.summary
        assert response.data.results

@pytest.mark.not_on_ci
async def test_summarize_python_inline_type_parameters_short(fastmcp_client: Client):
    async with fastmcp_client as client:
        response: CallToolResult = await client.call_tool(
            "summarize", arguments={"query": "How do I use Type Parameter Defaults in Python?", "depth": "Short"}
        )
        assert response.data.summary
        assert response.data.results

@pytest.mark.not_on_ci
async def test_summarize_python_inline_type_parameters_medium(fastmcp_client: Client):
    async with fastmcp_client as client:
        response: CallToolResult = await client.call_tool(
            "summarize", arguments={"query": "How do I use Type Parameter Defaults in Python?", "depth": "Medium"}
        )
        assert response.data.summary
        assert response.data.results