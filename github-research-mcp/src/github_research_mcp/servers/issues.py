from enum import Enum
from textwrap import dedent
from typing import Annotated, Any, Literal, Self

import yaml
from fastmcp import Context
from githubkit.github import GitHub
from mcp.types import ContentBlock, SamplingMessage, TextContent
from pydantic import BaseModel, Field

from github_research_mcp.clients.github import get_github_client
from github_research_mcp.models import Comment, Issue, PullRequest
from github_research_mcp.models.graphql.queries import GqlGetIssuesWithDetails, GqlSearchIssuesWithDetails
from github_research_mcp.models.query.base import AllKeywordsQualifier, AnyKeywordsQualifier, OwnerQualifier, RepoQualifier
from github_research_mcp.models.query.issue import IssueSearchQuery

OWNER = Annotated[str, "The owner of the repository."]
REPO = Annotated[str, "The name of the repository."]
KEYWORDS = Annotated[set[str], "The keywords of the issue."]
REQUIRE_ALL_KEYWORDS = Annotated[bool, "Whether all keywords must be present for a result to appear in the search results."]
STATE = Annotated[Literal["open", "closed", "all"], "The state of the issue."]
LABELS = Annotated[list[str] | None, "The labels of the issue."]
SORT = Annotated[Literal["created", "updated", "comments"], "The sort of the issue."]
DIRECTION = Annotated[Literal["asc", "desc"], "The direction of the issue."]
ISSUE_NUMBER = Annotated[int, "The number of the issue."]
PULL_REQUEST_NUMBER = Annotated[int, "The number of the pull request."]
PAGE = Annotated[int, "The page of the search results."]
PER_PAGE = Annotated[int, "The number of results per page."]
SUMMARY = Annotated[str, Field(description="The summary of the issue.")]

OWNER_OR_REPO = Annotated[OwnerQualifier | RepoQualifier, "The scope of the search, i.e. limited to a specific owner or repository."]

# Summary Fields
SUMMARY_LENGTH = Annotated["Length", Field(description="The length of the summary in words.")]
SUMMARY_FOCUS = Annotated[str, Field(description="The desired focus of the summary to be produced.")]
SEARCH_SUMMARY_FOCUS = Annotated[
    str,
    Field(
        description=(
            "The desired focus of the summary of the search results. "
            "If you are looking for related issues, be sure to include the body, title, etc. "
            "or at a minimum, significant details from the original issue in the focus."
        )
    ),
]

LIMIT_COMMENTS = Annotated[int, Field(description="The maximum number of comments to include in the summary.")]
LIMIT_RELATED_ITEMS = Annotated[int, Field(description="The maximum number of related items to include in the summary.")]
LIMIT_ISSUES = Annotated[int, Field(description="The maximum number of issues to include in the search results.")]


class Length(int, Enum):
    SHORT = 100
    MEDIUM = 500
    LONG = 1000


DEFAULT_COMMENT_LIMIT = 50
DEFAULT_RELATED_ITEMS_LIMIT = 20
DEFAULT_ISSUES_LIMIT = 100


class IssueWithDetails(BaseModel):
    issue: Issue
    comments: list[Comment]
    related: list[Issue | PullRequest]

    @classmethod
    def from_gql_get_issues_with_details(cls, gql_get_issues_with_details: GqlGetIssuesWithDetails) -> Self:
        return cls(
            issue=gql_get_issues_with_details.repository.issue,
            comments=gql_get_issues_with_details.repository.issue.comments.nodes,
            related=[node.source for node in gql_get_issues_with_details.repository.issue.timeline_items.nodes],
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


class IssuesServer:
    _client: GitHub[Any]

    def __init__(self, client: GitHub[Any] | None = None):
        self._client = client or get_github_client()

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

        graphql_response = await self._client.async_graphql(
            query=GqlGetIssuesWithDetails.graphql_query(),
            variables={
                "owner": owner,
                "repo": repo,
                "issue_number": issue_number,
                "limit_comments": limit_comments,
                "limit_events": limit_related_items,
            },
        )

        gql_get_issues_with_details = GqlGetIssuesWithDetails.model_validate(graphql_response)

        return IssueWithDetails.from_gql_get_issues_with_details(gql_get_issues_with_details=gql_get_issues_with_details)

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

        system_prompt = """
        {WHO_YOU_ARE}

        {DEEPLY_ROOTED}

        # Instructions

        You will be given an issue, its comments, and some basic info about related items.
        You will be given a "focus" for the summary, this is the topic that the user is most interested in.

        By default, your summary should include:
        1. Information about the issue, its state, age, etc.
        2. A description of the reported issue
        3. Additional information/corrections/findings related to the reported issue that occurred in the comments
        4. The resolution (or lack thereof) of the reported issue whether it was solved with a code change, documentation,
            closed as won't fix, closed as a duplicate, closed as a false positive, or closed as a false negative, etc.

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

        return IssueSummary(
            owner=owner,
            repo=repo,
            issue_number=issue_number,
            summary=summary.text,
        )

    async def research_issues_by_keywords(
        self,
        owner: OWNER,
        repo: REPO,
        keywords: KEYWORDS,
        require_all_keywords: REQUIRE_ALL_KEYWORDS = True,
        limit_issues: LIMIT_ISSUES = DEFAULT_ISSUES_LIMIT,
        limit_comments: LIMIT_COMMENTS = DEFAULT_COMMENT_LIMIT,
        limit_related_items: LIMIT_RELATED_ITEMS = DEFAULT_RELATED_ITEMS_LIMIT,
    ) -> list[IssueWithDetails]:
        """Search for issues in a repository."""

        search_query: IssueSearchQuery = IssueSearchQuery.from_repo_or_owner(owner=owner, repo=repo)

        search_query.add_qualifier(
            qualifier=AnyKeywordsQualifier(keywords=keywords) if require_all_keywords else AllKeywordsQualifier(keywords=keywords)
        )

        graphql_response: dict[str, Any] = await self._client.async_graphql(
            query=GqlSearchIssuesWithDetails.graphql_query(),
            variables=GqlSearchIssuesWithDetails.to_graphql_query_variables(
                query=search_query.to_query(), limit_issues=limit_issues, limit_comments=limit_comments, limit_events=limit_related_items
            ),
        )

        gql_search_issues_with_details = GqlSearchIssuesWithDetails.model_validate(graphql_response)

        return IssueWithDetails.from_gql_search_issues_with_details(gql_search_issues_with_details=gql_search_issues_with_details)

    async def summarize_issues_by_keywords(
        self,
        context: Context,
        owner: OWNER,
        repo: REPO,
        keywords: KEYWORDS,
        summary_focus: SUMMARY_FOCUS,
        summary_length: SUMMARY_LENGTH = Length.LONG,
        require_all_keywords: REQUIRE_ALL_KEYWORDS = True,
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

        system_prompt = """
        {WHO_YOU_ARE}

        {DEEPLY_ROOTED}

        # Instructions

        You will be given the user's search criteria, the issues which match the search criteria, and some basic info about them.

        The user will also provide a "focus" for the summary, this is the information, problem, etc. the user is hoping to context about
        in the results.

        By default, your summary should focus on the issues you determine are related to the user's focus. Issues should appear
        in order of most-related to least-related. At the end of the summary should be a concise list of the issue numbers that you
        analyzed but found to be unrelated.

        For related issues, you should include:
        1. Information about the issue including its title, state, age, and other relevant information
        2. A brief description of the reported issue and why you believe it relates to the user's focus.
        3. The specific details from the issue that you believe are related to the user's focus. Ideally enough information that
            the user should not have to look at the issue itself.
        """

        user_prompt = f"""
        # Focus
        {summary_focus}

        # Issue Search Results
        ```yaml
        {yaml.dump(issues)}
        ```
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

        return IssueSearchSummary(owner=owner, repo=repo, keywords=keywords, summary=summary.text)
