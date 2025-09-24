import os
from collections.abc import Callable
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from fastmcp import FastMCP
from fastmcp.tools.tool import Tool

from elasticsearch_esql_tools_mcp.clients.elasticsearch import build_es_client
from elasticsearch_esql_tools_mcp.tool_builder.compile import EsqlToolBuilder

_ = load_dotenv()

esql_tools_yaml = os.getenv("ESQL_TOOLS_YAML", "esql_tools.yaml")

es_client = build_es_client()

esql_tools_builder = EsqlToolBuilder(es_client)
esql_tools_builder.load_tools(Path(esql_tools_yaml))
esql_tools: list[Tool | Callable[..., Any]] = esql_tools_builder.to_fastmcp_tools()

mcp: FastMCP[Any] = FastMCP(name="elasticsearch-esql-tools-mcp", tools=esql_tools)


def run_mcp():
    transport = os.getenv("TRANSPORT", "sse")
    mcp.run(transport=transport)


if __name__ == "__main__":
    run_mcp()
