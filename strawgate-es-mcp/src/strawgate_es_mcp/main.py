import asyncio
import re
from collections.abc import Callable
from typing import Annotated, Any, Literal

import asyncclick as click
from dotenv import load_dotenv
from elasticsearch import AsyncElasticsearch
from fastmcp import FastMCP
from fastmcp.tools import FunctionTool

from strawgate_es_mcp.data_stream.summarize import DataStreamSummary, new_data_stream_summaries
from strawgate_es_mcp.search.dsl import search_dsl_tips, search_str_fn_factory
from strawgate_es_mcp.search.esql import esql_query_tips

_ = load_dotenv()



def build_es_client(es_host: str, api_key: str) -> AsyncElasticsearch:
    return AsyncElasticsearch(es_host, api_key=api_key, http_compress=True)

async def build_server(
    es: AsyncElasticsearch,
    include_tags: list[str] | None = None,
    exclude_tags: list[str] | None = None,
    include_tools_patterns: list[str] | None = None,
    exclude_tools_patterns: list[str] | None = None,
):
    mcp = FastMCP[Any](
        name="Strawgate Elasticsearch MCP",
        include_tags=set(include_tags) if include_tags is not None else None,
        exclude_tags=set(exclude_tags) if exclude_tags is not None else None,
    )

    async def summarize_data_streams(data_streams: Annotated[list[str], "The data streams to summarize"]) -> list[DataStreamSummary]:
        """Summarize the data stream, providing field information and sample rows for each requested data stream"""
        return await new_data_stream_summaries(es, data_streams)

    custom_tools: list[Callable[..., Any]] = [
        summarize_data_streams,
        search_str_fn_factory(es=es),
        search_dsl_tips,
        esql_query_tips,
    ]

    relevant_clients = [
        es.autoscaling,
        es.cat,
        es.ccr,
        es.cluster,
        es.connector,
        es.dangling_indices,
        es.enrich,
        es.eql,
        es.esql,
        es.features,
        es.fleet,
        es.graph,
        es.ilm,
        es.indices,
        es.inference,
        es.ingest,
        es.license,
        es.logstash,
        es.migration,
        es.ml,
        es.monitoring,
        es.nodes,
        es.query_rules,
        es.rollup,
        es.search_application,
        es.searchable_snapshots,
        es.security,
        es.shutdown,
        es.simulate,
        es.slm,
        es.snapshot,
        es.sql,
        es.ssl,
        es.synonyms,
        es.tasks,
        es.text_structure,
        es.transform,
        es.watcher,
        es.xpack,
    ]

    standalone_functions = [es.search]

    for client in relevant_clients:
        client_mcp = FastMCP[Any](name=client.__class__.__name__)

        # classname is things like "EsqlClient"
        # but the prefix and tag we want to be "esql" so we need to remove the "Client" suffix and lowercase the first letter
        client_prefix = client.__class__.__name__.replace("Client", "").lower()

        for tool in dir(client):
            if not tool.startswith("_") and not isinstance(getattr(client, tool), property):
                tool_function: Any = getattr(client, tool)  # pyright: ignore[reportAny]

                if not isinstance(tool_function, Callable):
                    continue

                if include_tools_patterns and not any(re.match(pattern, tool) for pattern in include_tools_patterns):
                    continue

                if exclude_tools_patterns and any(re.match(pattern, tool) for pattern in exclude_tools_patterns):
                    continue

                tool_tags = {client_prefix}

                _ = client_mcp.add_tool(FunctionTool.from_function(fn=tool_function, tags=tool_tags))  # pyright: ignore[reportUnknownArgumentType]

        _ = await mcp.import_server(client_mcp, prefix=client_prefix)

    for custom_tool in custom_tools:
        _ = mcp.add_tool(FunctionTool.from_function(custom_tool, tags={"custom"}))

    for standalone_function in standalone_functions:
        _ = mcp.add_tool(FunctionTool.from_function(standalone_function, tags={"standalone"}))

    return mcp


@click.command()
@click.option("--es-host", type=str, envvar="ES_HOST", required=False, help="the host of the elasticsearch cluster")
@click.option("--api-key", type=str, envvar="ES_API_KEY", required=False, help="the api key of the elasticsearch cluster")
@click.option("--transport", type=click.Choice(["stdio", "sse"]), default="stdio", help="the transport to use for the MCP")
@click.option("--include-tags", type=str, envvar="INCLUDE_TAGS", required=False, multiple=True, help="the tags to include in the MCP")
@click.option("--exclude-tags", type=str, envvar="EXCLUDE_TAGS", required=False, multiple=True, help="the tags to exclude from the MCP")
@click.option(
    "--include-tools-patterns",
    type=str,
    envvar="INCLUDE_TOOLS_PATTERNS",
    required=False,
    multiple=True,
    help="the patterns to include in the MCP",
)
@click.option(
    "--exclude-tools-patterns",
    type=str,
    envvar="EXCLUDE_TOOLS_PATTERNS",
    required=False,
    multiple=True,
    help="the patterns to exclude from the MCP",
)
async def cli(
    es_host: str,
    api_key: str,
    transport: Literal["stdio", "sse"],
    include_tags: list[str],
    exclude_tags: list[str],
    include_tools_patterns: list[str],
    exclude_tools_patterns: list[str],
) -> None:
    es = build_es_client(es_host, api_key)

    expanded_include_tags: list[str] = []
    for tag in include_tags:
        expanded_include_tags.extend(tag.strip() for tag in tag.split(","))

    expanded_exclude_tags: list[str] = []
    for tag in exclude_tags:
        expanded_exclude_tags.extend(tag.strip() for tag in tag.split(","))

    mcp = await build_server(es, expanded_include_tags, expanded_exclude_tags, include_tools_patterns, exclude_tools_patterns)

    _ = await es.ping()

    await mcp.run_async(transport=transport)


def run_mcp():
    asyncio.run(main=cli())


if __name__ == "__main__":
    run_mcp()
