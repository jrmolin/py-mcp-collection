from textwrap import dedent
from typing import TYPE_CHECKING, Annotated, Any, Literal, Self

import yaml
from fastmcp import Context
from fastmcp.utilities.logging import get_logger
from githubkit.versions.v2022_11_28.models.group_0238 import DiffEntry
from mcp.types import ContentBlock, SamplingMessage, TextContent
from pydantic import BaseModel, Field

from github_research_mcp.models import Comment, Issue, PullRequest
from github_research_mcp.models.graphql.queries import (
    GqlGetPullRequestWithDetails,
    GqlSearchPullRequestsWithDetails,
)
from github_research_mcp.models.query.base import AllKeywordsQualifier, AnyKeywordsQualifier, StateQualifier
from github_research_mcp.models.query.pull_request import PullRequestSearchQuery
from github_research_mcp.sampling.prompts import PREAMBLE
from github_research_mcp.servers.base import BaseServer
from github_research_mcp.servers.shared.annotations import (
    LIMIT_COMMENTS,
    LIMIT_RELATED_ITEMS,
    OWNER,
    REPO,
    SUMMARY_FOCUS,
    SUMMARY_LENGTH,
    Length,
)
from github_research_mcp.servers.shared.utility import estimate_model_tokens

if TYPE_CHECKING:
    from githubkit.response import Response
    from githubkit.versions.v2022_11_28.types.group_0238 import DiffEntryType

logger = get_logger(__name__)

KEYWORDS = Annotated[set[str], "The keywords to search for in the pull request. You may only provide up to 6 keywords."]
REQUIRE_ALL_KEYWORDS = Annotated[bool, "Whether all keywords must be present for a result to appear in the search results."]
STATE = Annotated[Literal["open", "closed", "all"], "The state of the pull request."]
PULL_REQUEST_NUMBER = Annotated[int, "The number of the pull request."]


LIMIT_PULL_REQUESTS = Annotated[int, Field(description="The maximum number of pull requests to include in the search results.")]


DEFAULT_COMMENT_LIMIT = 10
DEFAULT_RELATED_ITEMS_LIMIT = 5
DEFAULT_PULL_REQUESTS_LIMIT = 50

DEFAULT_SEARCH_STATE = "all"


class PullRequestFileDiff(BaseModel):
    path: str
    sha: str | None
    status: Literal["added", "removed", "modified", "renamed", "copied", "changed", "unchanged"]
    patch: str | None

    @classmethod
    def from_diff_entry(cls, diff_entry: DiffEntry) -> Self:
        return cls(
            path=diff_entry.filename,
            sha=diff_entry.sha,
            status=diff_entry.status,
            patch=diff_entry.patch if diff_entry.patch else None,
        )


class PullRequestDiff(BaseModel):
    owner: str
    repo: str
    pull_request_number: int
    diffs: list[PullRequestFileDiff]


class PullRequestWithDetails(BaseModel):
    pull_request: PullRequest
    comments: list[Comment]
    related: list[Issue | PullRequest]

    @classmethod
    def from_gql_get_pull_request_with_details(cls, gql_get_pull_request_with_details: GqlGetPullRequestWithDetails) -> Self:
        return cls(
            pull_request=gql_get_pull_request_with_details.repository.pull_request,
            comments=gql_get_pull_request_with_details.repository.pull_request.comments.nodes,
            related=[node.source for node in gql_get_pull_request_with_details.repository.pull_request.timeline_items.nodes],
        )

    @classmethod
    def from_gql_search_pull_requests_with_details(
        cls, gql_search_pull_requests_with_details: GqlSearchPullRequestsWithDetails
    ) -> list[Self]:
        return [
            cls(
                pull_request=node,
                comments=node.comments.nodes,
                related=[node.source for node in node.timeline_items.nodes],
            )
            for node in gql_search_pull_requests_with_details.search.nodes
        ]


class PullRequestWithTitle(BaseModel):
    number: int
    title: str

    @classmethod
    def from_pull_request(cls, pull_request: PullRequest) -> Self:
        return cls(number=pull_request.number, title=pull_request.title)


class PullRequestDetailsWithDiff(BaseModel):
    details: PullRequestWithDetails
    diff: PullRequestDiff


class PullRequestSummary(BaseModel):
    owner: str
    repo: str
    pull_request_number: int
    summary: str


class PullRequestSearchSummary(BaseModel):
    owner: str
    repo: str
    keywords: set[str]
    summary: str
    pull_requests_reviewed: list[PullRequestWithTitle]


class PullRequestsServer(BaseServer):
    async def _get_pull_request_diff(
        self,
        owner: OWNER,
        repo: REPO,
        pull_request_number: PULL_REQUEST_NUMBER,
    ) -> PullRequestDiff:
        """Get the diff of a specific pull request in the repository."""
        response: Response[list[DiffEntry], list[DiffEntryType]] = await self._client.rest.pulls.async_list_files(
            owner=owner, repo=repo, pull_number=pull_request_number
        )

        response_models: list[DiffEntry] = response.parsed_data

        pull_request_diff: PullRequestDiff = PullRequestDiff(
            owner=owner,
            repo=repo,
            pull_request_number=pull_request_number,
            diffs=[PullRequestFileDiff.from_diff_entry(diff_entry) for diff_entry in response_models],
        )

        return pull_request_diff

    async def research_pull_request(
        self,
        owner: OWNER,
        repo: REPO,
        pull_request_number: PULL_REQUEST_NUMBER,
        limit_comments: LIMIT_COMMENTS = DEFAULT_COMMENT_LIMIT,
        limit_related_items: LIMIT_RELATED_ITEMS = DEFAULT_RELATED_ITEMS_LIMIT,
    ) -> PullRequestDetailsWithDiff:
        """Get information (body, comments, related issues and pull requests) about a specific pull request in the
        repository along with the code diff of the pull request."""
        from github_research_mcp.models.graphql.queries import GqlGetPullRequestWithDetails

        gql_get_pull_request_with_details: GqlGetPullRequestWithDetails = await self._perform_query(
            query_model=GqlGetPullRequestWithDetails,
            variables=GqlGetPullRequestWithDetails.to_graphql_query_variables(
                owner=owner,
                repo=repo,
                pull_request_number=pull_request_number,
                limit_comments=limit_comments,
                limit_events=limit_related_items,
            ),
        )

        pull_request_diff: PullRequestDiff = await self._get_pull_request_diff(
            owner=owner,
            repo=repo,
            pull_request_number=pull_request_number,
        )

        pull_request_with_details: PullRequestWithDetails = PullRequestWithDetails.from_gql_get_pull_request_with_details(
            gql_get_pull_request_with_details=gql_get_pull_request_with_details,
        )

        logger.info(
            f"Research pull request response for {owner}/{repo}#{pull_request_number} is {estimate_model_tokens(pull_request_with_details)} tokens."
        )

        return PullRequestDetailsWithDiff(details=pull_request_with_details, diff=pull_request_diff)

    async def summarize_pull_request(
        self,
        context: Context,
        owner: OWNER,
        repo: REPO,
        pull_request_number: PULL_REQUEST_NUMBER,
        summary_focus: SUMMARY_FOCUS | None = None,
        summary_length: SUMMARY_LENGTH = Length.MEDIUM,
        limit_comments: LIMIT_COMMENTS = DEFAULT_COMMENT_LIMIT,
        limit_related_items: LIMIT_RELATED_ITEMS = DEFAULT_RELATED_ITEMS_LIMIT,
    ) -> PullRequestSummary:
        """Produce a "focus"-ed summary of a specific pull request incorporating the comments, related items,
        the pull request itself, and the code diff of the pull request."""

        pull_request_details = await self.research_pull_request(
            owner=owner,
            repo=repo,
            pull_request_number=pull_request_number,
            limit_comments=limit_comments,
            limit_related_items=limit_related_items,
        )

        system_prompt = f"""
        {PREAMBLE}

        # Instructions

        You will be given a pull request, its comments, and some basic info about related items.
        You will be given a "focus" for the summary, this is the topic that the user is most interested in.

        By default, your summary should include:
        1. Information about the pull request, its state, age, etc.
        2. A description of the reported pull request
        3. Additional information/corrections/findings related to the reported pull request that occurred in the comments
        4. The resolution (or lack thereof) of the reported issue whether it was solved with a code change, documentation,
            closed as won't fix, closed as a duplicate, closed as a false positive, or closed as a false negative, etc. Pay
            careful attention to the state of any related items before making any conclusions.

        That being said, what the user asks for in the `focus` should be prioritized over the default summary.
        """

        max_comments_reached = len(pull_request_details.details.comments) >= limit_comments
        max_related_items_reached = len(pull_request_details.details.related) >= limit_related_items

        user_prompt = f"""
        # Focus
        {summary_focus if summary_focus else "No specific focus provided"}

        # Pull Request
        ```yaml
        {yaml.dump(pull_request_details.details.pull_request.model_dump())}
        ```

        # Pull Request Diff
        ```yaml
        {yaml.dump(pull_request_details.diff.model_dump())}
        ```

        # Comments
        {f"There were more than {limit_comments} comments, only the first {limit_comments} are included below:" if max_comments_reached else ""}
        ```yaml
        {yaml.dump(pull_request_details.details.comments)}
        ```

        # Related Items
        {f"There were more than {limit_related_items} related items, only the first {limit_related_items} are included below:" if max_related_items_reached else ""}
        ```yaml
        {yaml.dump(pull_request_details.details.related)}
        ```

        # Length
        The user has requested you limit the summary to roughly {summary_length} words but if accurately summarizing the pull request requires
        more words, you should use more words. If accurately and fully summarizing the pull request can be done in fewer words, you should use
        fewer words.
        """  # noqa: E501

        sampling_message = SamplingMessage(role="user", content=TextContent(type="text", text=dedent(user_prompt)))

        summary: ContentBlock = await context.sample(
            system_prompt=system_prompt,
            messages=[sampling_message],
            temperature=0.0,
            max_tokens=summary_length.value * 10,  # Allow up to 2.5x the length requested.
        )

        if not isinstance(summary, TextContent):
            msg = "The sampling call failed to generate a valid text summary of the pull request."
            raise TypeError(msg)

        pull_request_summary: PullRequestSummary = PullRequestSummary(
            owner=owner,
            repo=repo,
            pull_request_number=pull_request_number,
            summary=summary.text,
        )

        logger.info(f"Summary response for {owner}/{repo}#{pull_request_number} is {estimate_model_tokens(pull_request_summary)} tokens.")

        return pull_request_summary

    async def research_pull_requests_by_keywords(
        self,
        owner: OWNER,
        repo: REPO,
        keywords: KEYWORDS,
        require_all_keywords: REQUIRE_ALL_KEYWORDS = False,
        state: STATE = DEFAULT_SEARCH_STATE,
        limit_pull_requests: LIMIT_PULL_REQUESTS = DEFAULT_PULL_REQUESTS_LIMIT,
        limit_comments: LIMIT_COMMENTS = DEFAULT_COMMENT_LIMIT,
        limit_related_items: LIMIT_RELATED_ITEMS = DEFAULT_RELATED_ITEMS_LIMIT,
    ) -> list[PullRequestWithDetails]:
        """Search for pull requests in a repository."""

        search_query: PullRequestSearchQuery = PullRequestSearchQuery.from_repo_or_owner(owner=owner, repo=repo)

        search_query.add_qualifier(
            qualifier=AllKeywordsQualifier(keywords=keywords) if require_all_keywords else AnyKeywordsQualifier(keywords=keywords)
        )

        if state != "all":
            search_query.add_qualifier(StateQualifier(state=state))

        graphql_response: dict[str, Any] = await self._client.async_graphql(
            query=GqlSearchPullRequestsWithDetails.graphql_query(),
            variables=GqlSearchPullRequestsWithDetails.to_graphql_query_variables(
                query=search_query.to_query(),
                limit_pull_requests=limit_pull_requests,
                limit_comments=limit_comments,
                limit_events=limit_related_items,
            ),
        )

        gql_search_pull_requests_with_details = GqlSearchPullRequestsWithDetails.model_validate(graphql_response)

        pull_request_with_details: list[PullRequestWithDetails] = PullRequestWithDetails.from_gql_search_pull_requests_with_details(
            gql_search_pull_requests_with_details=gql_search_pull_requests_with_details
        )

        logger.info(
            f"Research pull requests by keywords response for {owner}/{repo} is {estimate_model_tokens(pull_request_with_details)} tokens."
        )

        return pull_request_with_details

    async def summarize_pull_requests_by_keywords(
        self,
        context: Context,
        owner: OWNER,
        repo: REPO,
        keywords: KEYWORDS,
        summary_focus: SUMMARY_FOCUS,
        summary_length: SUMMARY_LENGTH = Length.LONG,
        require_all_keywords: REQUIRE_ALL_KEYWORDS = False,
        limit_pull_requests: LIMIT_PULL_REQUESTS = DEFAULT_PULL_REQUESTS_LIMIT,
        limit_comments: LIMIT_COMMENTS = DEFAULT_COMMENT_LIMIT,
        limit_related_items: LIMIT_RELATED_ITEMS = DEFAULT_RELATED_ITEMS_LIMIT,
        include_pull_request_diffs: Literal[False] = False,  # noqa: ARG002
    ) -> PullRequestSearchSummary:
        """Summarize the results of a search for pull requests in a repository."""

        pull_requests: list[PullRequestWithDetails] = await self.research_pull_requests_by_keywords(
            owner=owner,
            repo=repo,
            keywords=keywords,
            require_all_keywords=require_all_keywords,
            limit_pull_requests=limit_pull_requests,
            limit_comments=limit_comments,
            limit_related_items=limit_related_items,
        )

        pull_requests_with_title: list[PullRequestWithTitle] = [
            PullRequestWithTitle.from_pull_request(detailed_pull_request.pull_request) for detailed_pull_request in pull_requests
        ]

        system_prompt = f"""
        {PREAMBLE}

        # Instructions

        You will be given the user's search criteria, the pull requests which match the search criteria, and some basic info about them.

        The user will also provide a "focus" for the summary, this is the information, problem, etc. the user is hoping to context about
        in the results.
        """

        user_prompt = f"""
        # Pull Request Search Results
        ``````yaml
        {yaml.dump(pull_requests)}
        ``````

        # Focus
        The user has asked that you specifically focus your review of the pull request search results on the following aspects:
        {summary_focus}

        # Summary Instructions

        By default, your summary should focus on the pull requests you determine are related to the user's focus. Pull requests should appear
        in order of most-related to least-related.

        For related pull requests, you should include:
        1. Information about the pull request including its title, state, age, and other relevant information
        2. Every important detail from the pull request, related comments, or related Pull Requests that relate to the user's focus.
            Ideally enough information that the user should not have to look at the pull request itself. This is your chance to provide
            the key context the use is looking for. If it's not extremely obvious that it relates to the user's focus, you should
            provide a brief explanation of why you believe it relates to the user's focus. If the pull request is highly related to the user's
            focus, you should provide significantly more information about it. If the pull request and comments do not contain any information
            indicate in the summary that the body/comments do not provide information and understanding the Pull Request may require looking
            at the code diff in the Pull Request.
        3. The resolution (or lack thereof) of the reported pull request whether it was solved with a code change, documentation,
            closed as won't fix, closed as a duplicate, closed as a false positive, or closed as a false negative, etc. Pay
            careful attention to the state of any related items before making any conclusions.

        You should organize your results into high confidence of relation, medium confidence of relation.
        You should not mention pull requests that you have low confidence or no confidence in relation to the topic of the user's focus.

        The user will receive the list of pull requests you determine are not related to the topic of the user's focus and they can always
        investigate any of the pull requests if they determine you were wrong.

        You will double check your results against the user's focus to ensure that the pull requests you report as related are actually
        related to the user's focus.
        """

        sampling_message: SamplingMessage = SamplingMessage(role="user", content=TextContent(type="text", text=dedent(user_prompt)))

        summary: ContentBlock = await context.sample(
            system_prompt=system_prompt,
            messages=[sampling_message],
            temperature=0.0,
            max_tokens=summary_length.value * 10,  # Allow up to 2.5x the length requested.
        )

        if not isinstance(summary, TextContent):
            msg = "The sampling call failed to generate a valid text summary of the pull request search results."
            raise TypeError(msg)

        pull_request_search_summary: PullRequestSearchSummary = PullRequestSearchSummary(
            owner=owner, repo=repo, keywords=keywords, summary=summary.text, pull_requests_reviewed=pull_requests_with_title
        )

        logger.info(
            f"Summarize pull requests by keywords response for {owner}/{repo} is {estimate_model_tokens(pull_request_search_summary)} tokens."
        )

        return pull_request_search_summary
