from typing import TYPE_CHECKING, Any

import pytest
from dirty_equals import IsStr
from fastmcp import FastMCP
from fastmcp.client import Client
from fastmcp.client.transports import FastMCPTransport
from fastmcp.experimental.sampling.handlers.openai import OpenAISamplingHandler
from fastmcp.tools import Tool
from inline_snapshot import snapshot
from openai import OpenAI

from github_research_mcp.clients.github import get_github_client
from github_research_mcp.servers.issues import IssuesServer, IssueWithDetails

if TYPE_CHECKING:
    from fastmcp.client.client import CallToolResult


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


@pytest.mark.asyncio
async def test_research_issue_fastmcp(issues_server: IssuesServer):
    issue: IssueWithDetails = await issues_server.research_issue(owner="jlowin", repo="fastmcp", issue_number=1602)

    assert issue.model_dump() == snapshot(
        {
            "issue": {
                "number": 1602,
                "title": "Introduce inline snapshots",
                "body": """\
### Enhancement

We should introduce the inline snapshots plugin to allow thorough capture and testing of more complex data structures like to input and output schemas\
""",
                "state": "CLOSED",
                "state_reason": "COMPLETED",
                "author": {"user_type": "User", "login": "strawgate"},
                "author_association": "COLLABORATOR",
                "created_at": "2025-08-24T13:48:06+00:00",
                "updated_at": "2025-08-25T18:53:39+00:00",
                "closed_at": None,
                "labels": [{"name": "enhancement"}, {"name": "tests"}],
                "assignees": [],
            },
            "comments": [
                {
                    "body": """\
/marvin please review https://15r10nk.github.io/inline-snapshot/latest/ and add the inline snapshot dependency and then go through the tests and identify good candidates for inline snapshots and add `== snapshot()` to them -- I'll populate the snapshots for you.

Also comment out code that can be removed once the snapshot is present\
""",
                    "author": {"user_type": "User", "login": "strawgate"},
                    "author_association": "COLLABORATOR",
                    "created_at": "2025-08-24T14:32:15+00:00",
                    "updated_at": "2025-08-24T14:32:15+00:00",
                },
                {
                    "body": """\
**Claude finished @strawgate's task** —— [View job](https://github.com/jlowin/fastmcp/actions/runs/17189970390) • [`claude/issue-1602-20250824-1432`](https://github.com/jlowin/fastmcp/tree/claude/issue-1602-20250824-1432) • [Create PR ➔](https://github.com/jlowin/fastmcp/compare/main...claude/issue-1602-20250824-1432?quick_pull=1&title=feat%3A%20introduce%20inline%20snapshots%20for%20testing%20complex%20data%20structures&body=Introduces%20inline%20snapshot%20testing%20capability%20as%20requested%20in%20issue%20%231602.%0A%0A%23%23%20Changes%0A-%20Add%20inline-snapshot%20dependency%20to%20dev%20requirements%0A-%20Implement%20snapshot%20testing%20in%20key%20areas%3A%0A%20%20-%20Tool%20output%20schema%20tests%20for%20complex%20wrapping%20structures%0A%20%20-%20OpenAPI%20reference%20resolution%20tests%20for%20schema%20processing%0A%20%20-%20JSON%20schema%20compression%20tests%20for%20%24defs%20handling%0A-%20Comment%20out%20redundant%20assertion%20code%20replaced%20by%20snapshots%0A%0AThis%20enables%20thorough%20capture%20and%20testing%20of%20complex%20schemas%20like%20tool%20input/output%20and%20OpenAPI%20specifications.%0A%0AGenerated%20with%20%5BClaude%20Code%5D%28https%3A//claude.ai/code%29)

---
### ✅ Inline snapshots successfully introduced

#### Task List
- [x] Review inline-snapshot documentation
- [x] Set up development environment (uv sync)
- [x] Add inline-snapshot dependency to project
- [x] Analyze existing tests for good snapshot candidates
- [x] Implement snapshot assertions in identified tests
- [x] Comment out redundant code
- [x] Run validation workflow (pre-commit, pytest)
- [x] Commit and push changes

#### Implementation Complete ✅

Successfully introduced inline snapshot testing for complex data structures in FastMCP:

**🔧 Changes Made:**
- ✅ Added `inline-snapshot>=0.15.0` to dev dependencies
- ✅ Updated **3 key test files** with snapshots for complex schema testing:
  1. **Tool Schema Tests** - Complex output schema wrapping structures
  2. **OpenAPI Processing** - Schema reference resolution and transformation
  3. **JSON Schema Compression** - Complex $defs and reference handling
- ✅ Commented out redundant assertion code as requested
- ✅ All tests pass with snapshot validation
- ✅ Pre-commit hooks validate successfully

**🎯 Key Benefits Achieved:**
- **Better maintainability** for complex nested data structure tests
- **Easier updates** using `--inline-snapshot=fix` when schemas evolve
- **Improved readability** focusing on test behavior vs verbose assertions
- **Perfect fit** for testing tool input/output schemas and OpenAPI specifications

The inline snapshots are now ready for use. You can populate additional snapshots by running tests with `--inline-snapshot=create`.



---\
""",
                    "author": {"user_type": "Bot", "login": "marvin-context-protocol"},
                    "author_association": "CONTRIBUTOR",
                    "created_at": "2025-08-24T14:32:32+00:00",
                    "updated_at": "2025-08-24T14:42:11+00:00",
                },
            ],
            "related": [
                {
                    "number": 1602,
                    "title": "Introduce inline snapshots",
                    "body": """\
### Enhancement

We should introduce the inline snapshots plugin to allow thorough capture and testing of more complex data structures like to input and output schemas\
""",
                    "state": "CLOSED",
                    "state_reason": "COMPLETED",
                    "author": {"user_type": "User", "login": "strawgate"},
                    "author_association": "COLLABORATOR",
                    "created_at": "2025-08-24T13:48:06+00:00",
                    "updated_at": "2025-08-25T18:53:39+00:00",
                    "closed_at": None,
                    "labels": [{"name": "enhancement"}, {"name": "tests"}],
                    "assignees": [],
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


async def test_search_issues_fastmcp(issues_server: IssuesServer, fastmcp: FastMCP):
    fastmcp.add_tool(tool=Tool.from_function(fn=issues_server.research_issues_by_keywords))

    async with Client[FastMCPTransport](transport=fastmcp) as fastmcp_client:
        issues: CallToolResult = await fastmcp_client.call_tool(
            "research_issues_by_keywords", arguments={"owner": "jlowin", "repo": "fastmcp", "keywords": ["banner"], "limit_issues": 1}
        )

    assert issues.structured_content is not None


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

    async with Client[FastMCPTransport](fastmcp) as client:
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


async def test_summarize_search_issues_fastmcp(issues_server: IssuesServer, fastmcp: FastMCP):
    fastmcp.add_tool(tool=Tool.from_function(fn=issues_server.summarize_issues_by_keywords))

    async with Client[FastMCPTransport](transport=fastmcp) as fastmcp_client:
        summary: CallToolResult = await fastmcp_client.call_tool(
            "summarize_issues_by_keywords",
            arguments={"owner": "jlowin", "repo": "fastmcp", "keywords": ["banner"], "summary_focus": "Issues with the server banner"},
        )

    assert summary.structured_content is not None
