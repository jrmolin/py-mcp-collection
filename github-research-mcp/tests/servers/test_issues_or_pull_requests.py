import json
from typing import Any

import pytest
from dirty_equals import IsStr
from fastmcp.client import Client
from fastmcp.client.transports import FastMCPTransport
from fastmcp.server import FastMCP
from fastmcp.tools import Tool
from githubkit.github import GitHub
from inline_snapshot import snapshot

from github_research_mcp.servers.issues_or_pull_requests import IssueOrPullRequestWithDetails, IssuesOrPullRequestsServer
from github_research_mcp.servers.repository import RepositoryServer


def get_structured_content_length(structured_content: dict[str, Any] | None) -> int:
    if structured_content is None:
        return 0

    return len(json.dumps(structured_content))


@pytest.fixture
def repository_server(github_client: GitHub[Any]) -> RepositoryServer:
    return RepositoryServer(github_client=github_client)


def test_issues_server(repository_server: RepositoryServer, github_client: GitHub[Any]):
    issues_server = IssuesOrPullRequestsServer(repository_server=repository_server, github_client=github_client)
    assert issues_server is not None


@pytest.fixture
def issues_or_pr_server(repository_server: RepositoryServer, github_client: GitHub[Any]):
    return IssuesOrPullRequestsServer(repository_server=repository_server, github_client=github_client)


@pytest.mark.asyncio
async def test_research_issue(issues_or_pr_server: IssuesOrPullRequestsServer):
    issue: IssueOrPullRequestWithDetails = await issues_or_pr_server.research_issue_or_pull_request(
        owner="strawgate", repo="github-issues-e2e-test", issue_or_pr_number=1
    )

    assert issue.model_dump() == snapshot(
        {
            "issue_or_pr": {
                "number": 1,
                "title": "This is an issue",
                "body": "It has a description",
                "state": "OPEN",
                "state_reason": None,
                "is_pr": False,
                "author": {"user_type": "User", "login": "strawgate"},
                "author_association": "OWNER",
                "created_at": "2025-09-05T23:03:04+00:00",
                "updated_at": "2025-09-05T23:03:15+00:00",
                "closed_at": None,
                "labels": [{"name": "bug"}],
                "assignees": [{"user_type": "User", "login": "strawgate"}],
            },
            "diff": None,
            "comments": [
                {
                    "body": "it also has a comment",
                    "author": {"user_type": "User", "login": "strawgate"},
                    "author_association": "OWNER",
                    "created_at": "2025-09-05T23:03:15+00:00",
                    "updated_at": "2025-09-05T23:03:15+00:00",
                }
            ],
            "related": [
                {
                    "number": 2,
                    "title": "this is a test pull request",
                    "body": """\
it has a description\r
\r
it has a related issue #1\
""",
                    "state": "OPEN",
                    "is_pr": True,
                    "merged": False,
                    "author": {"user_type": "User", "login": "strawgate"},
                    "created_at": "2025-09-05T23:04:07+00:00",
                    "updated_at": "2025-09-05T23:04:24+00:00",
                    "closed_at": None,
                    "merged_at": None,
                    "merge_commit": None,
                    "labels": [{"name": "bug"}],
                    "assignees": [{"user_type": "User", "login": "strawgate"}],
                }
            ],
        }
    )


@pytest.mark.asyncio
async def test_research_pull_request(issues_or_pr_server: IssuesOrPullRequestsServer):
    issue: IssueOrPullRequestWithDetails = await issues_or_pr_server.research_issue_or_pull_request(
        owner="strawgate", repo="github-issues-e2e-test", issue_or_pr_number=2
    )

    assert issue.model_dump() == snapshot(
        {
            "issue_or_pr": {
                "number": 2,
                "title": "this is a test pull request",
                "body": """\
it has a description\r
\r
it has a related issue #1\
""",
                "state": "OPEN",
                "merged": False,
                "is_pr": True,
                "author": {"user_type": "User", "login": "strawgate"},
                "created_at": "2025-09-05T23:04:07+00:00",
                "merged_at": None,
                "merge_commit": None,
                "updated_at": "2025-09-05T23:04:24+00:00",
                "closed_at": None,
                "labels": [{"name": "bug"}],
                "assignees": [{"user_type": "User", "login": "strawgate"}],
            },
            "diff": [
                {
                    "path": "test.md",
                    "status": "modified",
                    "patch": """\
@@ -1 +1,3 @@
 this is a test file
+
+this is a test modification\
""",
                    "previous_filename": None,
                    "truncated": False,
                }
            ],
            "comments": [
                {
                    "body": "it also has a comment",
                    "author": {"user_type": "User", "login": "strawgate"},
                    "author_association": "OWNER",
                    "created_at": "2025-09-05T23:04:24+00:00",
                    "updated_at": "2025-09-05T23:04:24+00:00",
                }
            ],
            "related": [],
        }
    )


async def test_research_pull_requests(issues_or_pr_server: IssuesOrPullRequestsServer):
    pull_requests: list[IssueOrPullRequestWithDetails] = await issues_or_pr_server.research_issues_or_pull_requests(
        owner="strawgate", repo="github-issues-e2e-test", issue_or_pr="pull_request", keywords={"test"}
    )

    dumped_pull_requests = [pull_request.model_dump() for pull_request in pull_requests]

    assert dumped_pull_requests == snapshot(
        [
            {
                "issue_or_pr": {
                    "number": 2,
                    "title": "this is a test pull request",
                    "body": """\
it has a description\r
\r
it has a related issue #1\
""",
                    "state": "OPEN",
                    "is_pr": True,
                    "merged": False,
                    "author": {"user_type": "User", "login": "strawgate"},
                    "created_at": "2025-09-05T23:04:07+00:00",
                    "updated_at": "2025-09-05T23:04:24+00:00",
                    "closed_at": None,
                    "merged_at": None,
                    "merge_commit": None,
                    "labels": [{"name": "bug"}],
                    "assignees": [{"user_type": "User", "login": "strawgate"}],
                },
                "diff": [
                    {
                        "path": "test.md",
                        "status": "modified",
                        "patch": """\
@@ -1 +1,3 @@
 this is a test file
+
+this is a test modification\
""",
                        "previous_filename": None,
                        "truncated": False,
                    }
                ],
                "comments": [
                    {
                        "body": "it also has a comment",
                        "author": {"user_type": "User", "login": "strawgate"},
                        "author_association": "OWNER",
                        "created_at": "2025-09-05T23:04:24+00:00",
                        "updated_at": "2025-09-05T23:04:24+00:00",
                    }
                ],
                "related": [],
            }
        ]
    )


async def test_research_issues(issues_or_pr_server: IssuesOrPullRequestsServer):
    issues: list[IssueOrPullRequestWithDetails] = await issues_or_pr_server.research_issues_or_pull_requests(
        owner="strawgate", repo="github-issues-e2e-test", issue_or_pr="issue", keywords={"description"}
    )

    dumped_issues = [issue.model_dump() for issue in issues]

    assert dumped_issues == snapshot(
        [
            {
                "issue_or_pr": {
                    "number": 1,
                    "title": "This is an issue",
                    "body": "It has a description",
                    "state": "OPEN",
                    "state_reason": None,
                    "is_pr": False,
                    "author": {"user_type": "User", "login": "strawgate"},
                    "author_association": "OWNER",
                    "created_at": "2025-09-05T23:03:04+00:00",
                    "updated_at": "2025-09-05T23:03:15+00:00",
                    "closed_at": None,
                    "labels": [{"name": "bug"}],
                    "assignees": [{"user_type": "User", "login": "strawgate"}],
                },
                "diff": None,
                "comments": [
                    {
                        "body": "it also has a comment",
                        "author": {"user_type": "User", "login": "strawgate"},
                        "author_association": "OWNER",
                        "created_at": "2025-09-05T23:03:15+00:00",
                        "updated_at": "2025-09-05T23:03:15+00:00",
                    }
                ],
                "related": [
                    {
                        "number": 2,
                        "title": "this is a test pull request",
                        "body": """\
it has a description\r
\r
it has a related issue #1\
""",
                        "state": "OPEN",
                        "is_pr": True,
                        "merged": False,
                        "author": {"user_type": "User", "login": "strawgate"},
                        "created_at": "2025-09-05T23:04:07+00:00",
                        "updated_at": "2025-09-05T23:04:24+00:00",
                        "closed_at": None,
                        "merged_at": None,
                        "merge_commit": None,
                        "labels": [{"name": "bug"}],
                        "assignees": [{"user_type": "User", "login": "strawgate"}],
                    }
                ],
            }
        ]
    )


async def test_summarize_issue(issues_or_pr_server: IssuesOrPullRequestsServer, fastmcp: FastMCP):
    fastmcp.add_tool(tool=Tool.from_function(fn=issues_or_pr_server.summarize_issue_or_pull_request))

    async with Client[FastMCPTransport](transport=fastmcp) as fastmcp_client:
        context = await fastmcp_client.call_tool(
            "summarize_issue_or_pull_request", arguments={"owner": "strawgate", "repo": "github-issues-e2e-test", "issue_or_pr_number": 1}
        )

    assert context.structured_content == snapshot(
        {
            "owner": "strawgate",
            "repo": "github-issues-e2e-test",
            "issue_or_pr_number": 1,
            "summary": IsStr(),
        }
    )


async def test_summarize_pull_request(issues_or_pr_server: IssuesOrPullRequestsServer, fastmcp: FastMCP):
    fastmcp.add_tool(tool=Tool.from_function(fn=issues_or_pr_server.summarize_issue_or_pull_request))

    async with Client[FastMCPTransport](transport=fastmcp) as fastmcp_client:
        context = await fastmcp_client.call_tool(
            "summarize_issue_or_pull_request", arguments={"owner": "strawgate", "repo": "github-issues-e2e-test", "issue_or_pr_number": 2}
        )

    assert context.structured_content == snapshot(
        {
            "owner": "strawgate",
            "repo": "github-issues-e2e-test",
            "issue_or_pr_number": 2,
            "summary": IsStr(),
        }
    )


async def test_summarize_issues(issues_or_pr_server: IssuesOrPullRequestsServer, fastmcp: FastMCP):
    fastmcp.add_tool(tool=Tool.from_function(fn=issues_or_pr_server.summarize_issues_or_pull_requests))

    async with Client[FastMCPTransport](transport=fastmcp) as fastmcp_client:
        context = await fastmcp_client.call_tool(
            "summarize_issues_or_pull_requests",
            arguments={
                "owner": "strawgate",
                "repo": "github-issues-e2e-test",
                "issue_or_pr": "issue",
                "keywords": {"karma"},
                "summary_focus": "Focus on bugs related to Karma analysis",
            },
        )

    assert context.structured_content == snapshot(
        {
            "owner": "strawgate",
            "repo": "github-issues-e2e-test",
            "keywords": ["karma"],
            "summary": IsStr(),
            "items_reviewed": {
                "issue:5": "[ENLIGHTENMENT] Positive Code Karma is not enough",
                "issue:4": "[BUG] Currently, bad Karma is not that bad",
            },
        }
    )


async def test_summarize_issues_related_to_issue(issues_or_pr_server: IssuesOrPullRequestsServer, fastmcp: FastMCP):
    fastmcp.add_tool(tool=Tool.from_function(fn=issues_or_pr_server.summarize_issues_or_pull_requests))

    async with Client[FastMCPTransport](transport=fastmcp) as fastmcp_client:
        context = await fastmcp_client.call_tool(
            "summarize_issues_or_pull_requests",
            arguments={
                "owner": "strawgate",
                "repo": "github-issues-e2e-test",
                "issue_or_pr": "issue",
                "keywords": {"karma"},
                "summary_focus": "Determine if the related to issue is a duplicate of any issues in the repository",
                "related_to_issue": {"owner": "strawgate", "repo": "github-issues-e2e-test", "issue_number": 4},
            },
        )

    assert context.structured_content == snapshot(
        {
            "owner": "strawgate",
            "repo": "github-issues-e2e-test",
            "keywords": ["karma"],
            "summary": IsStr(),
            "items_reviewed": {
                "issue:5": "[ENLIGHTENMENT] Positive Code Karma is not enough",
                "issue:4": "[BUG] Currently, bad Karma is not that bad",
            },
        }
    )
