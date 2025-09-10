from typing import Annotated, Any, Literal, Self

import yaml
from fastmcp.utilities.logging import get_logger
from githubkit.github import GitHub
from pydantic import BaseModel, Field
from pydantic.root_model import RootModel

from github_research_mcp.models import Comment, Issue, PullRequest
from github_research_mcp.models.graphql.queries import (
    GqlGetIssueOrPullRequestsWithDetails,
    GqlIssueWithDetails,
    GqlSearchIssueOrPullRequestsWithDetails,
)
from github_research_mcp.models.query.base import AllKeywordsQualifier, AnyKeywordsQualifier, StateQualifier
from github_research_mcp.models.query.issue_or_pull_request import IssueOrPullRequestSearchQuery
from github_research_mcp.sampling.prompts import PREAMBLE
from github_research_mcp.servers.base import BaseResponseModel, BaseServer
from github_research_mcp.servers.repository import RepositoryServer, RepositorySummary
from github_research_mcp.servers.shared.annotations import (
    LIMIT_COMMENTS,
    LIMIT_RELATED_ITEMS,
    OWNER,
    REPO,
    SEARCH_SUMMARY_FOCUS,
    SUMMARY_FOCUS,
)

logger = get_logger(__name__)

SEARCH_KEYWORDS = Annotated[
    set[str],
    "The keywords to use to search for issues. Picking keywords is important as only issues containing these "
    "keywords will be included in the search results. You may only provide up to 6 keywords.",
]
SUMMARY_KEYWORDS = Annotated[
    set[str],
    "The keywords to use to search for issues. Picking keywords is important as only issues containing these "
    "keywords will be reviewed to produce the summary. You may only provide up to 6 keywords.",
]
REQUIRE_ALL_KEYWORDS = Annotated[bool, "Whether all keywords must be present for a result to appear in the search results."]
STATE = Annotated[Literal["open", "closed", "all"], "The state of the issue."]

ISSUE_OR_PR_NUMBER = Annotated[int, "The number of the issue or pull request."]

LIMIT_ISSUES_OR_PULL_REQUESTS = Annotated[
    int, Field(description="The maximum number of issues or pull requests to include in the search results.")
]


DEFAULT_COMMENT_LIMIT = 10
DEFAULT_RELATED_ITEMS_LIMIT = 5
DEFAULT_ISSUES_OR_PULL_REQUESTS_LIMIT = 50

DEFAULT_SEARCH_STATE = "all"


class IssueOrPullRequestWithDetails(BaseResponseModel):
    issue_or_pr: Issue | PullRequest
    comments: list[Comment]
    related: list[Issue | PullRequest]

    @classmethod
    def from_gql_get_issue_or_pull_requests_with_details(
        cls, gql_get_issue_or_pull_requests_with_details: GqlGetIssueOrPullRequestsWithDetails
    ) -> Self:
        gql_issue_or_pull_request = gql_get_issue_or_pull_requests_with_details.repository.issue_or_pull_request

        issue_or_pull_request = (
            gql_issue_or_pull_request.to_issue()
            if isinstance(gql_issue_or_pull_request, GqlIssueWithDetails)
            else gql_issue_or_pull_request.to_pull_request()
        )

        return cls(
            issue_or_pr=issue_or_pull_request,
            comments=gql_issue_or_pull_request.comments.nodes,
            related=[node.source for node in gql_issue_or_pull_request.timeline_items.nodes],
        )

    @classmethod
    def from_gql_search_issue_or_pull_requests_with_details(
        cls, gql_search_issue_or_pull_requests_with_details: GqlSearchIssueOrPullRequestsWithDetails
    ) -> list[Self]:
        results = []

        for node in gql_search_issue_or_pull_requests_with_details.search.nodes:
            issue_or_pull_request = node.to_issue() if isinstance(node, GqlIssueWithDetails) else node.to_pull_request()

            results.append(
                cls(
                    issue_or_pr=issue_or_pull_request,
                    comments=node.comments.nodes,
                    related=[node.source for node in node.timeline_items.nodes],
                )
            )

        return results


class TitleByIssueOrPullRequestInfo(RootModel[dict[str, str]]):
    @classmethod
    def from_issues_or_pull_requests(cls, issues_or_pull_requests: list[Issue | PullRequest]) -> Self:
        issues_or_pull_requests_by_info = {}

        for issue_or_pull_request in issues_or_pull_requests:
            key = "issue" if isinstance(issue_or_pull_request, Issue) else "pull_request"
            key: str = f"{key}:{issue_or_pull_request.number}"

            issues_or_pull_requests_by_info[key] = issue_or_pull_request.title

        return cls(root=issues_or_pull_requests_by_info)


class IssueOrPullRequestSummary(BaseModel):
    owner: str
    repo: str
    issue_or_pr_number: int
    summary: str


class IssueSearchSummary(BaseModel):
    owner: str
    repo: str
    keywords: set[str]
    summary: str
    items_reviewed: TitleByIssueOrPullRequestInfo


class IssuesOrPullRequestsServer(BaseServer):
    repository_server: RepositoryServer

    def __init__(self, github_client: GitHub[Any], repository_server: RepositoryServer):
        self.github_client = github_client
        self.repository_server = repository_server

    async def research_issue_or_pull_request(
        self,
        owner: OWNER,
        repo: REPO,
        issue_or_pr_number: ISSUE_OR_PR_NUMBER,
        limit_comments: LIMIT_COMMENTS = DEFAULT_COMMENT_LIMIT,
        limit_related_items: LIMIT_RELATED_ITEMS = DEFAULT_RELATED_ITEMS_LIMIT,
    ) -> IssueOrPullRequestWithDetails:
        """Get information (body, comments, related issues and pull requests) about a specific issue or pull request in the repository."""

        query_variables = GqlGetIssueOrPullRequestsWithDetails.to_graphql_query_variables(
            owner=owner,
            repo=repo,
            issue_or_pr_number=issue_or_pr_number,
            limit_comments=limit_comments,
            limit_events=limit_related_items,
        )

        gql_get_issue_or_pull_requests_with_details: GqlGetIssueOrPullRequestsWithDetails = await self._perform_graphql_query(
            query_model=GqlGetIssueOrPullRequestsWithDetails,
            variables=query_variables,
        )

        return IssueOrPullRequestWithDetails.from_gql_get_issue_or_pull_requests_with_details(
            gql_get_issue_or_pull_requests_with_details=gql_get_issue_or_pull_requests_with_details
        )

    async def summarize_issue_or_pull_request(
        self,
        owner: OWNER,
        repo: REPO,
        issue_or_pr_number: ISSUE_OR_PR_NUMBER,
        summary_focus: SUMMARY_FOCUS | None = None,
        limit_comments: LIMIT_COMMENTS = DEFAULT_COMMENT_LIMIT,
        limit_related_items: LIMIT_RELATED_ITEMS = DEFAULT_RELATED_ITEMS_LIMIT,
    ) -> IssueOrPullRequestSummary:
        """Produce a "focus"-ed summary of a specific issue incorporating the comments, related items, and the issue itself."""

        issue_details: IssueOrPullRequestWithDetails = await self.research_issue_or_pull_request(
            owner=owner,
            repo=repo,
            issue_or_pr_number=issue_or_pr_number,
            limit_comments=limit_comments,
            limit_related_items=limit_related_items,
        )

        repository_summary: RepositorySummary = await self.repository_server.summarize(
            owner=owner,
            repo=repo,
        )

        system_prompt = f"""
        {PREAMBLE}

        # Instructions

        You will be given an issue or pull request, its comments, and some basic info about related items.
        You will be given a "focus" for the summary, this is the topic that the user is most interested in.

        By default, your summary should include:
        1. Information about the issue or pull request, its state, age, etc.
        2. A description of the reported issue or pull request
        3. Additional information/corrections/findings related to the reported issue that occurred in the comments
        4. The resolution (or lack thereof) of the reported issue whether it was solved with a code change, documentation,
            closed as won't fix, closed as a duplicate, closed as a false positive, or closed as a false negative, etc. Pay
            careful attention to the state of any related items before making any conclusions.

        That being said, what the user asks for in the `focus` should be prioritized over the default summary.
        """

        max_comments_reached = len(issue_details.comments) >= limit_comments
        max_related_items_reached = len(issue_details.related) >= limit_related_items

        comment_warning = (
            f"There were more than {limit_comments} comments, only the first {limit_comments} are included below:"
            if max_comments_reached
            else ""
        )
        related_items_warning = (
            f"There were more than {limit_related_items} related items, only the first {limit_related_items} are included below:"
            if max_related_items_reached
            else ""
        )

        user_prompt = f"""
        # Repository Background Information
        ```
        {repository_summary.root}
        ```

        # Focus
        {summary_focus if summary_focus else "No specific focus provided"}

        # Issue
        ```yaml
        {yaml.dump(issue_details.issue_or_pr.model_dump())}
        ```

        # Comments
        {comment_warning}
        ```yaml
        {yaml.dump(issue_details.comments)}
        ```

        # Related Items
        {related_items_warning}
        ```yaml
        {yaml.dump(issue_details.related)}
        ```

        # Length
        The user has requested you limit the summary to roughly 4000 words but if accurately summarizing the issue requires
        more words, you should use more words. If accurately summarizing the issue can be done in fewer words, you should use
        fewer words.
        """

        summary: str = await self._sample(
            system_prompt=system_prompt,
            messages=user_prompt,
        )

        return IssueOrPullRequestSummary(
            owner=owner,
            repo=repo,
            issue_or_pr_number=issue_or_pr_number,
            summary=summary,
        )

    async def research_issues_or_pull_requests(
        self,
        owner: OWNER,
        repo: REPO,
        issue_or_pr: Literal["issue", "pull_request"],
        keywords: SEARCH_KEYWORDS,
        require_all_keywords: REQUIRE_ALL_KEYWORDS = False,
        state: STATE = DEFAULT_SEARCH_STATE,
        limit_issues_or_pull_requests: LIMIT_ISSUES_OR_PULL_REQUESTS = DEFAULT_ISSUES_OR_PULL_REQUESTS_LIMIT,
        limit_comments: LIMIT_COMMENTS = DEFAULT_COMMENT_LIMIT,
        limit_related_items: LIMIT_RELATED_ITEMS = DEFAULT_RELATED_ITEMS_LIMIT,
    ) -> list[IssueOrPullRequestWithDetails]:
        """Search for issues in a repository by keywords. Only issues containing the keywords will be included in the search results.

        For each issue, comments, and related items will also be gathered and included in the response."""

        search_query: IssueOrPullRequestSearchQuery = IssueOrPullRequestSearchQuery.from_repo_or_owner(
            owner=owner, repo=repo, issue_or_pull_request=issue_or_pr
        )

        search_query.add_qualifier(
            qualifier=AllKeywordsQualifier(keywords=keywords) if require_all_keywords else AnyKeywordsQualifier(keywords=keywords)
        )

        if state != "all":
            search_query.add_qualifier(StateQualifier(state=state))

        gql_search_issue_or_pull_requests_with_details: GqlSearchIssueOrPullRequestsWithDetails = await self._perform_graphql_query(
            query_model=GqlSearchIssueOrPullRequestsWithDetails,
            variables=GqlSearchIssueOrPullRequestsWithDetails.to_graphql_query_variables(
                query=search_query.to_query(),
                limit_issues_or_pull_requests=limit_issues_or_pull_requests,
                limit_comments=limit_comments,
                limit_events=limit_related_items,
            ),
        )

        return IssueOrPullRequestWithDetails.from_gql_search_issue_or_pull_requests_with_details(
            gql_search_issue_or_pull_requests_with_details=gql_search_issue_or_pull_requests_with_details
        )

    async def summarize_issues_or_pull_requests(
        self,
        owner: OWNER,
        repo: REPO,
        issue_or_pr: Literal["issue", "pull_request"],
        keywords: SUMMARY_KEYWORDS,
        summary_focus: SEARCH_SUMMARY_FOCUS,
        require_all_keywords: REQUIRE_ALL_KEYWORDS = False,
        limit_issues_or_pull_requests: LIMIT_ISSUES_OR_PULL_REQUESTS = DEFAULT_ISSUES_OR_PULL_REQUESTS_LIMIT,
        limit_comments: LIMIT_COMMENTS = DEFAULT_COMMENT_LIMIT,
        limit_related_items: LIMIT_RELATED_ITEMS = DEFAULT_RELATED_ITEMS_LIMIT,
    ) -> IssueSearchSummary:
        """First perform a search for issues or pull requests in a repository by keywords. Then, summarize those
        results according to the `summary_focus`.

        For each issue, comments, and related items will also be gathered and included in the response."""

        repository_summary: RepositorySummary = await self.repository_server.summarize(
            owner=owner,
            repo=repo,
        )

        items_with_details: list[IssueOrPullRequestWithDetails] = await self.research_issues_or_pull_requests(
            owner=owner,
            repo=repo,
            issue_or_pr=issue_or_pr,
            keywords=keywords,
            require_all_keywords=require_all_keywords,
            limit_issues_or_pull_requests=limit_issues_or_pull_requests,
            limit_comments=limit_comments,
            limit_related_items=limit_related_items,
        )

        issues_with_title: TitleByIssueOrPullRequestInfo = TitleByIssueOrPullRequestInfo.from_issues_or_pull_requests(
            issues_or_pull_requests=[item.issue_or_pr for item in items_with_details]
        )

        system_prompt = f"""
        {PREAMBLE}

        # Instructions

        You will be given the user's search criteria, the issues which match the search criteria, and some basic info about them.

        The user will also provide a "focus" for the summary, this is the information, problem, etc. the user is hoping to context about
        in the results.
        """

        user_prompt = f"""
        # Repository Background Information
        ```
        {repository_summary.root}
        ```

        # Issue Search Results
        ``````yaml
        {yaml.dump(items_with_details)}
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
            This is your chance to provide the key context the user is looking for. If it's not extremely obvious that it relates to the
            user's focus, you should provide a brief explanation of why you believe it relates to the user's focus.
            **If the issue is highly related to the user's focus, you should provide significantly more information about it and discussion
            around it. Ideally enough information that the user should not have to look at the issue itself.**
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

        summary: str = await self._sample(
            system_prompt=system_prompt,
            messages=user_prompt,
        )

        return IssueSearchSummary(owner=owner, repo=repo, keywords=keywords, summary=summary, items_reviewed=issues_with_title)
