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
from github_research_mcp.models.query.base import AllKeywordsQualifier, AnyKeywordsQualifier, StateQualifier
from github_research_mcp.models.query.issue_or_pull_request import IssueOrPullRequestSearchQuery
from github_research_mcp.sampling.prompts import PREAMBLE, PromptBuilder
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

LIMIT_ISSUES_OR_PULL_REQUESTS = Annotated[
    int, Field(description="The maximum number of issues or pull requests to include in the search results.")
]

SEARCH_SUMMARY_FOCUS = Annotated[
    str,
    Field(
        description=(
            "The desired focus of the summary of the search results. The quality of the summary is going to be "
            "highly dependent on what you include in the focus. If you are looking for related/duplicate issues"
        )
    ),
]

RELATED_TO_ISSUE = Annotated["GitHubIssue", Field(description="A specific GitHub issue that the search is related to.")]

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


class IssueSearchSummary(BaseModel):
    owner: str = Field(description="The owner of the repository.")
    repo: str = Field(description="The name of the repository.")
    keywords: set[str] = Field(description="The keywords used to search for the issues.")
    summary: str = Field(description="The summary of the issue search results.")
    items_reviewed: TitleByIssueOrPullRequestInfo = Field(description="The items reviewed.")


class GitHubIssue(BaseModel):
    owner: str = Field(description="The owner of the repository.")
    repo: str = Field(description="The name of the repository.")
    issue_number: int = Field(description="The number of the issue or pull request.")


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
        include_pull_request_diff: bool = True,
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

    async def summarize_issue_or_pull_request(
        self,
        owner: OWNER,
        repo: REPO,
        issue_or_pr_number: ISSUE_OR_PR_NUMBER,
        summary_focus: SUMMARY_FOCUS | None = None,
        limit_comments: LIMIT_COMMENTS = DEFAULT_COMMENT_LIMIT,
        limit_related_items: LIMIT_RELATED_ITEMS = DEFAULT_RELATED_ITEMS_LIMIT,
        include_pull_request_diff: bool = True,
    ) -> IssueOrPullRequestSummary:
        """Produce a "focus"-ed summary of a specific issue incorporating the comments, related items, and the issue itself."""

        issue_details: IssueOrPullRequestWithDetails = await self.research_issue_or_pull_request(
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
        user_prompt = PromptBuilder()

        user_prompt.add_text_section(title="Repository Background Information", text=repository_summary.root)
        user_prompt.add_text_section(title="Focus", text=summary_focus if summary_focus else "No specific focus provided")

        if len(issue_details.comments) >= limit_comments:
            comment_warning = f"There were more than {limit_comments} comments, only the first {limit_comments} are included below:"
            user_prompt.add_text_section(title="Not all comments are included", text=comment_warning)

        if len(issue_details.related) >= limit_related_items:
            related_items_warning = (
                f"There were more than {limit_related_items} related items, only the first {limit_related_items} are included below:"
            )
            user_prompt.add_text_section(title="Not all related items are included", text=related_items_warning)

        user_prompt.add_yaml_section(title="Issue or Pull Request with Context", obj=issue_details)

        summary: str = await self._sample(
            system_prompt=system_prompt,
            messages=user_prompt.render_text(),
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
        include_pull_request_diffs: bool = True,
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

        issues_or_pull_requests_with_details: list[IssueOrPullRequestWithDetails] = (
            IssueOrPullRequestWithDetails.from_gql_search_issue_or_pull_requests_with_details(
                gql_search_issue_or_pull_requests_with_details=gql_search_issue_or_pull_requests_with_details
            )
        )

        if include_pull_request_diffs:
            issues_or_pull_requests_with_details = await self._add_pull_request_diffs(
                owner=owner,
                repo=repo,
                issues_or_pull_requests_with_details=issues_or_pull_requests_with_details,
            )

        return issues_or_pull_requests_with_details

    async def summarize_issues_or_pull_requests(
        self,
        owner: OWNER,
        repo: REPO,
        issue_or_pr: Literal["issue", "pull_request"],
        keywords: SUMMARY_KEYWORDS,
        summary_focus: SEARCH_SUMMARY_FOCUS,
        related_to_issue: RELATED_TO_ISSUE | None = None,
        require_all_keywords: REQUIRE_ALL_KEYWORDS = False,
        limit_issues_or_pull_requests: LIMIT_ISSUES_OR_PULL_REQUESTS = DEFAULT_ISSUES_OR_PULL_REQUESTS_LIMIT,
        limit_comments: LIMIT_COMMENTS = DEFAULT_COMMENT_LIMIT,
        limit_related_items: LIMIT_RELATED_ITEMS = DEFAULT_RELATED_ITEMS_LIMIT,
        include_pull_request_diffs: bool = True,
    ) -> IssueSearchSummary:
        """First perform a search for issues or pull requests in a repository by keywords. Then, summarize those
        results according to the `summary_focus`. If your search is related to a specific issue, you should include
        `related_to_issue` which will gather the information from that issue and inform the summary provided.

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
            include_pull_request_diffs=include_pull_request_diffs,
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

        user_prompt: PromptBuilder = PromptBuilder()

        user_prompt.add_text_section(title="Repository Background Information", text=repository_summary.root)
        user_prompt.add_yaml_section(title="Issue Search Results", obj=items_with_details)

        focus_text = [
            "The user has asked that you specifically focus your review of the issue search results on the following aspects:",
            summary_focus,
        ]
        user_prompt.add_text_section(title="Focus", text=focus_text)

        if related_to_issue:
            related_issue_details: IssueOrPullRequestWithDetails = await self.research_issue_or_pull_request(
                owner=related_to_issue.owner,
                repo=related_to_issue.repo,
                issue_or_pr_number=related_to_issue.issue_number,
            )
            user_prompt.add_yaml_section(
                title="Related to Issue",
                obj=[
                    "The user has indicated that the search they are performing is related to the following issue or pull request: ",
                    related_issue_details,
                    "As a result, you can skip this issue if you find it in the search results",
                ],
            )

        user_prompt.add_text_section(
            title="Summary Instructions",
            text="""
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
        """,
        )

        summary: str = await self._sample(
            system_prompt=system_prompt,
            messages=user_prompt.render_text(),
        )

        return IssueSearchSummary(owner=owner, repo=repo, keywords=keywords, summary=summary, items_reviewed=issues_with_title)

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
