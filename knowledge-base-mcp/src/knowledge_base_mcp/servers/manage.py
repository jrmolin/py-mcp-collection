from logging import Logger
from typing import Any

from fastmcp import FastMCP
from fastmcp.tools import Tool as FastMCPTool

from knowledge_base_mcp.servers.base import BaseKnowledgeBaseServer
from knowledge_base_mcp.utils.logging import BASE_LOGGER

logger: Logger = BASE_LOGGER.getChild(suffix=__name__)


class KnowledgeBaseManagementServer(BaseKnowledgeBaseServer):
    """A server for managing knowledge bases."""

    server_name: str = "Knowledge Base Management Server"

    def get_management_tools(self) -> list[FastMCPTool]:
        return [
            FastMCPTool.from_function(fn=self.knowledge_base_client.get_knowledge_bases),
            FastMCPTool.from_function(fn=self.knowledge_base_client.delete_knowledge_base),
            FastMCPTool.from_function(fn=self.knowledge_base_client.delete_all_knowledge_bases),
            FastMCPTool.from_function(fn=self.knowledge_base_client.get_knowledge_base_stats),
            FastMCPTool.from_function(fn=self.knowledge_base_client.clean_knowledge_base_hash_store),
        ]

    def as_management_server(self) -> FastMCP[Any]:
        """Get the management tools for the server."""
        mcp: FastMCP[Any] = FastMCP[Any](name=self.server_name)

        [mcp.add_tool(tool=tool) for tool in self.get_management_tools()]

        return mcp
