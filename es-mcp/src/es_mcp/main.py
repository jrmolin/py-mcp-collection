import asyncio

import asyncclick as click
from dotenv import load_dotenv
from elasticsearch import AsyncElasticsearch
from fastmcp import FastMCP

load_dotenv()


@click.command()
@click.option("--es-host", type=str, envvar="ES_HOST", required=False, help="the host of the elasticsearch cluster")
@click.option("--api-key", type=str, envvar="ES_API_KEY", required=False, help="the api key of the elasticsearch cluster")
async def cli(es_host: str, api_key: str):
    es = AsyncElasticsearch(es_host, api_key=api_key)

    await es.ping()

    mcp = FastMCP(name="Local Es Mcp")

    mcp.add_tool(es.ping)
    mcp.add_tool(es.info)
    mcp.add_tool(es.cat.allocation)
    mcp.add_tool(es.cat.aliases)
    mcp.add_tool(es.cat.component_templates)
    mcp.add_tool(es.cat.count)
    mcp.add_tool(es.cat.fielddata)
    mcp.add_tool(es.cat.health)
    mcp.add_tool(es.cat.help)
    mcp.add_tool(es.cat.indices)
    mcp.add_tool(es.cat.master)
    mcp.add_tool(es.cat.ml_data_frame_analytics)
    mcp.add_tool(es.cat.ml_datafeeds)
    mcp.add_tool(es.cat.ml_jobs)
    mcp.add_tool(es.cat.ml_trained_models)
    mcp.add_tool(es.cat.nodeattrs)
    mcp.add_tool(es.cat.nodes)
    mcp.add_tool(es.cat.pending_tasks)
    mcp.add_tool(es.cat.plugins)
    mcp.add_tool(es.cat.recovery)
    mcp.add_tool(es.cat.repositories)
    mcp.add_tool(es.cat.segments)
    mcp.add_tool(es.cat.shards)
    mcp.add_tool(es.cat.snapshots)
    mcp.add_tool(es.cat.tasks)
    mcp.add_tool(es.cat.templates)
    mcp.add_tool(es.cat.thread_pool)
    mcp.add_tool(es.cat.transforms)
    mcp.add_tool(es.cluster.health)
    mcp.add_tool(es.cluster.state)
    mcp.add_tool(es.cluster.stats)
    mcp.add_tool(es.nodes.info)
    mcp.add_tool(es.nodes.stats)
    mcp.add_tool(es.indices.create_data_stream)
    mcp.add_tool(es.indices.get_data_stream)
    mcp.add_tool(es.indices.data_streams_stats)
    mcp.add_tool(es.indices.resolve_index)
    mcp.add_tool(es.ilm.get_lifecycle)
    mcp.add_tool(es.ilm.explain_lifecycle)
    mcp.add_tool(es.ilm.get_status)
    mcp.add_tool(es.slm.get_lifecycle)
    mcp.add_tool(es.slm.get_stats)
    mcp.add_tool(es.slm.get_status)
    mcp.add_tool(es.shutdown.get_node)

    await mcp.run_async()


def run_mcp():
    asyncio.run(cli())


if __name__ == "__main__":
    run_mcp()
