import inspect
from collections.abc import Callable
from inspect import Parameter
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, Optional, Self

import yaml
from elasticsearch import AsyncElasticsearch
from fastmcp.tools.tool import Tool
from makefun import create_function
from pydantic import BaseModel, Field, RootModel

if TYPE_CHECKING:
    from elastic_transport import ObjectApiResponse

type_name_to_type = {
    "string": str,
    "number": int,
    "boolean": bool,
}


class ESQLToolArgument(BaseModel):
    name: str
    description: str
    type: Literal["string", "number", "boolean"]
    required: bool
    default: Any | None

    def to_type(self) -> "type":
        return type_name_to_type[self.type] if self.required else (Optional[type_name_to_type[self.type]])  # noqa: UP045


class EsqlToolResultColumn(BaseModel):
    name: str
    type: str


class EsqlToolResultRow(RootModel[dict[str, Any]]):
    @classmethod
    def from_values(
        cls, columns: list[EsqlToolResultColumn], values: list[Any], trim_null: bool = True, trim_empty: bool = True
    ) -> Self:
        row: dict[str, Any] = {}
        for column, value in zip(columns, values, strict=False):
            if trim_null and value is None:
                continue

            if trim_empty and value == "":
                continue

            if trim_empty and isinstance(value, list) and len(value) == 0:
                continue

            row[column.name] = value

        return cls(root=row)

    @classmethod
    def from_response(cls, response: "EsqlResponse", trim_null: bool = True, trim_empty: bool = True) -> list[Self]:
        return [cls.from_values(response.columns, values, trim_null, trim_empty) for values in response.values]


class EsqlResponse(BaseModel):
    took: int
    documents_found: int
    values_loaded: int
    columns: list[EsqlToolResultColumn]
    values: list[Any]


class EsqlToolRawResult(EsqlResponse):
    pass


class EsqlToolResultValuesOnly(BaseModel):
    results: list[EsqlToolResultRow]


class EsqlToolResponseSettings(BaseModel):
    values_only: bool = Field(default=True)
    trim_null: bool = Field(default=True)
    trim_empty: bool = Field(default=True)


class EsqlTool(BaseModel):
    name: str
    description: str
    esql: str
    arguments: list[ESQLToolArgument]
    response: EsqlToolResponseSettings = Field(default=EsqlToolResponseSettings())

    def to_tool(self, client: AsyncElasticsearch) -> Tool:
        return Tool.from_function(fn=self.to_function(client=client), name=self.name, description=self.description)

    def to_function(self, client: AsyncElasticsearch):
        function_parameters: list[Parameter] = [
            Parameter(name=arg.name, kind=Parameter.KEYWORD_ONLY, annotation=arg.to_type()) for arg in self.arguments
        ]

        signature = inspect.Signature(parameters=function_parameters)

        async def function(*args, **kwargs: dict[str, Any]) -> Any:
            return await self.run(client, params=kwargs)

        return create_function(func_signature=signature, func_name=self.name, func_impl=function)

    async def run(self, client: AsyncElasticsearch, params: dict[str, Any] | None = None) -> EsqlToolRawResult | EsqlToolResultValuesOnly:
        params_list: list[dict[str, Any]] = [{k: v} for k, v in params.items()] if params else []
        result: ObjectApiResponse[Any] = await client.esql.async_query(query=self.esql, params=params_list)  # pyright: ignore[reportArgumentType]

        body: dict[str, Any] = result.body

        response: EsqlResponse = EsqlResponse(
            took=body["took"],
            documents_found=body["documents_found"],
            values_loaded=body["values_loaded"],
            columns=body["columns"],
            values=body["values"],
        )

        if self.response == "raw":
            return EsqlToolRawResult(
                took=response.took,
                documents_found=response.documents_found,
                values_loaded=response.values_loaded,
                columns=response.columns,
                values=response.values,
            )

        return EsqlToolResultValuesOnly(results=EsqlToolResultRow.from_response(response))


class EsqlToolConfig(BaseModel):
    tools: list[EsqlTool]


class EsqlToolBuilder:
    tools: list[EsqlTool]

    def __init__(self, es_client: AsyncElasticsearch):
        self.es_client = es_client

    def load_tools(self, str_or_path: str | Path):
        if isinstance(str_or_path, Path):
            with Path.open(str_or_path) as f:
                tools = yaml.safe_load(f)
        else:
            tools = yaml.safe_load(str_or_path)

        esql_tool_config = EsqlToolConfig(tools=tools["tools"])

        self.tools = esql_tool_config.tools

    def to_fastmcp_tools(self) -> list[Tool | Callable[..., Any]]:
        return [tool.to_tool(client=self.es_client) for tool in self.tools]
