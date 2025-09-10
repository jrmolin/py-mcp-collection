from typing import Self, override

from github_research_mcp.models.query.base import (
    AllKeywordsQualifier,
    AllSymbolsQualifier,
    AnyKeywordsQualifier,
    AnySymbolsQualifier,
    AssigneeQualifier,
    AuthorQualifier,
    BaseQuery,
    IssueTypeQualifier,
    KeywordQualifier,
    LabelQualifier,
    LanguageQualifier,
    OwnerQualifier,
    PathQualifier,
    RepoQualifier,
    StateQualifier,
)

SimpleCodeSearchQualifierTypes = (
    AssigneeQualifier
    | AuthorQualifier
    | IssueTypeQualifier
    | AllKeywordsQualifier
    | AnyKeywordsQualifier
    | AnySymbolsQualifier
    | AllSymbolsQualifier
    | LabelQualifier
    | PathQualifier
    | LanguageQualifier
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
        return f"{query}"

    @classmethod
    def from_repo_or_owner(cls, owner: str | None = None, repo: str | None = None) -> Self:
        qualifiers: list[SimpleCodeSearchQualifierTypes] = []

        if owner is not None:
            if repo is None:
                qualifiers.append(OwnerQualifier(owner=owner))
            else:
                qualifiers.append(RepoQualifier(owner=owner, repo=repo))

        return cls(qualifiers=qualifiers)
