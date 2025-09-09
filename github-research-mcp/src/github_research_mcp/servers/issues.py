from textwrap import dedent
from typing import Annotated, Any, Literal, Self

import yaml
from fastmcp import Context
from fastmcp.utilities.logging import get_logger
from mcp.types import ContentBlock, SamplingMessage, TextContent
from pydantic import BaseModel, Field

from github_research_mcp.models import Comment, Issue, PullRequest
from github_research_mcp.models.graphql.queries import GqlGetIssuesWithDetails, GqlSearchIssuesWithDetails
from github_research_mcp.models.query.base import AllKeywordsQualifier, AnyKeywordsQualifier, StateQualifier
from github_research_mcp.models.query.issue import IssueSearchQuery
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

logger = get_logger(__name__)

KEYWORDS = Annotated[set[str], "The keywords to search for in the issue. You may only provide up to 6 keywords."]
REQUIRE_ALL_KEYWORDS = Annotated[bool, "Whether all keywords must be present for a result to appear in the search results."]
STATE = Annotated[Literal["open", "closed", "all"], "The state of the issue."]
ISSUE_NUMBER = Annotated[int, "The number of the issue."]


LIMIT_ISSUES = Annotated[int, Field(description="The maximum number of issues to include in the search results.")]


DEFAULT_COMMENT_LIMIT = 10
DEFAULT_RELATED_ITEMS_LIMIT = 5
DEFAULT_ISSUES_LIMIT = 50

DEFAULT_SEARCH_STATE = "all"


class IssueWithDetails(BaseModel):
    issue: Issue
    comments: list[Comment]
    related: list[Issue | PullRequest]

    @classmethod
    def from_gql_get_issues_with_details(cls, gql_get_issues_with_details: GqlGetIssuesWithDetails) -> Self:
        closed_by_pull_requests: list[PullRequest] = gql_get_issues_with_details.repository.issue.closed_by_pull_requests.nodes
        return cls(
            issue=gql_get_issues_with_details.repository.issue,
            comments=gql_get_issues_with_details.repository.issue.comments.nodes,
            related=[node.source for node in gql_get_issues_with_details.repository.issue.timeline_items.nodes] + closed_by_pull_requests,
        )

    @classmethod
    def from_gql_search_issues_with_details(cls, gql_search_issues_with_details: GqlSearchIssuesWithDetails) -> list[Self]:
        return [
            cls(
                issue=node,
                comments=node.comments.nodes,
                related=[node.source for node in node.timeline_items.nodes],
            )
            for node in gql_search_issues_with_details.search.nodes
        ]


class IssueWithTitle(BaseModel):
    number: int
    title: str

    @classmethod
    def from_issue(cls, issue: Issue) -> Self:
        return cls(number=issue.number, title=issue.title)


class IssueSummary(BaseModel):
    owner: str
    repo: str
    issue_number: int
    summary: str


class IssueSearchSummary(BaseModel):
    owner: str
    repo: str
    keywords: set[str]
    summary: str
    issues_reviewed: list[IssueWithTitle]


class IssuesServer(BaseServer):
    async def research_issue(
        self,
        owner: OWNER,
        repo: REPO,
        issue_number: ISSUE_NUMBER,
        limit_comments: LIMIT_COMMENTS = DEFAULT_COMMENT_LIMIT,
        limit_related_items: LIMIT_RELATED_ITEMS = DEFAULT_RELATED_ITEMS_LIMIT,
    ) -> IssueWithDetails:
        """Get information (body, comments, related issues and pull requests) about a specific issue in the repository."""
        from github_research_mcp.models.graphql.queries import GqlGetIssuesWithDetails

        gql_get_issues_with_details: GqlGetIssuesWithDetails = await self._perform_query(
            query_model=GqlGetIssuesWithDetails,
            variables={
                "owner": owner,
                "repo": repo,
                "issue_number": issue_number,
                "limit_comments": limit_comments,
                "limit_events": limit_related_items,
            },
        )

        issue_with_details: IssueWithDetails = IssueWithDetails.from_gql_get_issues_with_details(
            gql_get_issues_with_details=gql_get_issues_with_details
        )

        logger.info(f"Research issue response for {owner}/{repo}#{issue_number} is {estimate_model_tokens(issue_with_details)} tokens.")

        return issue_with_details

    async def summarize_issue(
        self,
        context: Context,
        owner: OWNER,
        repo: REPO,
        issue_number: ISSUE_NUMBER,
        summary_focus: SUMMARY_FOCUS | None = None,
        summary_length: SUMMARY_LENGTH = Length.MEDIUM,
        limit_comments: LIMIT_COMMENTS = DEFAULT_COMMENT_LIMIT,
        limit_related_items: LIMIT_RELATED_ITEMS = DEFAULT_RELATED_ITEMS_LIMIT,
    ) -> IssueSummary:
        """Produce a "focus"-ed summary of a specific issue incorporating the comments, related items, and the issue itself."""

        issue_details = await self.research_issue(
            owner=owner, repo=repo, issue_number=issue_number, limit_comments=limit_comments, limit_related_items=limit_related_items
        )

        system_prompt = f"""
        {PREAMBLE}

        # Instructions

        You will be given an issue, its comments, and some basic info about related items.
        You will be given a "focus" for the summary, this is the topic that the user is most interested in.

        By default, your summary should include:
        1. Information about the issue, its state, age, etc.
        2. A description of the reported issue
        3. Additional information/corrections/findings related to the reported issue that occurred in the comments
        4. The resolution (or lack thereof) of the reported issue whether it was solved with a code change, documentation,
            closed as won't fix, closed as a duplicate, closed as a false positive, or closed as a false negative, etc. Pay
            careful attention to the state of any related items before making any conclusions.

        That being said, what the user asks for in the `focus` should be prioritized over the default summary.
        """

        max_comments_reached = len(issue_details.comments) >= limit_comments
        max_related_items_reached = len(issue_details.related) >= limit_related_items

        user_prompt = f"""
        # Focus
        {summary_focus if summary_focus else "No specific focus provided"}

        # Issue
        ```yaml
        {yaml.dump(issue_details.issue.model_dump())}
        ```

        # Comments
        {f"There were more than {limit_comments} comments, only the first {limit_comments} are included below:" if max_comments_reached else ""}
        ```yaml
        {yaml.dump(issue_details.comments)}
        ```

        # Related Items
        {f"There were more than {limit_related_items} related items, only the first {limit_related_items} are included below:" if max_related_items_reached else ""}
        ```yaml
        {yaml.dump(issue_details.related)}
        ```

        # Length
        The user has requested you limit the summary to roughly {summary_length} words but if accurately summarizing the issue requires
        more words, you should use more words. If accurately summarizing the issue can be done in fewer words, you should use
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
            msg = "The sampling call failed to generate a valid text summary of the issue."
            raise TypeError(msg)

        issue_summary: IssueSummary = IssueSummary(
            owner=owner,
            repo=repo,
            issue_number=issue_number,
            summary=summary.text,
        )

        logger.info(f"Summary response for {owner}/{repo}#{issue_number} is {estimate_model_tokens(issue_summary)} tokens.")

        return issue_summary

    async def research_issues_by_keywords(
        self,
        owner: OWNER,
        repo: REPO,
        keywords: KEYWORDS,
        require_all_keywords: REQUIRE_ALL_KEYWORDS = False,
        state: STATE = DEFAULT_SEARCH_STATE,
        limit_issues: LIMIT_ISSUES = DEFAULT_ISSUES_LIMIT,
        limit_comments: LIMIT_COMMENTS = DEFAULT_COMMENT_LIMIT,
        limit_related_items: LIMIT_RELATED_ITEMS = DEFAULT_RELATED_ITEMS_LIMIT,
    ) -> list[IssueWithDetails]:
        """Search for issues in a repository."""

        search_query: IssueSearchQuery = IssueSearchQuery.from_repo_or_owner(owner=owner, repo=repo)

        search_query.add_qualifier(
            qualifier=AllKeywordsQualifier(keywords=keywords) if require_all_keywords else AnyKeywordsQualifier(keywords=keywords)
        )

        if state != "all":
            search_query.add_qualifier(StateQualifier(state=state))

        graphql_response: dict[str, Any] = await self._client.async_graphql(
            query=GqlSearchIssuesWithDetails.graphql_query(),
            variables=GqlSearchIssuesWithDetails.to_graphql_query_variables(
                query=search_query.to_query(), limit_issues=limit_issues, limit_comments=limit_comments, limit_events=limit_related_items
            ),
        )

        gql_search_issues_with_details = GqlSearchIssuesWithDetails.model_validate(graphql_response)

        issue_with_details: list[IssueWithDetails] = IssueWithDetails.from_gql_search_issues_with_details(
            gql_search_issues_with_details=gql_search_issues_with_details
        )

        logger.info(f"Research issues by keywords response for {owner}/{repo} is {estimate_model_tokens(issue_with_details)} tokens.")

        return issue_with_details

    async def summarize_issues_by_keywords(
        self,
        context: Context,
        owner: OWNER,
        repo: REPO,
        keywords: KEYWORDS,
        summary_focus: SUMMARY_FOCUS,
        summary_length: SUMMARY_LENGTH = Length.LONG,
        require_all_keywords: REQUIRE_ALL_KEYWORDS = False,
        limit_issues: LIMIT_ISSUES = DEFAULT_ISSUES_LIMIT,
        limit_comments: LIMIT_COMMENTS = DEFAULT_COMMENT_LIMIT,
        limit_related_items: LIMIT_RELATED_ITEMS = DEFAULT_RELATED_ITEMS_LIMIT,
    ) -> IssueSearchSummary:
        """Summarize the results of a search for issues in a repository."""

        issues: list[IssueWithDetails] = await self.research_issues_by_keywords(
            owner=owner,
            repo=repo,
            keywords=keywords,
            require_all_keywords=require_all_keywords,
            limit_issues=limit_issues,
            limit_comments=limit_comments,
            limit_related_items=limit_related_items,
        )

        issues_with_title: list[IssueWithTitle] = [IssueWithTitle.from_issue(detailed_issue.issue) for detailed_issue in issues]

        system_prompt = f"""
        {PREAMBLE}

        # Instructions

        You will be given the user's search criteria, the issues which match the search criteria, and some basic info about them.

        The user will also provide a "focus" for the summary, this is the information, problem, etc. the user is hoping to context about
        in the results.
        """

        user_prompt = f"""
        # Issue Search Results
        ``````yaml
        {yaml.dump(issues)}
        ``````

        # Focus
        The user has asked that you specifically focus your review of the issue search results on the following aspects:
        {summary_focus}

        # Summary Instructions

        By default, your summary should focus on the issues you determine are related to the user's focus. Issues should appear
        in order of most-related to least-related.

        For related issues, you should include:
        1. Information about the issue including its title, state, age, and other relevant information
        2. Every important detail from the issue, related comments, or related Pull Requests that relate to the user's focus.
            Ideally enough information that the user should not have to look at the issue itself. This is your chance to provide
            the key context the use is looking for. If it's not extremely obvious that it relates to the user's focus, you should
            provide a brief explanation of why you believe it relates to the user's focus. If the issue is highly related to the user's
            focus, you should provide significantly more information about it.
        3. The resolution (or lack thereof) of the reported issue whether it was solved with a code change, documentation,
            closed as won't fix, closed as a duplicate, closed as a false positive, or closed as a false negative, etc. Pay
            careful attention to the state of any related items before making any conclusions.

        You should organize your results into high confidence of relation, medium confidence of relation.
        You should not mention issues that you have low confidence or no confidence in relation to the topic of the user's focus.

        The user will receive the list of issues you determine are not related to the topic of the user's focus and they can always
        investigate any of the issues if they determine you were wrong.

        You will double check your results against the user's focus to ensure that the issues you report as related are actually related
        to the user's focus.
        """

        sampling_message: SamplingMessage = SamplingMessage(role="user", content=TextContent(type="text", text=dedent(user_prompt)))

        summary: ContentBlock = await context.sample(
            system_prompt=system_prompt,
            messages=[sampling_message],
            temperature=0.0,
            max_tokens=summary_length.value * 10,  # Allow up to 2.5x the length requested.
        )

        if not isinstance(summary, TextContent):
            msg = "The sampling call failed to generate a valid text summary of the issue search results."
            raise TypeError(msg)

        issue_search_summary: IssueSearchSummary = IssueSearchSummary(
            owner=owner, repo=repo, keywords=keywords, summary=summary.text, issues_reviewed=issues_with_title
        )

        logger.info(f"Summarize issues by keywords response for {owner}/{repo} is {estimate_model_tokens(issue_search_summary)} tokens.")

        return issue_search_summary
