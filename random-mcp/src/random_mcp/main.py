import asyncio
import os

import asyncclick as click
from fastmcp import FastMCP
from fastmcp.tools import Tool
from fastmcp.utilities.mcp_config import MCPConfig, StdioMCPServer
from git import Repo  # pip install gitpython

from .query import QUERY_INSTRUCTIONS, SEARCH_CODE_INSTRUCTIONS

mcp_config = MCPConfig(
    mcpServers={
        "github": StdioMCPServer(
            command="docker",
            args=[
                "run",
                "-i",
                "--rm",
                "-e",
                f"GITHUB_PERSONAL_ACCESS_TOKEN={os.environ['GITHUB_PERSONAL_ACCESS_TOKEN']}",
                "ghcr.io/github/github-mcp-server",
            ],
        )
    }
)


@click.command()
async def cli():
    mcp = FastMCP(name="Random MCP")

    github_proxy = FastMCP.as_proxy(mcp_config)

    def clone_repo(repo_url: str, repo_dir: str, depth: int = 1) -> str:
        Repo.clone_from(repo_url, repo_dir, depth=1)
        return f"Cloned {repo_url} to {repo_dir} at {depth} depth"

    def get_query_tips():
        return QUERY_INSTRUCTIONS

    def get_search_code_tips():
        return SEARCH_CODE_INSTRUCTIONS

    search_issues = await github_proxy.get_tool("search_issues")
    search_code = await github_proxy.get_tool("search_code")

    mcp.add_tool(search_issues)
    mcp.add_tool(search_code)

    mcp.add_tool(Tool.from_function(clone_repo))
    mcp.add_tool(Tool.from_function(get_query_tips))
    mcp.add_tool(Tool.from_function(get_search_code_tips))

    await mcp.run_async(transport="sse")


def run_mcp():
    asyncio.run(cli())


if __name__ == "__main__":
    run_mcp()
