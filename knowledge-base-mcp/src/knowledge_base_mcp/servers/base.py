from abc import ABC
from typing import ClassVar

from pydantic import ConfigDict
from pydantic.main import BaseModel

from knowledge_base_mcp.clients.knowledge_base import KnowledgeBaseClient


class BaseKnowledgeBaseServer(BaseModel, ABC):  # pyright: ignore[reportUnsafeMultipleInheritance]
    """A base server for all servers."""

    model_config: ClassVar[ConfigDict] = ConfigDict(arbitrary_types_allowed=True)

    knowledge_base_client: KnowledgeBaseClient

    server_name: str
