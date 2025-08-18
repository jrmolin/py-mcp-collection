from enum import StrEnum
from typing import Annotated, ClassVar

import yaml
from fastmcp import Context
from mcp.types import SamplingMessage, TextContent
from pydantic import BaseModel, ConfigDict, Field

from web_search_summary_mcp.clients.convert.base import BaseConvertClient
from web_search_summary_mcp.clients.convert.markdown import MarkdownConvertClient
from web_search_summary_mcp.clients.fetch.base import BaseFetchClient
from web_search_summary_mcp.clients.fetch.simple import SimpleFetchClient
from web_search_summary_mcp.clients.search.auto import AutoSearchClient
from web_search_summary_mcp.clients.search.base import BaseSearchClient
from web_search_summary_mcp.models.search import SearchResponse, SummaryResponse


class SummarizeDepth(StrEnum):
    SHORT = "Short"
    MEDIUM = "Medium"
    LONG = "Long"

    def to_prompt(self) -> str:
        preamble = "The answer to the posed query should be presented first and be short and concise."
        match self:
            case SummarizeDepth.SHORT:
                return f"{preamble}, focusing on answering the user's exact question with little to no extra information."
            case SummarizeDepth.MEDIUM:
                return f"{preamble}, but a summary of the context related to the answer should follow the answer."
            case SummarizeDepth.LONG:
                return (
                    f"{preamble}, but a detailed analysis of the background and context related to the answer should follow the answer. "
                    "This analysis should include additional information gathered from the results that the user may find "
                    "helpful based on the query."
                )
            case _:
                msg = f"Invalid depth: {self}"
                raise ValueError(msg)


class SummarizeServer(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(arbitrary_types_allowed=True)

    search_client: BaseSearchClient = Field(default_factory=AutoSearchClient)
    fetch_client: BaseFetchClient = Field(default_factory=SimpleFetchClient)
    convert_client: BaseConvertClient = Field(default_factory=MarkdownConvertClient)

    async def search(self, query: str) -> SearchResponse:
        """Perform a web search for the given query and return the results."""
        return await self.search_client.search(query)

    async def fetch(self, url: str, convert: bool = True) -> str:
        """Fetch the content of the given URL and return the content as markdown."""

        content: str = await self.fetch_client.fetch(url)

        if convert:
            content = await self.convert_client.convert(content)

        return content

    async def try_fetch(self, url: str, convert: bool = True) -> str | None:
        """Fetch the content of the given URL and return the content as markdown. Return None if the fetch fails."""

        try:
            return await self.fetch(url, convert=convert)
        except Exception as e:
            msg = f"Error fetching {url}: {e}"
            print(msg)
            return None

    async def search_and_fetch(self, query: str, convert: bool = True) -> SearchResponse:
        """Perform a web search for the given query and return the results."""

        response = await self.search(query)

        if not response.results:
            msg = "No results were found"
            raise ValueError(msg)

        for result in response.results:
            result.content = await self.try_fetch(result.url, convert=convert)

        return response

    async def summarize(
        self,
        ctx: Context,
        query: str,
        depth: Annotated[
            SummarizeDepth, "The depth of the summary. i.e. how far beyond answering the exact question should the summary go?"
        ] = SummarizeDepth.MEDIUM,
        include_results: Annotated[bool, "Whether to include the raw search results with the answer"] = False,
    ) -> SummaryResponse:
        """Perform a web search for the given query and summarize the results."""

        response = await self.search_and_fetch(query)

        if not response.results:
            msg = "No results were found"
            raise ValueError(msg)

        results = yaml.safe_dump([result.model_dump(exclude_none=True) for result in response.results])

        prompt = f"""
        # Instructions
        We need to provide an apprioriately-detailed response to the user's query using only information from the results.
        We are not just summarizing the results, we are providing a detailed response to the user's query rooted in the results.
        Do not make/invent any information.

        # Context
        The user has performed a web search for `{query}`.
        A search was performed and the *ranked* results are as follows:
        ```
        {results}
        ```

        # Response
        {depth.to_prompt()}
        Your response will strive to answer the user's question with specific
        references to the results provided above. If the question has a simple answer that is strongly verified, it is
        totally appropriate to respond with a short response. Regardless of the length of your response, every single
        claim/concept/idea in your response should include a markdown link back to the page /section it came from.

        If there is ambiguity in the meaning of the user's query, you should also make suggestions for follow-up queries that the user
        could run depending on which potential meanings are most likely.
        """
        sampling_message = SamplingMessage(
            role="user",
            content=TextContent(type="text", text=prompt),
        )

        summary = await ctx.sample(
            messages=[sampling_message],
            temperature=0.0,
        )

        if not isinstance(summary, TextContent):
            msg = "No summary was generated"
            raise TypeError(msg)

        return SummaryResponse(
            summary=summary.text,
            results=response.results if include_results else None,
        )
