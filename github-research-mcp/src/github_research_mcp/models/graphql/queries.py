from abc import ABC, abstractmethod
from textwrap import dedent
from typing import Any

from pydantic import BaseModel, Field
from pydantic.aliases import AliasChoices

from github_research_mcp.models.graphql.fragments import Comment, Issue, Nodes, PullRequest, TimelineItem


class GqlIssueWithDetails(Issue):
    comments: Nodes[Comment]
    timeline_items: Nodes[TimelineItem] = Field(validation_alias=AliasChoices("timelineItems", "timeline_items"))

    @staticmethod
    def graphql_fragments() -> set[str]:
        base_fragments: set[str] = Issue.graphql_fragments()

        return {*base_fragments, *Comment.graphql_fragments(), *TimelineItem.graphql_fragments()}

    def to_issue(self) -> Issue:
        return Issue(**self.model_dump())


class GqlPullRequestWithDetails(PullRequest):
    comments: Nodes[Comment]
    timeline_items: Nodes[TimelineItem] = Field(validation_alias=AliasChoices("timelineItems", "timeline_items"))

    @staticmethod
    def graphql_fragments() -> set[str]:
        return {*PullRequest.graphql_fragments(), *Comment.graphql_fragments(), *TimelineItem.graphql_fragments()}

    def to_pull_request(self) -> PullRequest:
        return PullRequest(**self.model_dump())


class GqlGetIssuesWithDetailsRepository(BaseModel):
    issue: GqlIssueWithDetails

    @staticmethod
    def graphql_fragments() -> set[str]:
        return {*GqlIssueWithDetails.graphql_fragments()}


class BaseGqlQuery(BaseModel, ABC):
    @staticmethod
    @abstractmethod
    def graphql_fragments() -> set[str]: ...

    @staticmethod
    @abstractmethod
    def graphql_query() -> str: ...


class GqlGetIssueOrPullRequestsWithDetailsRepository(BaseModel):
    issue_or_pull_request: GqlIssueWithDetails | GqlPullRequestWithDetails = Field(validation_alias="issueOrPullRequest")

    @staticmethod
    def graphql_fragments() -> set[str]:
        return {*GqlIssueWithDetails.graphql_fragments(), *GqlPullRequestWithDetails.graphql_fragments()}


class GqlGetIssueOrPullRequestsWithDetails(BaseGqlQuery, BaseModel):
    repository: GqlGetIssueOrPullRequestsWithDetailsRepository

    @staticmethod
    def graphql_fragments() -> set[str]:
        return {
            *Issue.graphql_fragments(),
            *PullRequest.graphql_fragments(),
            *Comment.graphql_fragments(),
            *TimelineItem.graphql_fragments(),
        }

    @staticmethod
    def graphql_query() -> str:
        fragments = "\n".join(GqlGetIssueOrPullRequestsWithDetails.graphql_fragments())

        query = """
            query GqlGetIssueOrPullRequestsWithDetails(
                $owner: String!
                $repo: String!
                $issue_or_pr_number: Int!
                $limit_comments: Int!
                $limit_events: Int!
            ) {
                repository(owner: $owner, name: $repo) {
                    issueOrPullRequest(number: $issue_or_pr_number) {
                        ... on Issue {
                            ...gqlIssue

                            comments(last: $limit_comments) {
                                nodes {
                                    ...gqlComment
                                }
                            }
                            timelineItems( itemTypes: [CROSS_REFERENCED_EVENT, REFERENCED_EVENT], last: $limit_events) {
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
                                    ... on ReferencedEvent {
                                        actor {
                                            ...gqlActor
                                        }
                                        createdAt
                                        subject {
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
                        ... on PullRequest {
                            ...gqlPullRequest

                            comments(last: $limit_comments) {
                                nodes {
                                    ...gqlComment
                                }
                            }
                            timelineItems( itemTypes: [CROSS_REFERENCED_EVENT, REFERENCED_EVENT], last: $limit_events) {
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
                                    ... on ReferencedEvent {
                                        actor {
                                            ...gqlActor
                                        }
                                        createdAt
                                        subject {
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
    def to_graphql_query_variables(
        owner: str, repo: str, issue_or_pr_number: int, limit_comments: int, limit_events: int
    ) -> dict[str, Any]:
        return {
            "owner": owner,
            "repo": repo,
            "issue_or_pr_number": issue_or_pr_number,
            "limit_comments": limit_comments,
            "limit_events": limit_events,
        }


# class GqlGetIssuesWithDetails(BaseGqlQuery, BaseModel):
#     repository: GqlGetIssuesWithDetailsRepository

#     @staticmethod
#     def graphql_fragments() -> set[str]:
#         return {*Issue.graphql_fragments(), *Comment.graphql_fragments(), *TimelineItem.graphql_fragments()}

#     @staticmethod
#     def graphql_query() -> str:
#         fragments = "\n".join(GqlGetIssuesWithDetails.graphql_fragments())
#         query = """
#             query GqlGetIssuesWithDetails(
#                 $owner: String!
#                 $repo: String!
#                 $issue_number: Int!
#                 $limit_comments: Int!
#                 $limit_events: Int!
#             ) {
#                 repository(owner: $owner, name: $repo) {
#                     issue(number: $issue_number) {
#                         ...gqlIssue
#                         comments(last: $limit_comments) {
#                             nodes {
#                                 ...gqlComment
#                             }
#                         }
#                         closedByPullRequestsReferences(last: 5) {
#                             nodes {
#                                 ...gqlPullRequest
#                             }
#                         }
#                         timelineItems( itemTypes: [CROSS_REFERENCED_EVENT, REFERENCED_EVENT], last: $limit_events) {
#                             nodes {
#                                 ... on CrossReferencedEvent {
#                                     actor {
#                                         ...gqlActor
#                                     }
#                                     createdAt
#                                     source {
#                                         ... on Issue {
#                                             ...gqlIssue
#                                         }
#                                         ... on PullRequest {
#                                             ...gqlPullRequest
#                                         }
#                                     }
#                                 }
#                                 ... on ReferencedEvent {
#                                     actor {
#                                         ...gqlActor
#                                     }
#                                     createdAt
#                                     subject {
#                                         ... on Issue {
#                                             ...gqlIssue
#                                     }
#                                         ... on PullRequest {
#                                             ...gqlPullRequest
#                                         }
#                                     }
#                                 }
#                             }
#                         }
#                     }
#                 }
#             }
#         """
#         query = dedent(text=query)

#         return fragments + "\n" + query

#     @staticmethod
#     def to_graphql_query_variables(owner: str, repo: str, issue_number: int, limit_comments: int, limit_events: int) -> dict[str, Any]:
#         return {
#             "owner": owner,
#             "repo": repo,
#             "issue_number": issue_number,
#             "limit_comments": limit_comments,
#             "limit_events": limit_events,
#         }


class GqlSearchIssueOrPullRequestsWithDetails(BaseGqlQuery, BaseModel):
    search: Nodes[GqlIssueWithDetails | GqlPullRequestWithDetails]

    @staticmethod
    def graphql_fragments() -> set[str]:
        return {*GqlIssueWithDetails.graphql_fragments(), *GqlPullRequestWithDetails.graphql_fragments()}

    @staticmethod
    def graphql_query() -> str:
        fragments = "\n".join(GqlSearchIssueOrPullRequestsWithDetails.graphql_fragments())
        query = """
            query GqlSearchIssueOrPullRequestsWithDetails(
                $search_query: String!
                $limit_issues_or_pull_requests: Int!
                $limit_comments: Int!
                $limit_events: Int!
            ) {
                search(query: $search_query, type: ISSUE, first: $limit_issues_or_pull_requests) {
                    issueCount
                    nodes {
                        ... on PullRequest {
                            ...gqlPullRequest
                            comments(last: $limit_comments) {
                                nodes {
                                    ...gqlComment
                                }
                            }
                            timelineItems(itemTypes: [CROSS_REFERENCED_EVENT], last: $limit_events) {
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
                        ... on Issue {
                            ...gqlIssue
                            comments(last: $limit_comments) {
                                nodes {
                                    ...gqlComment
                                }
                            }
                            timelineItems(itemTypes: [CROSS_REFERENCED_EVENT], last: $limit_events) {
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
    def to_graphql_query_variables(
        query: str, limit_issues_or_pull_requests: int, limit_comments: int, limit_events: int
    ) -> dict[str, Any]:
        return {
            "search_query": query,
            "limit_issues_or_pull_requests": limit_issues_or_pull_requests,
            "limit_comments": limit_comments,
            "limit_events": limit_events,
        }


# class GqlGetPullRequestWithDetailsRepository(BaseModel):
#     pull_request: GqlPullRequestWithDetails = Field(validation_alias="pullRequest")

#     @staticmethod
#     def graphql_fragments() -> set[str]:
#         return {*GqlPullRequestWithDetails.graphql_fragments()}


# class GqlGetPullRequestWithDetails(BaseGqlQuery, BaseModel):
#     repository: GqlGetPullRequestWithDetailsRepository

#     @staticmethod
#     def graphql_fragments() -> set[str]:
#         return {*PullRequest.graphql_fragments(), *Comment.graphql_fragments(), *TimelineItem.graphql_fragments()}

#     @staticmethod
#     def graphql_query() -> str:
#         fragments = "\n".join(GqlGetPullRequestWithDetails.graphql_fragments())
#         query = """
#             query GqlGetPullRequestWithDetails(
#                 $owner: String!
#                 $repo: String!
#                 $pull_request_number: Int!
#                 $limit_comments: Int!
#                 $limit_events: Int!
#             ) {
#                 repository(owner: $owner, name: $repo) {
#                     pullRequest(number: $pull_request_number) {
#                         ...gqlPullRequest
#                         comments(last: $limit_comments) {
#                             nodes {
#                                 ...gqlComment
#                             }
#                         }
#                         timelineItems( itemTypes: [CROSS_REFERENCED_EVENT, REFERENCED_EVENT], last: $limit_events) {
#                             nodes {
#                                 ... on CrossReferencedEvent {
#                                     actor {
#                                         ...gqlActor
#                                     }
#                                     createdAt
#                                     source {
#                                         ... on Issue {
#                                             ...gqlIssue
#                                         }
#                                         ... on PullRequest {
#                                             ...gqlPullRequest
#                                         }
#                                     }
#                                 }
#                                 ... on ReferencedEvent {
#                                     actor {
#                                         ...gqlActor
#                                     }
#                                     createdAt
#                                     subject {
#                                         ... on Issue {
#                                             ...gqlIssue
#                                     }
#                                         ... on PullRequest {
#                                             ...gqlPullRequest
#                                         }
#                                     }
#                                 }
#                             }
#                         }
#                     }
#                 }
#             }
#         """
#         query = dedent(text=query)

#         return fragments + "\n" + query

#     @staticmethod
#     def to_graphql_query_variables(
#         owner: str, repo: str, pull_request_number: int, limit_comments: int, limit_events: int
#     ) -> dict[str, Any]:
#         return {
#             "owner": owner,
#             "repo": repo,
#             "pull_request_number": pull_request_number,
#             "limit_comments": limit_comments,
#             "limit_events": limit_events,
#         }


# class GqlSearchPullRequestsWithDetails(BaseGqlQuery, BaseModel):
#     search: Nodes[GqlPullRequestWithDetails]

#     @staticmethod
#     def graphql_fragments() -> set[str]:
#         return {*GqlPullRequestWithDetails.graphql_fragments()}

#     @staticmethod
#     def graphql_query() -> str:
#         fragments = "\n".join(GqlSearchPullRequestsWithDetails.graphql_fragments())
#         query = """
#             query GqlSearchPullRequestsWithDetails(
#                 $search_query: String!
#                 $limit_pull_requests: Int!
#                 $limit_comments: Int!
#                 $limit_events: Int!
#             ) {
#                 search(query: $search_query, type: ISSUE, first: $limit_pull_requests) {
#                     nodes {
#                         ... on PullRequest {
#                             ...gqlPullRequest
#                             comments(last: $limit_comments) {
#                                 nodes {
#                                     ...gqlComment
#                                 }
#                             }
#                             timelineItems(itemTypes: [CROSS_REFERENCED_EVENT], last: $limit_events) {
#                                 nodes {
#                                     ... on CrossReferencedEvent {
#                                         actor {
#                                             ...gqlActor
#                                         }
#                                         createdAt
#                                         source {
#                                             ... on Issue {
#                                                 ...gqlIssue
#                                             }
#                                             ... on PullRequest {
#                                                 ...gqlPullRequest
#                                             }
#                                         }
#                                     }
#                                 }
#                             }
#                         }
#                     }
#                 }
#             }
#         """
#         query = dedent(text=query)

#         return fragments + "\n" + query

#     @staticmethod
#     def to_graphql_query_variables(query: str, limit_pull_requests: int, limit_comments: int, limit_events: int) -> dict[str, Any]:
#         return {
#             "search_query": query,
#             "limit_pull_requests": limit_pull_requests,
#             "limit_comments": limit_comments,
#             "limit_events": limit_events,
#         }
