from typing import Literal, Self

from github_research_mcp.models.query.base import (
    AllKeywordsQualifier,
    AnyKeywordsQualifier,
    AssigneeQualifier,
    AuthorQualifier,
    BaseQuery,
    IssueOrPullRequestQualifier,
    IssueTypeQualifier,
    KeywordQualifier,
    LabelQualifier,
    OwnerQualifier,
    RepoQualifier,
    StateQualifier,
)

SimpleIssueOrPullRequestSearchQualifierTypes = (
    AssigneeQualifier
    | AuthorQualifier
    | IssueTypeQualifier
    | IssueOrPullRequestQualifier
    | AllKeywordsQualifier
    | AnyKeywordsQualifier
    | LabelQualifier
    | OwnerQualifier
    | RepoQualifier
    | StateQualifier
)

AdvancedIssueOrPullRequestSearchQualifierTypes = KeywordQualifier | LabelQualifier


class IssueOrPullRequestSearchQuery(
    BaseQuery[SimpleIssueOrPullRequestSearchQualifierTypes, AdvancedIssueOrPullRequestSearchQualifierTypes]
):
    """The `IssueOrPullRequestSearchQuery` operator searches for issues or pull requests."""

    @classmethod
    def from_repo_or_owner(
        cls, owner: str | None = None, repo: str | None = None, issue_or_pull_request: Literal["issue", "pull_request"] = "issue"
    ) -> Self:
        qualifiers: list[SimpleIssueOrPullRequestSearchQualifierTypes] = [
            IssueOrPullRequestQualifier(issue_or_pull_request=issue_or_pull_request)
        ]

        if owner is not None:
            if repo is None:
                qualifiers.append(OwnerQualifier(owner=owner))
            else:
                qualifiers.append(RepoQualifier(owner=owner, repo=repo))

        return cls(qualifiers=qualifiers)
