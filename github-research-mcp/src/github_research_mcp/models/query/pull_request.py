from typing import Self, override

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

    @classmethod
    def from_repo_or_owner(cls, owner: str | None = None, repo: str | None = None) -> Self:
        if owner is not None:
            if repo is None:
                return cls(qualifiers=[OwnerQualifier(owner=owner)])

            return cls(qualifiers=[RepoQualifier(owner=owner, repo=repo)])

        return cls()
