from collections.abc import Sequence

from pydantic import BaseModel


def estimate_tokens(text: str) -> int:
    """Estimate the number of tokens for a given text."""
    return len(text) // 4


def estimate_model_tokens(basemodel: BaseModel | Sequence[BaseModel]) -> int:
    """Estimate the number of tokens for a given base model."""
    if isinstance(basemodel, Sequence):
        return sum(estimate_model_tokens(item) for item in basemodel)

    return estimate_tokens(basemodel.model_dump_json())
