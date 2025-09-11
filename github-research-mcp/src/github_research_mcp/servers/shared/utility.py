import base64
from collections.abc import Sequence

from githubkit.response import Response
from pydantic import BaseModel


def estimate_tokens(text: str) -> int:
    """Estimate the number of tokens for a given text."""
    return len(text) // 4


def estimate_model_tokens(basemodel: BaseModel | Sequence[BaseModel]) -> int:
    """Estimate the number of tokens for a given base model."""
    if isinstance(basemodel, Sequence):
        return sum(estimate_model_tokens(item) for item in basemodel)

    return estimate_tokens(basemodel.model_dump_json())


def extract_response[T: BaseModel | Sequence[BaseModel]](response: Response[T]) -> T:
    """Extract the response from a response."""

    return response.parsed_data


def decode_content(content: str) -> str:
    return base64.b64decode(content).decode("utf-8")
