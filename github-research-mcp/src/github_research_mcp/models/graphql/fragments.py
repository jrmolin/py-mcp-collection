from datetime import datetime
from textwrap import dedent
from typing import Any, Literal

from pydantic import BaseModel, Field, field_serializer, field_validator
from pydantic.aliases import AliasChoices


def dedent_set(fragments: set[str]) -> set[str]:
    return {dedent(text=fragment) for fragment in fragments}


def extract_nodes(value: Any) -> list[Any] | Any:
    if isinstance(value, dict):
        nodes = value.get("nodes")
        if isinstance(nodes, list):
            return nodes

    return value


MAX_BODY_LENGTH = 2000
MAX_COMMENT_BODY_LENGTH = 1000

TRUNCATION_MARKER = "... [the middle portion has been truncated, retrieve object directly to get the full body]"


def trim_body(body: str, max_length: int = MAX_BODY_LENGTH) -> str:
    """If the body is longer than the max length, we take the first max_length / 2 characters and the last max_length / 2 characters."""

    if len(body) > max_length:
        first_half = body[: max_length // 2]
        middle_truncated_marker = TRUNCATION_MARKER + " ... "
        last_half = body[-max_length // 2 :]
        end_truncated_marker = TRUNCATION_MARKER
        return first_half + "\n\n" + middle_truncated_marker + "\n\n" + last_half + "\n\n" + end_truncated_marker

    return body.strip()


def trim_comment_body(body: str, max_length: int = MAX_COMMENT_BODY_LENGTH) -> str:
    """If the body is longer than the max length, we take the first max_length / 2 characters and the last max_length / 2 characters."""
    return trim_body(body, max_length)


class Nodes[T](BaseModel):
    nodes: list[T]


class Actor(BaseModel):
    """A user, bot, or app on GitHub."""

    user_type: str
    login: str

    @staticmethod
    def graphql_fragments() -> set[str]:
        fragment = """
            fragment gqlActor on Actor {
                __typename
                user_type: __typename
                login
            }
            """
        return {dedent(text=fragment)}


class Comment(BaseModel):
    """A comment on an issue or pull request."""

    body: str
    author: Actor
    author_association: str = Field(validation_alias="authorAssociation")
    created_at: datetime = Field(validation_alias="createdAt")
    updated_at: datetime = Field(validation_alias="updatedAt")

    @field_serializer("created_at", "updated_at")
    def serialize_datetime(self, value: datetime | None) -> str | None:
        if value is None:
            return None
        return value.isoformat()

    @field_serializer("body")
    def serialize_body(self, value: str) -> str:
        return trim_comment_body(value)

    @staticmethod
    def graphql_fragments() -> set[str]:
        fragment = """
            fragment gqlComment on IssueComment {
                body
                author {
                    ...gqlActor
                }
                authorAssociation
                createdAt
                updatedAt
            }
            """
        return {dedent(text=fragment), *Actor.graphql_fragments()}


class Label(BaseModel):
    """A label on an issue or pull request."""

    name: str

    @staticmethod
    def graphql_fragments() -> set[str]:
        fragment = """
            fragment gqlLabelName on Label {
                name
            }
            """
        return {dedent(text=fragment)}


class Issue(BaseModel):
    """An issue on GitHub."""

    number: int
    title: str
    body: str
    state: str
    state_reason: str | None = Field(validation_alias=AliasChoices("stateReason", "state_reason"))
    is_pr: Literal[False] = Field(default=False)

    author: Actor
    author_association: str = Field(validation_alias=AliasChoices("authorAssociation", "author_association"))
    created_at: datetime = Field(validation_alias=AliasChoices("createdAt", "created_at"))
    updated_at: datetime = Field(validation_alias=AliasChoices("updatedAt", "updated_at"))
    closed_at: datetime | None = Field(default=None, validation_alias=AliasChoices("closedAt", "closed_at"))

    labels: list[Label]

    assignees: list[Actor]

    @field_serializer("body")
    def serialize_body(self, value: str) -> str:
        return trim_body(value)

    @field_validator("labels", "assignees", mode="before")
    @classmethod
    def flatten_labels_and_assignees(cls, value: Any) -> Any:
        return extract_nodes(value)

    @field_serializer("created_at", "updated_at", "closed_at")
    def serialize_datetime(self, value: datetime | None) -> str | None:
        if value is None:
            return None
        return value.isoformat()

    @staticmethod
    def graphql_fragments() -> set[str]:
        fragment = """
            fragment gqlIssue on Issue {
                number
                title
                body
                state
                stateReason
                author {
                    ...gqlActor
                }
                authorAssociation
                createdAt
                updatedAt
                labels(first: 10) {
                    nodes {
                        ...gqlLabelName
                    }
                }
                assignees(first: 5) {
                    nodes {
                        ...gqlActor
                    }
                }
            }
            """
        return {dedent(text=fragment), *Actor.graphql_fragments(), *Label.graphql_fragments()}


class MergeCommit(BaseModel):
    oid: str


class PullRequest(BaseModel):
    """A pull request on GitHub."""

    number: int
    title: str
    body: str
    state: str
    is_pr: Literal[True] = Field(default=True)
    merged: bool
    author: Actor
    created_at: datetime = Field(validation_alias=AliasChoices("createdAt", "created_at"))
    updated_at: datetime = Field(validation_alias=AliasChoices("updatedAt", "updated_at"))
    closed_at: datetime | None = Field(default=None, validation_alias=AliasChoices("closedAt", "closed_at"))
    merged_at: datetime | None = Field(default=None, validation_alias=AliasChoices("mergedAt", "merged_at"))
    merge_commit: MergeCommit | None = Field(validation_alias=AliasChoices("mergeCommit", "merge_commit"))

    labels: list[Label]

    assignees: list[Actor]

    @field_serializer("body")
    def serialize_body(self, value: str) -> str:
        return trim_body(value)

    @field_validator("labels", "assignees", mode="before")
    @classmethod
    def flatten_labels_and_assignees(cls, value: Any) -> Any:
        return extract_nodes(value)

    @field_serializer("created_at", "updated_at", "closed_at", "merged_at")
    def serialize_datetime(self, value: datetime | None) -> str | None:
        if value is None:
            return None
        return value.isoformat()

    @staticmethod
    def graphql_fragments() -> set[str]:
        fragment = """
            fragment gqlPullRequest on PullRequest {
                number
                title
                body
                state
                authorAssociation
                author {
                    ...gqlActor
                }
                createdAt
                updatedAt
                merged
                mergedAt
                mergeCommit {
                    oid
                }
                closedAt
                labels(first: 10) {
                    nodes {
                    ...gqlLabelName
                    }
                }
                assignees(first: 5) {
                    nodes {
                    ...gqlActor
                    }
                }
            }
            """
        return {dedent(text=fragment), *Actor.graphql_fragments(), *Label.graphql_fragments()}


class TimelineItem(BaseModel):
    actor: Actor
    created_at: datetime = Field(validation_alias="createdAt")
    source: Issue | PullRequest = Field(validation_alias=AliasChoices("source", "subject"))

    @field_serializer("created_at")
    def serialize_datetime(self, value: datetime | None) -> str | None:
        if value is None:
            return None
        return value.isoformat()

    @staticmethod
    def graphql_fragments() -> set[str]:
        return {*Actor.graphql_fragments(), *Issue.graphql_fragments(), *PullRequest.graphql_fragments()}


class ChangedFile(BaseModel):
    path: str
    additions: int
    deletions: int
    change_type: str = Field(validation_alias="changeType")

    @staticmethod
    def graphql_fragments() -> set[str]:
        return {*Actor.graphql_fragments(), *Issue.graphql_fragments(), *PullRequest.graphql_fragments()}
