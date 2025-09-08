from datetime import datetime
from textwrap import dedent
from typing import Any

from pydantic import BaseModel, Field, field_serializer, field_validator


def dedent_set(fragments: set[str]) -> set[str]:
    return {dedent(text=fragment) for fragment in fragments}


class Nodes[T](BaseModel):
    nodes: list[T]


class Actor(BaseModel):
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
    number: int
    title: str
    body: str
    state: str
    state_reason: str | None = Field(validation_alias="stateReason")

    author: Actor
    author_association: str = Field(validation_alias="authorAssociation")
    created_at: datetime = Field(validation_alias="createdAt")
    updated_at: datetime = Field(validation_alias="updatedAt")
    closed_at: datetime | None = Field(default=None, validation_alias="closedAt")

    labels: list[Label]

    assignees: list[Actor]

    @field_validator("labels", "assignees", mode="before")
    @classmethod
    def flatten_labels_and_assignees(cls, value: Any) -> Any:
        if isinstance(value, dict) and (nodes := value.get("nodes")):
            return nodes

        return value

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
    number: int
    title: str
    body: str
    state: str
    merged: bool
    author: Actor
    created_at: datetime = Field(validation_alias="createdAt")
    updated_at: datetime = Field(validation_alias="updatedAt")
    closed_at: datetime | None = Field(default=None, validation_alias="closedAt")
    merged_at: datetime | None = Field(default=None, validation_alias="mergedAt")
    merge_commit: MergeCommit | None = Field(validation_alias="mergeCommit")

    labels: list[Label]

    assignees: list[Actor]

    @field_validator("labels", "assignees", mode="before")
    @classmethod
    def flatten_labels_and_assignees(cls, value: Any) -> Any:
        if isinstance(value, dict) and (nodes := value.get("nodes")):
            return nodes

        return value

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
    source: Issue | PullRequest

    @field_serializer("created_at")
    def serialize_datetime(self, value: datetime | None) -> str | None:
        if value is None:
            return None
        return value.isoformat()

    @staticmethod
    def graphql_fragments() -> set[str]:
        return {*Actor.graphql_fragments(), *Issue.graphql_fragments(), *PullRequest.graphql_fragments()}
