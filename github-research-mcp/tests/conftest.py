import os
from typing import Any

import pytest
from fastmcp import FastMCP
from fastmcp.experimental.sampling.handlers.openai import OpenAISamplingHandler
from fastmcp.server.middleware.logging import LoggingMiddleware
from githubkit.github import GitHub
from openai import OpenAI

from github_research_mcp.clients.github import get_github_client

OPENAI_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")


@pytest.fixture
def openai_client() -> OpenAI:
    return OpenAI(api_key=OPENAI_KEY, base_url=OPENAI_BASE_URL)


@pytest.fixture
def github_client() -> GitHub[Any]:
    return get_github_client()


@pytest.fixture
def fastmcp(openai_client: OpenAI):
    return FastMCP(
        sampling_handler=OpenAISamplingHandler(
            default_model=OPENAI_MODEL,  # pyright: ignore[reportArgumentType]
            client=openai_client,
        ),
        middleware=[LoggingMiddleware()],
    )
