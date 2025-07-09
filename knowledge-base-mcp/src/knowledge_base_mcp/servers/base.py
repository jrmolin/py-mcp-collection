from abc import ABC, abstractmethod
from typing import Any, ClassVar

from fastmcp import FastMCP
from fastmcp.tools import Tool as FastMCPTool
from pydantic import ConfigDict
from pydantic.main import BaseModel

from knowledge_base_mcp.clients.knowledge_base import KnowledgeBaseClient


class BaseKnowledgeBaseServer(BaseModel, ABC):  # pyright: ignore[reportUnsafeMultipleInheritance]
    """A base server for all servers."""

    model_config: ClassVar[ConfigDict] = ConfigDict(arbitrary_types_allowed=True)

    knowledge_base_client: KnowledgeBaseClient

    server_name: str

    def as_fastmcp(self) -> FastMCP[Any]:
        """Convert the server to a FastMCP server."""

        mcp: FastMCP[Any] = FastMCP[Any](name=self.server_name)

        [mcp.add_tool(tool=tool) for tool in self.get_tools()]

        return mcp

    @abstractmethod
    def get_tools(self) -> list[FastMCPTool]: ...
