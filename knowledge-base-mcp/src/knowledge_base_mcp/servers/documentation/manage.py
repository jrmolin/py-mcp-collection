from logging import Logger

from fastmcp.tools import Tool as FastMCPTool

from knowledge_base_mcp.clients.knowledge_base import KnowledgeBaseClient
from knowledge_base_mcp.utils.logging import BASE_LOGGER
from knowledge_base_mcp.utils.models import BaseKBModel

logger: Logger = BASE_LOGGER.getChild(suffix=__name__)


class KnowledgeBaseManagementServer(BaseKBModel):
    """A server for managing knowledge bases."""

    knowledge_base_client: KnowledgeBaseClient

    def get_raw_tools(self) -> list[FastMCPTool]:
        return [
            FastMCPTool.from_function(fn=self.knowledge_base_client.get_knowledge_bases),
            FastMCPTool.from_function(fn=self.knowledge_base_client.delete_knowledge_base),
            FastMCPTool.from_function(fn=self.knowledge_base_client.delete_all_knowledge_bases),
            FastMCPTool.from_function(fn=self.knowledge_base_client.get_knowledge_base_stats),
            FastMCPTool.from_function(fn=self.knowledge_base_client.clean_knowledge_base_hash_store),
        ]
