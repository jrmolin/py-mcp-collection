import asyncio
import os
from typing import Any

import asyncclick as click
from fastmcp import FastMCP
from fastmcp.contrib.llm_sampling_handler import OpenAISamplingHandler
from fastmcp.tools.tool import Tool
from openai import OpenAI

from web_search_summary_mcp.servers.summarize import SummarizeServer

# class BraveServer(BaseModel):
#     model_config: ClassVar[ConfigDict] = ConfigDict(arbitrary_types_allowed=True)

#     brave_client: BraveClient


@click.command()
async def cli():
    search_server = SummarizeServer()

    sampling_handler: OpenAISamplingHandler = OpenAISamplingHandler(
        default_model="gpt-5-nano", client=OpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("OPENAI_BASE_URL"))
    )

    mcp = FastMCP[Any](name="Local Web Search Mcp", sampling_handler=sampling_handler)
    mcp.add_tool(Tool.from_function(search_server.summarize, name="summarize"))

    await mcp.run_async()


def run_mcp():
    asyncio.run(cli())


if __name__ == "__main__":
    run_mcp()
