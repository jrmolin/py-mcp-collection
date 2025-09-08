from textwrap import dedent
from typing import Any

from pydantic import BaseModel, Field

from github_research_mcp.models.graphql.fragments import Comment, Issue, Nodes, TimelineItem


class GqlIssueWithDetails(Issue):
    comments: Nodes[Comment]
    timeline_items: Nodes[TimelineItem] = Field(alias="timelineItems")

    @staticmethod
    def graphql_fragments() -> set[str]:
        base_fragments: set[str] = Issue.graphql_fragments()

        return {*base_fragments, *Comment.graphql_fragments(), *TimelineItem.graphql_fragments()}


class GqlGetIssuesWithDetailsRepository(BaseModel):
    issue: GqlIssueWithDetails

    @staticmethod
    def graphql_fragments() -> set[str]:
        return {*GqlIssueWithDetails.graphql_fragments()}


class GqlGetIssuesWithDetails(BaseModel):
    repository: GqlGetIssuesWithDetailsRepository

    @staticmethod
    def graphql_fragments() -> set[str]:
        return {*Issue.graphql_fragments(), *Comment.graphql_fragments(), *TimelineItem.graphql_fragments()}

    @staticmethod
    def graphql_query() -> str:
        fragments = "\n".join(GqlGetIssuesWithDetails.graphql_fragments())
        query = """
            query GqlGqlGetIssuesWithDetails(
                $owner: String!
                $repo: String!
                $issue_number: Int!
                $limit_comments: Int!
                $limit_events: Int!
            ) {
                repository(owner: $owner, name: $repo) {
                    issue(number: $issue_number) {
                        ...gqlIssue
                        comments(first: $limit_comments) {
                            nodes {
                                ...gqlComment
                            }
                        }
                        timelineItems(itemTypes: [CROSS_REFERENCED_EVENT], first: $limit_events) {
                            nodes {
                                ... on CrossReferencedEvent {
                                    actor {
                                    ...gqlActor
                                    }
                                    createdAt
                                    source {
                                    ... on Issue {
                                        ...gqlIssue
                                    }
                                    ... on PullRequest {
                                        ...gqlPullRequest
                                    }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        """
        query = dedent(text=query)

        return fragments + "\n" + query


class GqlSearchIssuesWithDetails(BaseModel):
    search: Nodes[GqlIssueWithDetails]

    @staticmethod
    def graphql_fragments() -> set[str]:
        return {*GqlIssueWithDetails.graphql_fragments()}

    @staticmethod
    def graphql_query() -> str:
        fragments = "\n".join(GqlSearchIssuesWithDetails.graphql_fragments())
        query = """
            query GqlSearchIssuesWithDetails(
                $search_query: String!
                $limit_issues: Int!
                $limit_comments: Int!
                $limit_events: Int!
            ) {
                search(query: $search_query, type: ISSUE, first: $limit_issues) {
                    issueCount
                    nodes {
                        ... on Issue {
                            ...gqlIssue
                            comments(first: $limit_comments) {
                                nodes {
                                    ...gqlComment
                                }
                            }
                            timelineItems(itemTypes: [CROSS_REFERENCED_EVENT], first: $limit_events) {
                                nodes {
                                    ... on CrossReferencedEvent {
                                        actor {
                                            ...gqlActor
                                        }
                                        createdAt
                                        source {
                                            ... on Issue {
                                                ...gqlIssue
                                            }
                                            ... on PullRequest {
                                                ...gqlPullRequest
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        """
        query = dedent(text=query)

        return fragments + "\n" + query

    @staticmethod
    def to_graphql_query_variables(query: str, limit_issues: int, limit_comments: int, limit_events: int) -> dict[str, Any]:
        return {
            "search_query": query,
            "limit_issues": limit_issues,
            "limit_comments": limit_comments,
            "limit_events": limit_events,
        }
