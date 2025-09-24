from typing import TYPE_CHECKING, Any

from pydantic import BaseModel
import pytest
from inline_snapshot import snapshot

from elasticsearch_esql_tools_mcp.clients.elasticsearch import build_es_client
from elasticsearch_esql_tools_mcp.tool_builder.compile import EsqlTool, ESQLToolArgument, EsqlToolResultRow, EsqlToolResultValuesOnly

if TYPE_CHECKING:
    from fastmcp.tools.tool import Tool


def test_compile_esql_tool():
    esql_tool = EsqlTool(name="test", description="test", esql="FROM * | LIMIT 10", arguments=[])

    assert esql_tool == snapshot(EsqlTool(name="test", description="test", esql="FROM * | LIMIT 10", arguments=[]))


def test_compile_esql_tool_with_arguments():
    esql_tool = EsqlTool(
        name="test",
        description="test",
        esql="FROM * | LIMIT 10",
        arguments=[
            ESQLToolArgument(
                name="test",
                description="test",
                type="string",
                required=True,
                default=None,
            )
        ],
    )

    assert esql_tool == snapshot(
        EsqlTool(
            name="test",
            description="test",
            esql="FROM * | LIMIT 10",
            arguments=[ESQLToolArgument(name="test", description="test", type="string", required=True, default=None)],
        )
    )


@pytest.fixture
async def es_client():
    es_client = build_es_client()

    yield es_client

    await es_client.close()


def test_compile_esql_tool_to_tool(es_client):
    esql_tool = EsqlTool(name="test", description="test", esql="FROM * | LIMIT 10", arguments=[])

    tool: Tool = esql_tool.to_tool(client=es_client)

    assert tool.to_mcp_tool().model_dump() == snapshot(
        {
            "name": "test",
            "title": None,
            "description": "test",
            "inputSchema": {"properties": {}, "type": "object"},
            "outputSchema": None,
            "annotations": None,
            "meta": None,
        }
    )


def test_compile_esql_tool_to_tool_with_arguments(es_client):
    esql_tool = EsqlTool(
        name="test",
        description="test",
        esql="FROM * | LIMIT 10",
        arguments=[ESQLToolArgument(name="test", description="test", type="string", required=True, default=None)],
    )

    tool: Tool = esql_tool.to_tool(client=es_client)

    assert tool.to_mcp_tool().model_dump() == snapshot(
        {
            "name": "test",
            "title": None,
            "description": "test",
            "inputSchema": {
                "properties": {"test": {"title": "Test", "type": "string"}},
                "required": ["test"],
                "type": "object",
            },
            "outputSchema": None,
            "annotations": None,
            "meta": None,
        }
    )


def test_compile_esql_tool_to_tool_with_optional_arguments(es_client):
    esql_tool = EsqlTool(
        name="test",
        description="test",
        esql="FROM * | LIMIT 10",
        arguments=[ESQLToolArgument(name="test", description="test", type="string", required=False, default=None)],
    )

    tool: Tool = esql_tool.to_tool(client=es_client)

    assert tool.to_mcp_tool().model_dump() == snapshot(
        {
            "name": "test",
            "title": None,
            "description": "test",
            "inputSchema": {
                "properties": {"test": {"anyOf": [{"type": "string"}, {"type": "null"}], "title": "Test"}},
                "required": ["test"],
                "type": "object",
            },
            "outputSchema": None,
            "annotations": None,
            "meta": None,
        }
    )


async def test_run_esql_tool(es_client):
    esql_tool = EsqlTool(name="test", description="test", esql="FROM * | KEEP slug | LIMIT 1", arguments=[])

    result: Any = await esql_tool.run(client=es_client, params={})

    assert result == snapshot(
        EsqlToolResultValuesOnly(
            results=[EsqlToolResultRow(root={"slug": "docs-reference-elasticsearch-rest-apis-retrieve-stored-fields.md"})]
        )
    )


async def test_run_esql_tool_with_arguments(es_client):
    esql_tool = EsqlTool(
        name="search_by_title",
        description="Search for documents by matching part of their title",
        esql="FROM * | KEEP content_title | WHERE MATCH(content_title,?title ) | LIMIT 100",
        arguments=[ESQLToolArgument(name="title", description="Title to search for", type="string", required=True, default=None)],
    )

    assert esql_tool.model_dump() == snapshot(
        {
            "name": "search_by_title",
            "description": "Search for documents by matching part of their title",
            "esql": "FROM * | KEEP content_title | WHERE MATCH(content_title,?title ) | LIMIT 100",
            "arguments": [{"name": "title", "description": "Title to search for", "type": "string", "required": True, "default": None}],
            "response": "values_only",
        }
    )

    result: BaseModel = await esql_tool.run(client=es_client, params={"title": "recovery"})

    assert result.model_dump() == snapshot(
        {
            "results": [
                {"content_title": "Docs / Reference / Elasticsearch / Configuration Reference / Index Recovery Settings"},
                {"content_title": "Docs / Reference / Elasticsearch / Index Settings / Recovery Prioritization"},
            ]
        }
    )
