from typing import Self

import pytest
from pydantic import BaseModel

from github_research_mcp.models.query.base import (
    AllKeywordsQualifier,
    AllSymbolsQualifier,
    AndOperator,
    AnyKeywordsQualifier,
    AnySymbolsQualifier,
    AssigneeQualifier,
    AuthorQualifier,
    BaseOperator,
    BaseQualifier,
    BaseQuery,
    IssueOrPullRequestQualifier,
    IssueTypeQualifier,
    KeywordInQualifier,
    KeywordQualifier,
    LabelQualifier,
    OrOperator,
    OwnerQualifier,
    RepoQualifier,
    StateQualifier,
)


@pytest.mark.parametrize(
    ("qualifier", "query"),
    [
        (AssigneeQualifier(assignee="test"), 'assignee:"test"'),
        (AuthorQualifier(author="test"), 'author:"test"'),
        (IssueOrPullRequestQualifier(issue_or_pull_request="issue"), "is:issue"),
        (IssueOrPullRequestQualifier(issue_or_pull_request="pull_request"), "is:pr"),
        (LabelQualifier(label="test"), 'label:"test"'),
        (OwnerQualifier(owner="test"), 'owner:"test"'),
        (RepoQualifier(owner="owner", repo="repo"), 'repo:"owner/repo"'),
        (StateQualifier(state="open"), "state:open"),
        (StateQualifier(state="closed"), "state:closed"),
        (KeywordQualifier(keyword="test"), '"test"'),
        (AnyKeywordsQualifier(keywords={"test", "test2"}), '"test" OR "test2"'),
        (AllKeywordsQualifier(keywords={"test", "test2"}), '"test" AND "test2"'),
        (AnySymbolsQualifier(symbols={"test", "test2"}), 'symbol:"test" OR symbol:"test2"'),
        (AllSymbolsQualifier(symbols={"test", "test2"}), 'symbol:"test" AND symbol:"test2"'),
        (KeywordInQualifier(location="title"), "in:title"),
        (KeywordInQualifier(location="body"), "in:body"),
        (KeywordInQualifier(location="comments"), "in:comments"),
        (IssueTypeQualifier(type="bug"), 'type:"bug"'),
        (IssueTypeQualifier(type="feature"), 'type:"feature"'),
    ],
)
def test_qualifiers(qualifier: BaseQualifier, query: str):
    assert qualifier.to_query() == query


@pytest.mark.parametrize(
    ("operator", "query"),
    [
        (AndOperator(clauses=[]), ""),
        (AndOperator(clauses=[KeywordQualifier(keyword="test")]), '"test"'),
        (AndOperator(clauses=[KeywordQualifier(keyword="test"), KeywordQualifier(keyword="test2")]), '"test" AND "test2"'),
        (OrOperator(clauses=[]), ""),
        (OrOperator(clauses=[KeywordQualifier(keyword="test")]), '"test"'),
        (OrOperator(clauses=[KeywordQualifier(keyword="test"), KeywordQualifier(keyword="test2")]), '"test" OR "test2"'),
        (
            AndOperator(
                clauses=[
                    OrOperator(clauses=[KeywordQualifier(keyword="test"), KeywordQualifier(keyword="test2")]),
                    KeywordQualifier(keyword="test3"),
                ]
            ),
            '("test" OR "test2") AND "test3"',
        ),
    ],
)
def test_operators(operator: BaseOperator, query: str):
    assert operator.to_query() == query


class Case(BaseModel):
    name: str
    query: BaseQuery
    expected: str


class Cases(BaseModel):
    cases: list[Case]

    def add_case(self, name: str, query: BaseQuery, expected: str) -> Self:
        self.cases.append(Case(name=name, query=query, expected=expected))
        return self

    def get_names(self) -> list[str]:
        return [case.name for case in self.cases]

    def get_parameterization(self) -> list[tuple[BaseQuery, str]]:
        return [(case.query, case.expected) for case in self.cases]


cases: Cases = Cases(cases=[])

cases.add_case(
    name="Single Keyword",
    query=BaseQuery(qualifiers=[AnyKeywordsQualifier(keywords={"test"})]),
    expected='"test"',
)


cases.add_case(
    name="Multiple Any Keywords",
    query=BaseQuery(
        qualifiers=[AnyKeywordsQualifier(keywords={"test", "test2", "test3"})],
    ),
    expected='"test" OR "test2" OR "test3"',
)

cases.add_case(
    name="Multiple All Keywords",
    query=BaseQuery(
        qualifiers=[AllKeywordsQualifier(keywords={"test", "test2", "test3"})],
    ),
    expected='"test" AND "test2" AND "test3"',
)

cases.add_case(
    name="Multiple Any Keywords with Label and Assignee",
    query=BaseQuery(
        qualifiers=[
            AnyKeywordsQualifier(keywords={"testOne", "testTwo", "testThree"}),
            LabelQualifier(label="labelOne"),
            AssigneeQualifier(assignee="assigneeOne"),
        ],
    ),
    expected='"testOne" OR "testThree" OR "testTwo" label:"labelOne" assignee:"assigneeOne"',
)

cases.add_case(
    name="Specific Repository Any Keyword Search",
    query=BaseQuery(
        qualifiers=[
            RepoQualifier(owner="ownerOne", repo="repoOne"),
            AnyKeywordsQualifier(keywords={"testOne", "testTwo", "testThree"}),
        ],
    ),
    expected='repo:"ownerOne/repoOne" "testOne" OR "testThree" OR "testTwo"',
)


@pytest.mark.parametrize(("query", "expected"), cases.get_parameterization(), ids=cases.get_names())
def test_base_query(query: BaseQuery, expected: str):
    assert query.to_query() == expected
