import os
from typing import Any

import pytest
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
