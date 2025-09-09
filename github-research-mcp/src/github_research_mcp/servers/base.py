from typing import Any

from githubkit.github import GitHub

from github_research_mcp.clients.github import get_github_client
from github_research_mcp.models.graphql.queries import BaseGqlQuery


class BaseServer:
    _client: GitHub[Any]

    def __init__(self, client: GitHub[Any] | None = None):
        self._client = client or get_github_client()

    async def _perform_query[T: BaseGqlQuery](self, query_model: type[T], variables: dict[str, Any]) -> T:
        """Perform a GraphQL query and return the response as a model."""

        raw_response = await self._client.async_graphql(
            query=query_model.graphql_query(),
            variables=variables,
        )

        return query_model.model_validate(raw_response)
