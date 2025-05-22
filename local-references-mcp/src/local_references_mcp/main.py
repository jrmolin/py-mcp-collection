import asyncio

import asyncclick as click
from fastmcp import FastMCP

from local_references_mcp.references import ReferenceManager


@click.command()
@click.option("--reference", type=str, required=True, multiple=True, help="The reference to use. name:path")
@click.option("--preview-size", type=int, default=1000, help="The number of characters to preview from each entry")
async def cli(reference: list[str], preview_size: int):
    mcp = FastMCP(name="Local References")

    reference_manager: ReferenceManager = ReferenceManager.from_reference_strings(reference, preview_size)

    reference_manager.register_tools(mcp_server=mcp)

    await mcp.run_async()


def run_mcp():
    asyncio.run(cli())


if __name__ == "__main__":
    run_mcp()
