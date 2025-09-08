import os

import pytest
from openai import OpenAI

OPENAI_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")


@pytest.fixture
def openai_client() -> OpenAI:
    return OpenAI(api_key=OPENAI_KEY, base_url=OPENAI_BASE_URL)
