import asyncio
import logging
import os
from typing import Any

import asyncclick as click
from fastmcp import FastMCP
from fastmcp.contrib.llm_sampling_handler import OpenAISamplingHandler
from fastmcp.tools.tool import Tool
from openai import OpenAI

from web_search_summary_mcp.servers.summarize import SummarizeServer

logger = logging.getLogger(__name__)

MODEL_ENV_VAR = "OPENAI_MODEL"
API_KEY_ENV_VAR = "OPENAI_API_KEY"
BASE_URL_ENV_VAR = "OPENAI_BASE_URL"


@click.command()
async def cli():
    sampling_handler: OpenAISamplingHandler | None = None
    search_server = SummarizeServer()

    if any(os.getenv(var) for var in [MODEL_ENV_VAR, API_KEY_ENV_VAR, BASE_URL_ENV_VAR]):
        sampling_handler = OpenAISamplingHandler(
            default_model=os.getenv(MODEL_ENV_VAR),  # pyright: ignore[reportArgumentType]
            client=OpenAI(
                api_key=os.getenv(API_KEY_ENV_VAR),
                base_url=os.getenv(BASE_URL_ENV_VAR),
            ),
        )

    mcp = FastMCP[Any](name="Web Search and Summarize MCP", sampling_handler=sampling_handler)

    mcp.add_tool(Tool.from_function(search_server.search, name="search"))
    mcp.add_tool(Tool.from_function(search_server.fetch, name="fetch"))

    if sampling_handler:
        mcp.add_tool(Tool.from_function(search_server.summarize, name="answer"))

    await mcp.run_async()


def run_mcp():
    asyncio.run(cli())


if __name__ == "__main__":
    run_mcp()
