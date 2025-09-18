from typing import TYPE_CHECKING, Annotated, Any, Literal, Self

from fastmcp.utilities.logging import get_logger
from githubkit.github import GitHub
from githubkit.versions.v2022_11_28.models.group_0238 import DiffEntry
from pydantic import BaseModel, Field
from pydantic.root_model import RootModel

from github_research_mcp.models import Comment, Issue, PullRequest
from github_research_mcp.models.graphql.queries import (
    GqlGetIssueOrPullRequestsWithDetails,
    GqlIssueWithDetails,
    GqlSearchIssueOrPullRequestsWithDetails,
)
from github_research_mcp.models.query.base import AllKeywordsQualifier, AnyKeywordsQualifier
from github_research_mcp.models.query.issue_or_pull_request import IssueOrPullRequestSearchQuery
from github_research_mcp.sampling.extract import object_in_text_instructions
from github_research_mcp.sampling.prompts import SystemPromptBuilder, UserPromptBuilder
from github_research_mcp.servers.base import BaseResponseModel, BaseServer
from github_research_mcp.servers.repository import RepositoryServer, RepositorySummary
from github_research_mcp.servers.shared.annotations import (
    LIMIT_COMMENTS,
    LIMIT_RELATED_ITEMS,
    OWNER,
    REPO,
    SUMMARY_FOCUS,
)
from github_research_mcp.servers.shared.utility import extract_response

if TYPE_CHECKING:
    from githubkit.response import Response
    from githubkit.versions.v2022_11_28.types.group_0238 import DiffEntryType

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

ISSUE_OR_PULL_REQUEST = Annotated[Literal["issue", "pull_request"], "The type of issue or pull request to search for."]

LIMIT_ISSUES_OR_PULL_REQUESTS = Annotated[
    int, Field(description="The maximum number of issues or pull requests to include in the search results.")
]

INCLUDE_PULL_REQUEST_DIFF = Annotated[bool, "Whether to include the diff of the pull request in the search results."]

SEARCH_SUMMARY_FOCUS = Annotated[
    str,
    Field(
        description=(
            "The desired focus of the summary of the search results. The quality of the summary is going to be "
            "highly dependent on what you include in the focus. If you are looking for related/duplicate issues"
        )
    ),
]

DEFAULT_COMMENT_LIMIT = 10
DEFAULT_RELATED_ITEMS_LIMIT = 5
DEFAULT_ISSUES_OR_PULL_REQUESTS_LIMIT = 50

DEFAULT_SEARCH_STATE = "all"


class PullRequestFileDiff(BaseModel):
    path: str = Field(description="The path of the file.")
    status: Literal["added", "removed", "modified", "renamed", "copied", "changed", "unchanged"] = Field(
        description="The status of the file."
    )
    patch: str | None = Field(default=None, description="The patch of the file.")
    previous_filename: str | None = Field(default=None, description="The previous filename of the file.")
    truncated: bool = Field(default=False, description="Whether the patch has been truncated to reduce response size.")

    @classmethod
    def from_diff_entry(cls, diff_entry: DiffEntry, truncate: int = 100) -> Self:
        pr_file_diff: Self = cls(
            path=diff_entry.filename,
            status=diff_entry.status,
            patch=diff_entry.patch if diff_entry.patch else None,
            previous_filename=diff_entry.previous_filename if diff_entry.previous_filename else None,
        )

        return pr_file_diff.truncate(truncate=truncate)

    @classmethod
    def from_diff_entries(cls, diff_entries: list[DiffEntry], truncate: int = 100) -> list[Self]:
        return [cls.from_diff_entry(diff_entry=diff_entry, truncate=truncate) for diff_entry in diff_entries]

    @property
    def lines(self) -> list[str]:
        return self.patch.split("\n") if self.patch else []

    def truncate(self, truncate: int) -> Self:
        lines: list[str] = self.lines

        if len(lines) > truncate:
            lines = lines[:truncate]
            return self.model_copy(update={"patch": "\n".join(lines), "truncated": True})

        return self


class IssueOrPullRequestWithDetails(BaseResponseModel):
    issue_or_pr: Issue | PullRequest = Field(description="The issue or pull request.")
    diff: list[PullRequestFileDiff] | None = Field(default=None, description="The diff, if it's a pull request.")
    comments: list[Comment] = Field(description="The comments on the issue or pull request.")
    related: list[Issue | PullRequest] = Field(description="The related issues or pull requests.")

    @classmethod
    def from_gql_get_issue_or_pull_requests_with_details(
        cls,
        gql_get_issue_or_pull_requests_with_details: GqlGetIssueOrPullRequestsWithDetails,
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
    def from_issues_or_pull_requests_with_details(cls, issues_or_pull_requests_with_details: list[IssueOrPullRequestWithDetails]) -> Self:
        # sort by issue or pull request number
        issues_or_pull_requests_with_details.sort(key=lambda x: x.issue_or_pr.number)

        return cls.from_issues_or_pull_requests(
            issues_or_pull_requests=[issue_or_pull_request.issue_or_pr for issue_or_pull_request in issues_or_pull_requests_with_details]
        )

    @classmethod
    def from_issues_or_pull_requests(cls, issues_or_pull_requests: list[Issue | PullRequest]) -> Self:
        issues_or_pull_requests_by_info = {}

        for issue_or_pull_request in issues_or_pull_requests:
            key = "issue" if isinstance(issue_or_pull_request, Issue) else "pull_request"
            key: str = f"{key}:{issue_or_pull_request.number}"

            issues_or_pull_requests_by_info[key] = issue_or_pull_request.title

        return cls(root=issues_or_pull_requests_by_info)


class IssueOrPullRequestSummary(BaseModel):
    owner: str = Field(description="The owner of the repository.")
    repo: str = Field(description="The name of the repository.")
    issue_or_pr_number: int = Field(description="The number of the issue or pull request.")
    summary: str = Field(description="The summary of the issue or pull request.")


class IssueOrPullRequestResearchSummary(BaseModel):
    owner: str = Field(description="The owner of the repository.")
    repo: str = Field(description="The name of the repository.")
    issue_or_pr_number: int = Field(description="The number of the issue or pull request.")
    findings: str = Field(description="The research findings.")
    items_reviewed: TitleByIssueOrPullRequestInfo = Field(description="The items reviewed while researching the issue.")


class RequestKeywords(BaseModel):
    keywords: list[str] = Field(description="The keywords to use to search for related issues or pull requests.")


class IssuesOrPullRequestsServer(BaseServer):
    repository_server: RepositoryServer

    def __init__(self, github_client: GitHub[Any], repository_server: RepositoryServer):
        self.github_client = github_client
        self.repository_server = repository_server

    async def get_issue_or_pull_request(
        self,
        owner: OWNER,
        repo: REPO,
        issue_or_pr_number: ISSUE_OR_PR_NUMBER,
        limit_comments: LIMIT_COMMENTS = DEFAULT_COMMENT_LIMIT,
        limit_related_items: LIMIT_RELATED_ITEMS = DEFAULT_RELATED_ITEMS_LIMIT,
        include_pull_request_diff: INCLUDE_PULL_REQUEST_DIFF = True,
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

        issue_or_pull_request_with_details: IssueOrPullRequestWithDetails = (
            IssueOrPullRequestWithDetails.from_gql_get_issue_or_pull_requests_with_details(
                gql_get_issue_or_pull_requests_with_details=gql_get_issue_or_pull_requests_with_details,
            )
        )

        if isinstance(issue_or_pull_request_with_details.issue_or_pr, PullRequest) and include_pull_request_diff:
            await self._add_pull_request_diff(
                owner=owner,
                repo=repo,
                issue_or_pull_request_with_details=issue_or_pull_request_with_details,
            )

        return issue_or_pull_request_with_details

    async def search_issues_or_pull_requests(
        self,
        owner: OWNER,
        repo: REPO,
        keywords: SEARCH_KEYWORDS,
        issue_or_pull_request: ISSUE_OR_PULL_REQUEST = "issue",
        require_all_keywords: REQUIRE_ALL_KEYWORDS = False,
        limit_issues_or_pull_requests: LIMIT_ISSUES_OR_PULL_REQUESTS = DEFAULT_ISSUES_OR_PULL_REQUESTS_LIMIT,
        limit_comments: LIMIT_COMMENTS = DEFAULT_COMMENT_LIMIT,
        limit_related_items: LIMIT_RELATED_ITEMS = DEFAULT_RELATED_ITEMS_LIMIT,
        include_pull_request_diff: INCLUDE_PULL_REQUEST_DIFF = True,
    ) -> list[IssueOrPullRequestWithDetails]:
        """Search for issues or pull requests (determined by the `issue_or_pull_request` parameter) in a repository by the
        keywords provided.

        Only issues or pull requests containing the keywords will be included in the search results."""

        search_query: IssueOrPullRequestSearchQuery = IssueOrPullRequestSearchQuery.from_repo_or_owner(
            owner=owner, repo=repo, issue_or_pull_request=issue_or_pull_request
        )

        search_query.add_qualifier(qualifier=AnyKeywordsQualifier(keywords=set(keywords)))

        if require_all_keywords:
            search_query.add_qualifier(qualifier=AllKeywordsQualifier(keywords=set(keywords)))

        gql_search_issue_or_pull_requests_with_details: GqlSearchIssueOrPullRequestsWithDetails = await self._perform_graphql_query(
            query_model=GqlSearchIssueOrPullRequestsWithDetails,
            variables=GqlSearchIssueOrPullRequestsWithDetails.to_graphql_query_variables(
                query=search_query.to_query(),
                limit_issues_or_pull_requests=limit_issues_or_pull_requests,
                limit_comments=limit_comments,
                limit_events=limit_related_items,
            ),
        )

        issues_or_pull_requests_with_details: list[IssueOrPullRequestWithDetails] = (
            IssueOrPullRequestWithDetails.from_gql_search_issue_or_pull_requests_with_details(
                gql_search_issue_or_pull_requests_with_details=gql_search_issue_or_pull_requests_with_details
            )
        )

        if include_pull_request_diff:
            issues_or_pull_requests_with_details = await self._add_pull_request_diffs(
                owner=owner,
                repo=repo,
                issues_or_pull_requests_with_details=issues_or_pull_requests_with_details,
            )

        return issues_or_pull_requests_with_details

    async def research_issue_or_pull_request(
        self,
        owner: OWNER,
        repo: REPO,
        issue_or_pr_number: ISSUE_OR_PR_NUMBER,
        summary_focus: SUMMARY_FOCUS | None = None,
        limit_comments: LIMIT_COMMENTS = DEFAULT_COMMENT_LIMIT,
        limit_related_items: LIMIT_RELATED_ITEMS = DEFAULT_RELATED_ITEMS_LIMIT,
        include_pull_request_diff: bool = True,
    ) -> IssueOrPullRequestResearchSummary:
        """Produce a "focus"-ed summary of a specific issue incorporating the comments, related items, and the issue itself."""

        issue_details: IssueOrPullRequestWithDetails = await self.get_issue_or_pull_request(
            owner=owner,
            repo=repo,
            issue_or_pr_number=issue_or_pr_number,
            limit_comments=limit_comments,
            limit_related_items=limit_related_items,
            include_pull_request_diff=include_pull_request_diff,
        )

        repository_summary: RepositorySummary = await self.repository_server.summarize(
            owner=owner,
            repo=repo,
        )

        system_prompt_builder = SystemPromptBuilder()

        user_prompt_builder = UserPromptBuilder()

        user_prompt_builder.add_text_section(title="Repository Background Information", text=repository_summary.root)
        user_prompt_builder.add_text_section(title="Focus", text=summary_focus if summary_focus else "No specific focus provided")
        user_prompt_builder.add_yaml_section(
            title="Issue or Pull Request with Context",
            preamble="We are being asked to research the following issue or pull request:",
            obj=issue_details,
        )

        user_prompt_builder.add_text_section(
            title="Keywords",
            text=f"""
Based on the issue outlined in the `Issue or Pull Request with Context` above ({issue_details.issue_or_pr.number} in {owner}/{repo}
we will first search the GitHub repository issues and pull requests that are related to the issue.

We first need to identify a list of 6 keywords to use to search for related issues and pull requests. Only issues and pull
requests containing at least one of these keywords will be included in the search results so it's important to pick
the right keywords.

The best keywords will be reflective of the content of the issue/pull request and capture alternative ways of representing
the issue/pull request that are likely to be present in other issues and pull requests that cover related topics. Each keyword
you pick should be deeply rooted in some part of the issue/pull request.

You should not search for keywords like `issue`, `pull request`, `comment`, `event`, `bug`, `feature`,
but should search for words that are likely to be present in other issues and pull requests that cover
related topics. For example, if the bug is about a deadlock, you could search for keywords like `deadlock`,
`thread`, `synchronization`, `mutex`, `lock`, `race condition`, etc.

{object_in_text_instructions(object_type=RequestKeywords, require=True)}
""",
        )

        request_keywords: RequestKeywords = await self._structured_sample(
            system_prompt=system_prompt_builder.render_text(),
            messages=user_prompt_builder.to_sampling_messages(),
            object_type=RequestKeywords,
            max_tokens=5000,
        )

        logger.info(
            msg=(
                f"For {issue_details.issue_or_pr.number}, searching for related issues and "
                f"pull requests with keywords: {request_keywords.keywords}"
            )
        )

        search_query: IssueOrPullRequestSearchQuery = IssueOrPullRequestSearchQuery.from_repo_or_owner(
            owner=owner, repo=repo, issue_or_pull_request="issue"
        )

        search_query.add_qualifier(qualifier=AnyKeywordsQualifier(keywords=set(request_keywords.keywords)))

        gql_search_issue_or_pull_requests_with_details: GqlSearchIssueOrPullRequestsWithDetails = await self._perform_graphql_query(
            query_model=GqlSearchIssueOrPullRequestsWithDetails,
            variables=GqlSearchIssueOrPullRequestsWithDetails.to_graphql_query_variables(
                query=search_query.to_query(),
                limit_issues_or_pull_requests=DEFAULT_ISSUES_OR_PULL_REQUESTS_LIMIT,
                limit_comments=DEFAULT_COMMENT_LIMIT,
                limit_events=DEFAULT_RELATED_ITEMS_LIMIT,
            ),
        )

        issues_or_pull_requests_with_details: list[IssueOrPullRequestWithDetails] = (
            IssueOrPullRequestWithDetails.from_gql_search_issue_or_pull_requests_with_details(
                gql_search_issue_or_pull_requests_with_details=gql_search_issue_or_pull_requests_with_details
            )
        )

        user_prompt_builder.pop()

        user_prompt_builder.add_yaml_section(
            title="Search Results",
            preamble="""We have identified a list of keywords: {request_keywords.keywords} and have performed a search
            which returned the following results that, if you feel are related to the issue, you should reference in your research.""",
            obj=issues_or_pull_requests_with_details,
        )

        user_prompt_builder.add_text_section(
            title="Instructions",
            text=f"""
        Please provide your understanding of issue {issue_details.issue_or_pr.number} in the repository {owner}/{repo} paying special
        attention to how it might relate to to previous issues and pull requests in the repository (is it a duplicate, is it a similar
        problem, is it likely solved in a similar way, etc.).

        It is not necessary to reference issues or pull requests that are not related to the issue or pull request being researched.

        By default, your research should cover:
        1. Information about the issue or pull request, its state, age, etc.
        2. A description of the reported issue or pull request in the context of the repository and codebase
        3. Additional information/corrections/findings related to the reported issue that occurred in the comments and/or the search
            results.
        4. The resolution (or lack thereof) of the reported issue whether it was solved with a code change, documentation,
            closed as won't fix, closed as a duplicate, closed as a false positive, or closed as a false negative, etc. Pay
            careful attention to the state of any related items before making any conclusions.

        That being said, what the user asks for in the `focus` should be prioritized over the default summary.
        """,
        )

        research_findings: str = await self._sample(
            system_prompt=system_prompt_builder.render_text(),
            messages=user_prompt_builder.to_sampling_messages(),
            max_tokens=10000,
        )

        return IssueOrPullRequestResearchSummary(
            owner=owner,
            repo=repo,
            issue_or_pr_number=issue_or_pr_number,
            findings=research_findings,
            items_reviewed=TitleByIssueOrPullRequestInfo.from_issues_or_pull_requests_with_details(
                issues_or_pull_requests_with_details=issues_or_pull_requests_with_details
            ),
        )

    async def _get_pull_request_diff(
        self, owner: OWNER, repo: REPO, pull_request_number: int, truncate: int = 100
    ) -> list[PullRequestFileDiff]:
        """Get the diff of a pull request."""

        response: Response[list[DiffEntry], list[DiffEntryType]] = await self.github_client.rest.pulls.async_list_files(
            owner=owner, repo=repo, pull_number=pull_request_number
        )

        return PullRequestFileDiff.from_diff_entries(diff_entries=extract_response(response), truncate=truncate)

    async def _add_pull_request_diff(
        self, owner: OWNER, repo: REPO, issue_or_pull_request_with_details: IssueOrPullRequestWithDetails, truncate: int = 100
    ) -> IssueOrPullRequestWithDetails:
        """Add the diff to the issue or pull request."""

        diff = await self._get_pull_request_diff(
            owner=owner,
            repo=repo,
            pull_request_number=issue_or_pull_request_with_details.issue_or_pr.number,
            truncate=truncate,
        )

        issue_or_pull_request_with_details.diff = diff

        return issue_or_pull_request_with_details

    async def _add_pull_request_diffs(
        self, owner: OWNER, repo: REPO, issues_or_pull_requests_with_details: list[IssueOrPullRequestWithDetails], truncate: int = 100
    ) -> list[IssueOrPullRequestWithDetails]:
        """Add the diffs to the issues or pull requests."""

        for issue_or_pull_request_with_details in issues_or_pull_requests_with_details:
            if isinstance(issue_or_pull_request_with_details.issue_or_pr, PullRequest):
                await self._add_pull_request_diff(
                    owner=owner,
                    repo=repo,
                    issue_or_pull_request_with_details=issue_or_pull_request_with_details,
                    truncate=truncate,
                )

        return issues_or_pull_requests_with_details
