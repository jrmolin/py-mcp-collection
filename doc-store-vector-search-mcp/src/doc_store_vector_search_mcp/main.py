import asyncio

from fastmcp import FastMCP


async def cli():
    """Entrypoint for the FastMCP server."""
    mcp = FastMCP(name="Doc Store Vector Search MCP")
    await mcp.run_async()


def run_mcp():
    asyncio.run(cli())


if __name__ == "__main__":
    run_mcp()
