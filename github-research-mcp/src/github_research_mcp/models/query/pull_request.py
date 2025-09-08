from typing import override

from github_research_mcp.models.query.base import (
    AllKeywordsQualifier,
    AnyKeywordsQualifier,
    AssigneeQualifier,
    AuthorQualifier,
    BaseQuery,
    IssueTypeQualifier,
    KeywordQualifier,
    LabelQualifier,
    OwnerQualifier,
    RepoQualifier,
    StateQualifier,
)

SimplePullRequestSearchQualifierTypes = (
    AssigneeQualifier
    | AuthorQualifier
    | IssueTypeQualifier
    | AllKeywordsQualifier
    | AnyKeywordsQualifier
    | LabelQualifier
    | OwnerQualifier
    | RepoQualifier
    | StateQualifier
)

AdvancedPullRequestSearchQualifierTypes = KeywordQualifier | LabelQualifier


class PullRequestSearchQuery(BaseQuery[SimplePullRequestSearchQualifierTypes, AdvancedPullRequestSearchQualifierTypes]):
    """The `PullRequestSearchQuery` operator searches for pull requests."""

    @override
    def to_query(self) -> str:
        query = super().to_query()
        return f"is:pr {query}"
