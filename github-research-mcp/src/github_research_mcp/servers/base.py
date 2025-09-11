from typing import TYPE_CHECKING, Any

from fastmcp.server.dependencies import get_context
from fastmcp.utilities.logging import get_logger
from githubkit.github import GitHub
from mcp.types import ContentBlock, SamplingMessage, TextContent
from pydantic import BaseModel

from github_research_mcp.models.graphql.queries import BaseGqlQuery
from github_research_mcp.sampling.extract import extract_single_object_from_text
from github_research_mcp.servers.shared.utility import estimate_model_tokens

if TYPE_CHECKING:
    from fastmcp.server import Context

logger = get_logger(__name__)


class BaseResponseModel(BaseModel):
    def estimate_tokens(self) -> int:
        return estimate_model_tokens(self)


class BaseServer:
    github_client: GitHub[Any]

    async def _structured_sample[T: BaseModel](
        self, system_prompt: str, messages: str | list[str], object_type: type[T], max_tokens: int = 2000, temperature: float = 0.0
    ) -> T:
        """Sample a structured response from the server."""

        sampling_response: str = await self._sample(
            system_prompt=system_prompt, messages=messages, max_tokens=max_tokens, temperature=temperature
        )

        if structured_response := extract_single_object_from_text(sampling_response, object_type):
            return structured_response

        msg = "The sampling call failed to generate a valid structured response."
        raise TypeError(msg)

    async def _sample(self, system_prompt: str, messages: str | list[str], max_tokens: int = 2000, temperature: float = 0.0) -> str:
        """Sample a response from the server."""

        context: Context = get_context()

        if isinstance(messages, str):
            messages = [messages]

        sampling_messages: str | list[str | SamplingMessage] = [
            SamplingMessage(role="user", content=TextContent(type="text", text=message)) for message in messages
        ]

        summary: ContentBlock = await context.sample(
            system_prompt=system_prompt,
            messages=sampling_messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        if not isinstance(summary, TextContent):
            msg = "The sampling call failed to generate a valid text summary of the issue."
            raise TypeError(msg)

        return summary.text

    async def _perform_graphql_query[T: BaseGqlQuery](self, query_model: type[T], variables: dict[str, Any]) -> T:
        """Perform a GraphQL query and return the response as a model."""

        logger.info(f"Executing GraphQL query {query_model.__name__} with variables {variables}")

        raw_response = await self.github_client.async_graphql(
            query=query_model.graphql_query(),
            variables=variables,
        )

        response_model = query_model.model_validate(raw_response)
        response_size = estimate_model_tokens(response_model)

        logger.info(f"Completed GraphQL query {query_model.__name__} for with variables {variables} returned {response_size} tokens.")

        return response_model
