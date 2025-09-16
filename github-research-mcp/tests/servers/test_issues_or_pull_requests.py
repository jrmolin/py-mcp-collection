import json
from typing import Any
from unittest.mock import AsyncMock

import pytest
from dirty_equals import IsPartialDict, IsStr
from fastmcp.client import Client
from fastmcp.client.transports import FastMCPTransport
from fastmcp.server import FastMCP
from fastmcp.tools import Tool
from githubkit.github import GitHub
from inline_snapshot import snapshot

from github_research_mcp.servers.issues_or_pull_requests import IssueOrPullRequestWithDetails, IssuesOrPullRequestsServer
from github_research_mcp.servers.repository import RepositoryServer, RepositorySummary
from tests.constants import MOCK_GITHUB_REPOSITORY_SUMMARY


def get_structured_content_length(structured_content: dict[str, Any] | None) -> int:
    if structured_content is None:
        return 0

    return len(json.dumps(structured_content))


@pytest.fixture
def repository_server() -> RepositoryServer:
    repository_server: AsyncMock = AsyncMock(spec=RepositoryServer)
    repository_server.summarize = AsyncMock(return_value=RepositorySummary(root=MOCK_GITHUB_REPOSITORY_SUMMARY))
    return repository_server


def test_init_issues_or_pr_server(repository_server: RepositoryServer, github_client: GitHub[Any]):
    issues_server = IssuesOrPullRequestsServer(repository_server=repository_server, github_client=github_client)
    assert issues_server is not None


@pytest.fixture
def issues_or_pr_server(repository_server: RepositoryServer, github_client: GitHub[Any]):
    return IssuesOrPullRequestsServer(repository_server=repository_server, github_client=github_client)


@pytest.mark.asyncio
async def test_get_issue(issues_or_pr_server: IssuesOrPullRequestsServer):
    """Test that the `get_issue_or_pull_request` method returns the correct issue
    along with the comments, related issues and pull requests."""

    issue: IssueOrPullRequestWithDetails = await issues_or_pr_server.get_issue_or_pull_request(
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
async def test_get_pull_request(issues_or_pr_server: IssuesOrPullRequestsServer):
    """Test that the `get_pull_request` method returns the correct pull request along with the comments
    and related issues and pull requests."""

    issue: IssueOrPullRequestWithDetails = await issues_or_pr_server.get_issue_or_pull_request(
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


async def test_research_issue(issues_or_pr_server: IssuesOrPullRequestsServer, fastmcp: FastMCP):
    fastmcp.add_tool(tool=Tool.from_function(fn=issues_or_pr_server.research_issue_or_pull_request))

    async with Client[FastMCPTransport](transport=fastmcp) as fastmcp_client:
        context = await fastmcp_client.call_tool(
            "research_issue_or_pull_request",
            arguments={
                "owner": "strawgate",
                "repo": "github-issues-e2e-test",
                "issue_or_pr_number": 14,
            },
        )
    assert context.structured_content is not None

    assert context.structured_content == snapshot(
        {
            "owner": "strawgate",
            "repo": "github-issues-e2e-test",
            "issue_or_pr_number": 14,
            "findings": IsStr(min_length=100),
            "items_reviewed": IsPartialDict({"issue:4": "[BUG] Currently, bad Karma is not that bad"}),
        }
    )

    assert context.structured_content["items_reviewed"] is not None
    assert len(context.structured_content["items_reviewed"]) > 10


async def test_research_pull_request(issues_or_pr_server: IssuesOrPullRequestsServer, fastmcp: FastMCP):
    fastmcp.add_tool(tool=Tool.from_function(fn=issues_or_pr_server.research_issue_or_pull_request))

    async with Client[FastMCPTransport](transport=fastmcp) as fastmcp_client:
        context = await fastmcp_client.call_tool(
            "research_issue_or_pull_request",
            arguments={
                "owner": "strawgate",
                "repo": "github-issues-e2e-test",
                "issue_or_pr_number": 2,
            },
        )

    assert context.structured_content is not None

    assert context.structured_content == snapshot(
        {
            "owner": "strawgate",
            "repo": "github-issues-e2e-test",
            "issue_or_pr_number": 2,
            "findings": IsStr(min_length=100),
            "items_reviewed": IsPartialDict({"issue:1": "This is an issue"}),
        }
    )

    assert context.structured_content["items_reviewed"] is not None
    assert len(context.structured_content["items_reviewed"]) > 10


async def test_search_issues(issues_or_pr_server: IssuesOrPullRequestsServer, fastmcp: FastMCP):
    fastmcp.add_tool(tool=Tool.from_function(fn=issues_or_pr_server.search_issues_or_pull_requests))

    async with Client[FastMCPTransport](transport=fastmcp) as fastmcp_client:
        context = await fastmcp_client.call_tool(
            "search_issues_or_pull_requests",
            arguments={"owner": "strawgate", "repo": "github-issues-e2e-test", "issue_or_pull_request": "issue", "keywords": ["karma"]},
        )

    assert context.structured_content == snapshot(
        {
            "result": [
                {
                    "issue_or_pr": {
                        "number": 5,
                        "title": "[ENLIGHTENMENT] Positive Code Karma is not enough",
                        "body": """\
## 🧘 Your Digital Enlightenment Journey

*"Every developer's journey is unique, but the destination is the same: understanding."*

### Your Journey
I am improving my code's karma

### Key Insights
I have learned the importance of good code karma

### Current State

New code doesn't achieve enlightenment due to the Pull Request Template only requiring positive karma for any particular code change https://github.com/strawgate/github-issues-e2e-test/blob/f3fd0d116ae7f2ebcb420131298882642eafb3aa/.github/PULL_REQUEST_TEMPLATE.md?plain=1#L23

Karma can be calculated but it can also be felt, requiring a calculation of karma may result in us missing out on Karma improving changes

### Future Aspirations

We should strive to always improve code karma and a score of 1 or 2 is not sufficient to achieve enlightenment in the time frame required

---

*Remember: Every journey is valid, every insight is valuable, and every step forward is progress on the path to digital enlightenment.*\
""",
                        "state": "OPEN",
                        "state_reason": None,
                        "is_pr": False,
                        "author": {"user_type": "User", "login": "strawgate"},
                        "author_association": "OWNER",
                        "created_at": "2025-09-10T18:34:54+00:00",
                        "updated_at": "2025-09-10T18:35:34+00:00",
                        "closed_at": None,
                        "labels": [],
                        "assignees": [],
                    },
                    "diff": None,
                    "comments": [],
                    "related": [],
                },
                {
                    "issue_or_pr": {
                        "number": 11,
                        "title": "[FEATURE] Add `gith-ub karma` command to CLI",
                        "body": """\
## ✨ New Visions for the Digital Realm

*"Every feature is a new path, a new possibility in the journey of code."*

### Describe the Feature
Add a new command `gith-ub karma <file_path>` to the CLI (`src/cli.py`) that allows users to explicitly calculate and view the code karma of a given file. This command should leverage the `calculate_code_karma` and `get_karma_interpretation` functions from `src/utils.py`.

### Why is this Feature Needed?
Currently, code karma is implicitly part of the `analyze` command. A dedicated `karma` command would provide a more direct and focused way for developers to assess the karmic impact of their code, aligning with the project's philosophical goals.

### Proposed Solution
- Add a new `karma` command to `src/cli.py`.
- The command should take `file_path` as an argument.
- It should call `calculate_code_karma` and `get_karma_interpretation`.
- Display the karma score and its interpretation using `rich` panels for a visually appealing output.

### Philosophical Reflection
By providing a direct means to measure code karma, we empower developers to take conscious responsibility for their digital actions. This feature encourages self-reflection and continuous improvement, fostering a more enlightened coding practice.

---

*Remember: Every feature is a step towards a more enlightened digital future. Embrace the creation, and the wisdom will follow.*\
""",
                        "state": "OPEN",
                        "state_reason": None,
                        "is_pr": False,
                        "author": {"user_type": "User", "login": "strawgate"},
                        "author_association": "OWNER",
                        "created_at": "2025-09-13T18:10:57+00:00",
                        "updated_at": "2025-09-13T18:10:57+00:00",
                        "closed_at": None,
                        "labels": [],
                        "assignees": [],
                    },
                    "diff": None,
                    "comments": [],
                    "related": [],
                },
                {
                    "issue_or_pr": {
                        "number": 4,
                        "title": "[BUG] Currently, bad Karma is not that bad",
                        "body": """\
## 🐛 The Universe Has Spoken

*"Every bug is a teacher in disguise, showing us the way forward."*

### Describe the Bug
Regardless of how bad your code's karma is, the worst the analysis will return is "Your code shows some negative patterns. Reflect on your choices and seek improvement."

Code with quite bad karma should contain more stark warnings about the universal impact of such decisions.

### To Reproduce
Write bad code

### Expected Behavior
A stark warning about the impact on my karma

### Actual Behavior
A soft message about self reflection

### Environment
- G.I.T.H.U.B. version: 0.1.0

### Philosophical Reflection
This bug makes me question the value of Karma as an indicator of code quality

---

*Remember: Every bug is a step on the path to digital enlightenment. Embrace the learning, and the solution will reveal itself.*\
""",
                        "state": "OPEN",
                        "state_reason": None,
                        "is_pr": False,
                        "author": {"user_type": "User", "login": "strawgate"},
                        "author_association": "OWNER",
                        "created_at": "2025-09-10T18:31:01+00:00",
                        "updated_at": "2025-09-10T18:31:01+00:00",
                        "closed_at": None,
                        "labels": [{"name": "bug"}],
                        "assignees": [],
                    },
                    "diff": None,
                    "comments": [],
                    "related": [],
                },
                {
                    "issue_or_pr": {
                        "number": 10,
                        "title": "[BUG] `calculate_code_karma` does not account for code duplication",
                        "body": """\
## 🐛 The Universe Has Spoken

*"Every bug is a teacher in disguise, showing us the way forward."*

### Describe the Bug
The `calculate_code_karma` function in `src/utils.py` currently does not penalize for code duplication. While it considers factors like error handling and commenting, it overlooks the significant negative karma associated with copy-pasted code or redundant logic.

### To Reproduce
1. Create a Python file with a function.
2. Copy and paste the same function multiple times without modification.
3. Run `gith-ub analyze` on the file.
4. Observe that the karma score does not significantly decrease due to duplication.

### Expected Behavior
Code duplication should lead to a substantial reduction in the karma score, reflecting the increased technical debt and reduced maintainability.

### Actual Behavior
The karma score remains relatively high, even with egregious levels of code duplication.

### Environment
- G.I.T.H.U.B. version: 0.1.0

### Philosophical Reflection
If every line of code is a prayer, what does it mean to repeat the same prayer endlessly without new insight? Does duplication reflect a lack of understanding, or a fear of abstraction? The Oracle warns of 'karmic consequences of technical debt' – surely duplication is a prime example.

---

*Remember: Every bug is a step on the path to digital enlightenment. Embrace the learning, and the solution will reveal itself.*\
""",  # noqa: RUF001
                        "state": "OPEN",
                        "state_reason": None,
                        "is_pr": False,
                        "author": {"user_type": "User", "login": "strawgate"},
                        "author_association": "OWNER",
                        "created_at": "2025-09-13T18:10:54+00:00",
                        "updated_at": "2025-09-13T18:10:54+00:00",
                        "closed_at": None,
                        "labels": [],
                        "assignees": [],
                    },
                    "diff": None,
                    "comments": [],
                    "related": [],
                },
            ]
        }
    )


async def test_search_pull_requests(issues_or_pr_server: IssuesOrPullRequestsServer, fastmcp: FastMCP):
    fastmcp.add_tool(tool=Tool.from_function(fn=issues_or_pr_server.search_issues_or_pull_requests))

    async with Client[FastMCPTransport](transport=fastmcp) as fastmcp_client:
        context = await fastmcp_client.call_tool(
            "search_issues_or_pull_requests",
            arguments={
                "owner": "strawgate",
                "repo": "github-issues-e2e-test",
                "issue_or_pull_request": "pull_request",
                "keywords": ["test"],
            },
        )

    assert context.structured_content == snapshot(
        {
            "result": [
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
        }
    )
