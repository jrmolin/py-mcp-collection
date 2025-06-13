import asyncio
from typing import Literal

import asyncclick as click
from fastmcp import FastMCP
from fastmcp.utilities.logging import configure_logging
from langchain_community.vectorstores.duckdb import DuckDB

from doc_store_vector_search_mcp.etl.store import DuckDBSettings, ProjectVectorStoreManager, VectorStoreManager
from doc_store_vector_search_mcp.logging.util import BASE_LOGGER
from doc_store_vector_search_mcp.servers.load import DocumentServer
from doc_store_vector_search_mcp.servers.search import SearchServer

logger = BASE_LOGGER.getChild("main")


@click.command()
@click.option("--mcp-transport", type=click.Choice(["stdio", "sse", "streamable-http"]), default="stdio")
async def cli(mcp_transport: Literal["stdio", "sse", "streamable-http"]):
    """Entrypoint for the FastMCP server."""
    logger.info("Starting Doc Store Vector Search MCP")
    configure_logging()

    mcp = FastMCP(name="Doc Store Vector Search MCP")

    code_settings = DuckDBSettings(db_path=":memory:")
    document_settings = DuckDBSettings(db_path=":memory:")

    logger.info("Creating vector store manager")
    vector_store_manager = VectorStoreManager[DuckDB, DuckDBSettings](
        project_name="Local Development",
        kb_id="First KB",
        code_settings=code_settings,
        document_settings=document_settings,
        vector_store_class=DuckDB,
    )

    project_vector_store_manager = ProjectVectorStoreManager(
        project_name="Local Development",
        code_vector_store=vector_store_manager,
        document_vector_store=vector_store_manager,
    )

    logger.info("Creating document and search servers")
    document_server = DocumentServer(project_name="Local Development", project_vectorstore=project_vector_store_manager)
    search_server = SearchServer(project_name="Local Development", project_vectorstore=project_vector_store_manager)

    document_server.register_all(mcp)
    search_server.register_all(mcp)

    # await document_server.load_webpage(
    #     urls=["https://docs.pydantic.dev/latest/"],
    #     recursive=True,
    #     knowledge_base="pydantic",
    # )

    # print(await vector_store_manager.search_documents(
    #     query="What is a field validator and how do I use it as a decorator?",
    #     documents=10,
    # ))

    logger.info("Running FastMCP")
    await mcp.run_async(transport=mcp_transport)


def run_mcp():
    asyncio.run(cli())


if __name__ == "__main__":
    run_mcp()
