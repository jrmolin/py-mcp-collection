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

SimpleIssueSearchQualifierTypes = (
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

AdvancedIssueSearchQualifierTypes = KeywordQualifier | LabelQualifier


class IssueSearchQuery(BaseQuery[SimpleIssueSearchQualifierTypes, AdvancedIssueSearchQualifierTypes]):
    """The `IssueSearchQuery` operator searches for issues."""

    @override
    def to_query(self) -> str:
        query = super().to_query()
        return f"is:issue {query}"

    @classmethod
    def from_repo_or_owner(cls, owner: str | None = None, repo: str | None = None) -> Self:
        if owner is not None:
            if repo is None:
                return cls(qualifiers=[OwnerQualifier(owner=owner)])

            return cls(qualifiers=[RepoQualifier(owner=owner, repo=repo)])

        return cls()
