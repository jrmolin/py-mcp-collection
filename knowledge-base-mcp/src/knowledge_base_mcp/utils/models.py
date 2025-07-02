from typing import ClassVar

from pydantic import BaseModel
from pydantic.config import ConfigDict


class BaseKBModel(BaseModel):
    """A pydantic base model for a knowledge base project."""

    model_config: ClassVar[ConfigDict] = ConfigDict(
        strict=True,
        frozen=True,
        use_attribute_docstrings=True,
        extra="forbid",
    )


class BaseKBArbitraryModel(BaseModel):
    """A pydantic base model for a knowledge base project."""

    model_config: ClassVar[ConfigDict] = ConfigDict(
        strict=False,
        frozen=False,
        use_attribute_docstrings=True,
        extra="allow",
        arbitrary_types_allowed=True,
    )
