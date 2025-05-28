import asyncio

import asyncclick as click
from fastmcp import FastMCP


@click.command()
@click.option("--cli-arg-1", type=str, required=False, help="The first argument to pass to the CLI")
@click.option("--cli-arg-2", type=str, required=False, help="The second argument to pass to the CLI")
@click.option("--cli-arg-3", type=str, required=False, help="The third argument to pass to the CLI")
async def cli(cli_arg_1: str, cli_arg_2: str, cli_arg_3: str):
    mcp = FastMCP(name="Local Es Mcp")

    await mcp.run_async()


def run_mcp():
    asyncio.run(cli())


if __name__ == "__main__":
    run_mcp()
