from typing import Any

import pytest
from dirty_equals import IsStr
from fastmcp import FastMCP
from fastmcp.client import Client, FastMCPTransport
from fastmcp.client.client import CallToolResult
from fastmcp.experimental.sampling.handlers.openai import OpenAISamplingHandler
from fastmcp.tools import Tool
from inline_snapshot import snapshot
from openai import OpenAI

from github_research_mcp.clients.github import get_github_client
from github_research_mcp.servers.issues import IssuesServer, IssueWithDetails


def test_issues_server():
    issues_server = IssuesServer(client=get_github_client())
    assert issues_server is not None


@pytest.fixture
def issues_server():
    return IssuesServer(client=get_github_client())


@pytest.mark.asyncio
async def test_research_issue(issues_server: IssuesServer):
    issue: IssueWithDetails = await issues_server.research_issue(owner="strawgate", repo="github-issues-e2e-test", issue_number=1)

    assert issue.model_dump() == snapshot(
        {
            "issue": {
                "number": 1,
                "title": "This is an issue",
                "body": "It has a description",
                "state": "OPEN",
                "state_reason": None,
                "author": {"user_type": "User", "login": "strawgate"},
                "author_association": "OWNER",
                "created_at": "2025-09-05T23:03:04+00:00",
                "updated_at": "2025-09-05T23:03:15+00:00",
                "closed_at": None,
                "labels": [{"name": "bug"}],
                "assignees": [{"user_type": "User", "login": "strawgate"}],
            },
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
it has a related issue #1 \
""",
                    "state": "OPEN",
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


async def test_search_issues(issues_server: IssuesServer):
    issues: list[IssueWithDetails] = await issues_server.research_issues_by_keywords(
        owner="strawgate", repo="github-issues-e2e-test", keywords={"issue"}
    )
    dumped_issues: list[dict[str, Any]] = [issue.model_dump() for issue in issues]
    assert dumped_issues == snapshot(
        [
            {
                "issue": {
                    "number": 1,
                    "title": "This is an issue",
                    "body": "It has a description",
                    "state": "OPEN",
                    "state_reason": None,
                    "author": {"user_type": "User", "login": "strawgate"},
                    "author_association": "OWNER",
                    "created_at": "2025-09-05T23:03:04+00:00",
                    "updated_at": "2025-09-05T23:03:15+00:00",
                    "closed_at": None,
                    "labels": [{"name": "bug"}],
                    "assignees": [{"user_type": "User", "login": "strawgate"}],
                },
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
it has a related issue #1 \
""",
                        "state": "OPEN",
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


@pytest.fixture
def fastmcp(openai_client: OpenAI):
    return FastMCP(
        sampling_handler=OpenAISamplingHandler(
            default_model="gemini-2.0-flash",  # pyright: ignore[reportArgumentType]
            client=openai_client,
        )
    )


async def test_summarize_issue(issues_server: IssuesServer, fastmcp: FastMCP):
    fastmcp.add_tool(Tool.from_function(issues_server.summarize_issue))

    async with Client(fastmcp) as client:
        summary = await client.call_tool(
            "summarize_issue",
            arguments={"owner": "strawgate", "repo": "github-issues-e2e-test", "issue_number": 1, "summary_focus": "the issue"},
        )

    assert summary.structured_content == snapshot(
        {
            "owner": "strawgate",
            "repo": "github-issues-e2e-test",
            "issue_number": 1,
            "summary": IsStr(),
        }
    )


async def test_summarize_search_issues(issues_server: IssuesServer, fastmcp: FastMCP):
    fastmcp.add_tool(tool=Tool.from_function(fn=issues_server.summarize_issues_by_keywords))

    async with Client[FastMCPTransport](transport=fastmcp) as fastmcp_client:
        summary: CallToolResult = await fastmcp_client.call_tool(
            "summarize_issues_by_keywords",
            arguments={"owner": "strawgate", "repo": "github-issues-e2e-test", "keywords": ["issue"], "summary_focus": "the issue"},
        )

    assert summary.structured_content == snapshot(
        {
            "owner": "strawgate",
            "repo": "github-issues-e2e-test",
            "keywords": ["issue"],
            "summary": IsStr(),
        }
    )


# async def test_get_issue_details(issues_server: IssuesServer):
#     details = await issues_server.get_issue_details(owner="strawgate", repo="github-issues-e2e-test", issue_number=1)

#     assert details.model_dump() == snapshot(
#         {
#             "issue": {
#                 "number": 1,
#                 "title": "This is an issue",
#                 "body": "It has a description",
#                 "state": "OPEN",
#                 "state_reason": None,
#                 "author_association": "OWNER",
#                 "user": {"login": "strawgate", "type": "User"},
#                 "created_at": "2025-09-05T23:03:04+00:00",
#                 "updated_at": "2025-09-05T23:03:15+00:00",
#                 "closed_at": None,
#                 "labels": ["bug"],
#                 "assignees": [{"login": "strawgate", "type": "User"}],
#                 "reactions": {},
#             },
#             "comments": [
#                 {
#                     "id": 3259977946,
#                     "body": "it also has a comment",
#                     "user": {"login": "strawgate", "type": "User"},
#                     "author_association": "OWNER",
#                     "created_at": "2025-09-05T23:03:15+00:00",
#                     "updated_at": "2025-09-05T23:03:15+00:00",
#                     "reactions": {},
#                 }
#             ],
#             "timeline_items": [
#                 {
#                     "actor": {"login": "strawgate", "type": "User"},
#                     "created_at": "2025-09-05T23:04:08+00:00",
#                     "source": {
#                         "type": "pull_request",
#                         "pull_request": {
#                             "number": 2,
#                             "title": "this is a test pull request",
#                             "body": """\
# it has a description\r
# \r
# it has a related issue #1 \
# """,
#                             "state": "OPEN",
#                             "merged": False,
#                             "created_at": "2025-09-05T23:04:07+00:00",
#                             "updated_at": "2025-09-05T23:04:24+00:00",
#                             "closed_at": None,
#                             "merged_at": None,
#                             "merge_commit_sha": None,
#                             "assignees": [{"login": "strawgate", "type": "User"}],
#                         },
#                     },
#                 }
#             ],
#         }
#     )


# @pytest.mark.asyncio
# async def test_get_issue_related_items(issues_server: IssuesServer):
#     timeline = await issues_server.get_issue_related_items(owner="strawgate", repo="github-issues-e2e-test", issue_number=1)

#     dumped_timeline = [event.model_dump() for event in timeline]
#     assert dumped_timeline == snapshot(
#         [
#             {
#                 "actor": {"login": "strawgate", "type": "User"},
#                 "created_at": IsStr(),
#                 "updated_at": IsStr(),
#                 "source": {
#                     "type": "pull_request",
#                     "pull_request": {
#                         "number": 2,
#                         "title": "this is a test pull request",
#                         "body": """\
# it has a description\r
# \r
# it has a related issue #1 \
# """,
#                         "state": "open",
#                         "merged": False,
#                         "created_at": "2025-09-05T23:04:07+00:00",
#                         "updated_at": "2025-09-05T23:04:24+00:00",
#                         "closed_at": None,
#                         "merged_at": None,
#                         "merge_commit_sha": None,
#                         "assignees": [{"login": "strawgate", "type": "User"}],
#                     },
#                 },
#             }
#         ]
#     )


# @pytest.mark.asyncio
# async def test_list_issues(issues_server: IssuesServer):
#     issues = await issues_server.list_issues(owner="strawgate", repo="github-issues-e2e-test")

#     dumped_issues = [issue.model_dump() for issue in issues]

#     assert dumped_issues == snapshot(
#         [
#             {
#                 "number": 2,
#                 "title": "this is a test pull request",
#                 "body": """\
# it has a description\r
# \r
# it has a related issue #1 \
# """,
#                 "state": "open",
#                 "state_reason": None,
#                 "author_association": "OWNER",
#                 "user": {"login": "strawgate", "type": "User"},
#                 "created_at": IsStr(),
#                 "updated_at": IsStr(),
#                 "closed_at": None,
#                 "labels": ["bug"],
#                 "assignees": [{"login": "strawgate", "type": "User"}],
#                 "reactions": {},
#             },
#             {
#                 "number": 1,
#                 "title": "This is an issue",
#                 "body": "It has a description",
#                 "state": "open",
#                 "state_reason": None,
#                 "author_association": "OWNER",
#                 "user": {"login": "strawgate", "type": "User"},
#                 "created_at": IsStr(),
#                 "updated_at": IsStr(),
#                 "closed_at": None,
#                 "labels": ["bug"],
#                 "assignees": [{"login": "strawgate", "type": "User"}],
#                 "reactions": {},
#             },
#         ]
#     )


# @pytest.mark.asyncio
# async def test_list_issue_comments(issues_server: IssuesServer):
#     comments = await issues_server.list_issue_comments(owner="strawgate", repo="github-issues-e2e-test", issue_number=1)

#     dumped_comments = [comment.model_dump() for comment in comments]

#     assert dumped_comments == snapshot(
#         [
#             {
#                 "id": 3259977946,
#                 "body": "it also has a comment",
#                 "user": {"login": "strawgate", "type": "User"},
#                 "author_association": "OWNER",
#                 "created_at": IsStr(),
#                 "updated_at": IsStr(),
#                 "reactions": {},
#             }
#         ]
#     )


# @pytest.fixture
# def fastmcp():
#     return FastMCP(
#         sampling_handler=OpenAISamplingHandler(
#             default_model="gemini-2.0-flash",  # pyright: ignore[reportArgumentType]
#             client=OpenAI(api_key=os.getenv("GOOGLE_API_KEY"), base_url="https://generativelanguage.googleapis.com/v1beta/openai/"),
#         )
#     )


# async def test_summarize_simple_issue(issues_server: IssuesServer, fastmcp: FastMCP):
#     fastmcp.add_tool(Tool.from_function(issues_server.summarize_issue))

#     async with Client(fastmcp) as client:
#         summary = await client.call_tool(
#             "summarize_issue",
#             arguments={
#                 "owner": "strawgate",
#                 "repo": "github-issues-e2e-test",
#                 "issue_number": 1,
#                 "focus": "the issue",
#             },
#         )

#     assert isinstance(summary.content[0], TextContent)
#     assert summary.content[0].text == IsStr()

#     assert summary.structured_content == snapshot(
#         {
#             "owner": "strawgate",
#             "repo": "github-issues-e2e-test",
#             "issue_number": 1,
#             "summary": IsStr(),
#         }
#     )

#     assert summary.data is not None


# async def test_summarize_complex_issue(issues_server: IssuesServer, fastmcp: FastMCP):
#     fastmcp.add_tool(Tool.from_function(issues_server.summarize_issue))

#     async with Client(fastmcp) as client:
#         summary = await client.call_tool(
#             "summarize_issue",
#             arguments={
#                 "owner": "jlowin",
#                 "repo": "fastmcp",
#                 "issue_number": 956,
#                 "focus": "the issue",
#             },
#         )

#     assert isinstance(summary.content[0], TextContent)
#     assert summary.content[0].text == IsStr()

#     assert summary.structured_content == snapshot(
#         {
#             "owner": "jlowin",
#             "repo": "fastmcp",
#             "issue_number": 956,
#             "summary": IsStr(),
#         }
#     )

#     assert summary.data is not None


# async def test_summarize_search_issues(issues_server: IssuesServer, fastmcp: FastMCP):
#     fastmcp.add_tool(Tool.from_function(issues_server.summarize_search_issues))

#     async with Client(fastmcp) as client:
#         summary = await client.call_tool(
#             "summarize_search_issues",
#             arguments={
#                 "owner": "jlowin",
#                 "repo": "fastmcp",
#                 "keywords": ["sampling", "completions"],
#                 "focus": "Looking specifically for valid reports of type errors.",
#             },
#         )

#     assert isinstance(summary.content[0], TextContent)
#     assert summary.content[0].text == IsStr()

#     assert summary.structured_content == snapshot(
#         {
#             "owner": "jlowin",
#             "repo": "fastmcp",
#             "keywords": ["completions", "sampling"],
#             "summary": IsStr(),
#         }
#     )
