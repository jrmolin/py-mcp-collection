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

SimpleCodeSearchQualifierTypes = (
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

AdvancedCodeSearchQualifierTypes = KeywordQualifier | LabelQualifier


class CodeSearchQuery(BaseQuery[SimpleCodeSearchQualifierTypes, AdvancedCodeSearchQualifierTypes]):
    """The `CodeSearchQuery` operator searches for code."""

    @override
    def to_query(self) -> str:
        query = super().to_query()
        return f"is:code {query}"
