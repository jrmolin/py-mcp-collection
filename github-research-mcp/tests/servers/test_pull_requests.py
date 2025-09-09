import json
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
from github_research_mcp.servers.pull_requests import PullRequestDetailsWithDiff, PullRequestsServer, PullRequestWithDetails

if TYPE_CHECKING:
    from fastmcp.client.client import CallToolResult


def test_pull_requests_server():
    pull_requests_server = PullRequestsServer(client=get_github_client())
    assert pull_requests_server is not None


def get_structured_content_length(structured_content: dict[str, Any] | None) -> int:
    if structured_content is None:
        return 0

    return len(json.dumps(structured_content))


@pytest.fixture
def pull_requests_server():
    return PullRequestsServer(client=get_github_client())


@pytest.mark.asyncio
async def test_research_pull_request(pull_requests_server: PullRequestsServer):
    pull_request: PullRequestDetailsWithDiff = await pull_requests_server.research_pull_request(
        owner="strawgate", repo="github-issues-e2e-test", pull_request_number=2
    )

    assert pull_request.model_dump() == snapshot(
        {
            "details": {
                "pull_request": {
                    "number": 2,
                    "title": "this is a test pull request",
                    "body": """\
it has a description\r
\r
it has a related issue #1\
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
                },
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
            },
            "diff": {
                "owner": "strawgate",
                "repo": "github-issues-e2e-test",
                "pull_request_number": 2,
                "diffs": [
                    {
                        "path": "test.md",
                        "sha": "14767718072cdd9a709b1e33cfd6c69677bdff01",
                        "status": "modified",
                        "patch": """\
@@ -1 +1,3 @@
 this is a test file
+
+this is a test modification\
""",
                    }
                ],
            },
        }
    )


@pytest.mark.asyncio
async def test_research_pull_request_fastmcp(pull_requests_server: PullRequestsServer):
    pull_request: PullRequestDetailsWithDiff = await pull_requests_server.research_pull_request(
        owner="jlowin", repo="fastmcp", pull_request_number=2
    )

    assert pull_request.model_dump() == snapshot(
        {
            "details": {
                "pull_request": {
                    "number": 2,
                    "title": "Add github workflows",
                    "body": "",
                    "state": "MERGED",
                    "merged": True,
                    "author": {"user_type": "User", "login": "jlowin"},
                    "created_at": "2024-11-30T14:01:24+00:00",
                    "updated_at": "2024-11-30T14:13:32+00:00",
                    "closed_at": "2024-11-30T14:13:31+00:00",
                    "merged_at": "2024-11-30T14:13:31+00:00",
                    "merge_commit": {"oid": "56481d0bdfd0f122bb9991e1109d8f2dc7de2599"},
                    "labels": [],
                    "assignees": [],
                },
                "comments": [],
                "related": [
                    {
                        "number": 2,
                        "title": "Add github workflows",
                        "body": "",
                        "state": "MERGED",
                        "merged": True,
                        "author": {"user_type": "User", "login": "jlowin"},
                        "created_at": "2024-11-30T14:01:24+00:00",
                        "updated_at": "2024-11-30T14:13:32+00:00",
                        "closed_at": "2024-11-30T14:13:31+00:00",
                        "merged_at": "2024-11-30T14:13:31+00:00",
                        "merge_commit": {"oid": "56481d0bdfd0f122bb9991e1109d8f2dc7de2599"},
                        "labels": [],
                        "assignees": [],
                    },
                    {
                        "number": 2,
                        "title": "Add github workflows",
                        "body": "",
                        "state": "MERGED",
                        "merged": True,
                        "author": {"user_type": "User", "login": "jlowin"},
                        "created_at": "2024-11-30T14:01:24+00:00",
                        "updated_at": "2024-11-30T14:13:32+00:00",
                        "closed_at": "2024-11-30T14:13:31+00:00",
                        "merged_at": "2024-11-30T14:13:31+00:00",
                        "merge_commit": {"oid": "56481d0bdfd0f122bb9991e1109d8f2dc7de2599"},
                        "labels": [],
                        "assignees": [],
                    },
                    {
                        "number": 2,
                        "title": "Add github workflows",
                        "body": "",
                        "state": "MERGED",
                        "merged": True,
                        "author": {"user_type": "User", "login": "jlowin"},
                        "created_at": "2024-11-30T14:01:24+00:00",
                        "updated_at": "2024-11-30T14:13:32+00:00",
                        "closed_at": "2024-11-30T14:13:31+00:00",
                        "merged_at": "2024-11-30T14:13:31+00:00",
                        "merge_commit": {"oid": "56481d0bdfd0f122bb9991e1109d8f2dc7de2599"},
                        "labels": [],
                        "assignees": [],
                    },
                    {
                        "number": 1543,
                        "title": "new OpenAPI parser does not correctly handle explode setting of parameter when generating URL",
                        "body": """\
### Description

The new OpenAPI parser `fastmcp.experimental.server.openapi.FastMCPOpenAPI` does not correctly compose URLs that have a parameter defined in an OpenAPI spec with `explode` set to `false` and with `style` set to `pipeDelimited` or to `form`.  \n\

What happens: For example a parameter with the `form` style and `explode` set to `false` generates an url with `param=1&param=2&param=3`.

What I expect: The url contains `param=1,2,3`

Note that this is similar to bug #1004 which occurs in the old parser.

### Example Code

```Python
from typing import List

import fastmcp
import httpx
import pytest
from fastmcp.experimental.server.openapi import FastMCPOpenAPI
from fastmcp.experimental.utilities.openapi import convert_openapi_schema_to_json_schema


def _make_server_and_capture_urls(openapi_dict: dict, args: dict) -> List[str]:
    calls: List[str] = []

    async def handler(request: httpx.Request):
        calls.append(str(request.url))
        return httpx.Response(200, json

... [the middle portion has been truncated, retrieve object directly to get the full body] ... \n\

                          "name": "ids",
                            "in": "query",
                            "style": "pipeDelimited",
                            "explode": False,
                            "schema": {"type": "array", "items": {"type": "string"}},
                        }
                    ],
                    "responses": {"200": {"description": "ok"}},
                }
            }
        },
    }

    urls = _make_server_and_capture_urls(openapi, {"ids": ["1", "2", "3"]})
    assert any(
        url.endswith("/echo?ids=1|2|3") for url in urls
    ), f"Expected pipe-delimited value, got: {urls}"
```

### Version Information

```Text
FastMCP version:                                                          2.11.3
MCP version:                                                              1.13.0
Python version:                                                           3.13.3
Platform:                                      macOS-15.6-arm64-arm-64bit-Mach-O
```

... [the middle portion has been truncated, retrieve object directly to get the full body]\
""",
                        "state": "OPEN",
                        "state_reason": None,
                        "author": {"user_type": "User", "login": "uppersaranac"},
                        "author_association": "NONE",
                        "created_at": "2025-08-19T15:01:10+00:00",
                        "updated_at": "2025-08-19T20:11:53+00:00",
                        "closed_at": None,
                        "labels": [{"name": "bug"}, {"name": "openapi"}],
                        "assignees": [],
                    },
                ],
            },
            "diff": {
                "owner": "jlowin",
                "repo": "fastmcp",
                "pull_request_number": 2,
                "diffs": [
                    {
                        "path": ".github/ai-labeler.yml",
                        "sha": "23a7dc1d3c55b84d4a90afd4af9cce2de2264bf2",
                        "status": "added",
                        "patch": """\
@@ -0,0 +1,2 @@
+context-files:
+  - README.md\
""",
                    },
                    {
                        "path": ".github/workflows/ai-labeler.yml",
                        "sha": "41d5853fe0ecdaaf0e8e1f82eeb9a9e6c1df6d58",
                        "status": "added",
                        "patch": """\
@@ -0,0 +1,23 @@
+name: AI Labeler
+
+on:
+  issues:
+    types: [opened, reopened]
+  issue_comment:
+    types: [created]
+  pull_request:
+    types: [opened, reopened]
+
+jobs:
+  ai-labeler:
+    runs-on: ubuntu-latest
+    permissions:
+      contents: read
+      issues: write
+      pull-requests: write
+    steps:
+      - uses: actions/checkout@v4
+      - uses: jlowin/ai-labeler@v0.5.0
+        with:
+          openai-api-key: ${{ secrets.OPENAI_API_KEY }}
+          controlflow-llm-model: openai/gpt-4o-mini\
""",
                    },
                    {
                        "path": ".github/workflows/run-tests.yml",
                        "sha": "86609284e2702c88b8457cfa6b0abd4233e15d67",
                        "status": "added",
                        "patch": """\
@@ -0,0 +1,35 @@
+name: Run tests
+
+env:
+  # enable colored output
+  PY_COLORS: 1
+
+on:
+  push:
+    branches: ["main"]
+  pull_request:
+  workflow_dispatch:
+
+permissions:
+  contents: read
+
+jobs:
+  run_tests:
+    name: Run tests
+    runs-on: ubuntu-latest
+
+    steps:
+      - uses: actions/checkout@v4
+
+      - name: Install uv
+        uses: astral-sh/setup-uv@v4
+
+      - name: Set up Python
+        run: uv python install 3.11
+
+      - name: Install FastMCP
+        run: uv sync --all-extras --dev
+
+      - name: Run tests
+        run: uv run pytest -vv
+        if: ${{ !(github.event.pull_request.head.repo.fork) }}\
""",
                    },
                    {
                        "path": "examples/echo.py",
                        "sha": "2a81ca4c00969b141202398599fbc0068728f2ae",
                        "status": "added",
                        "patch": '''\
@@ -0,0 +1,19 @@
+"""
+FastMCP Echo Server
+"""
+
+from fastmcp import FastMCP
+
+
+# Create server
+mcp = FastMCP("Echo Server")
+
+
+@mcp.tool()
+def echo(text: str) -> str:
+    """Echo the input text"""
+    return text
+
+
+if __name__ == "__main__":
+    mcp.run()\
''',
                    },
                    {
                        "path": "pyproject.toml",
                        "sha": "ca524787b01262764e3d2a6d186b76a89018085a",
                        "status": "modified",
                        "patch": """\
@@ -29,6 +29,7 @@ dev = [
     "copychat>=0.5.2",
     "ipython>=8.12.3",
     "pdbpp>=0.10.3",
+    "pytest-xdist>=3.6.1",
     "pytest>=8.3.3",
     "pytest-asyncio>=0.23.5",
 ]\
""",
                    },
                    {
                        "path": "src/fastmcp/server.py",
                        "sha": "54cf5dff6c430e87b1eb5f5daf200cce91f64ea5",
                        "status": "modified",
                        "patch": '''\
@@ -279,6 +279,7 @@ def wrapper() -> Any:
     async def run_stdio_async(self) -> None:
         """Run the server using stdio transport."""
         async with stdio_server() as (read_stream, write_stream):
+            print(f'Starting "{self.name}"...')
             await self._mcp_server.run(
                 read_stream,
                 write_stream,\
''',
                    },
                    {
                        "path": "uv.lock",
                        "sha": "72b2ceeed242776be54693596dec8c0d05ee77a0",
                        "status": "modified",
                        "patch": """\
@@ -198,6 +198,15 @@ wheels = [
     { url = "https://files.pythonhosted.org/packages/02/cc/b7e31358aac6ed1ef2bb790a9746ac2c69bcb3c8588b41616914eb106eaf/exceptiongroup-1.2.2-py3-none-any.whl", hash = "sha256:3111b9d131c238bec2f8f516e123e14ba243563fb135d3fe885990585aa7795b", size = 16453 },
 ]
 \n\
+[[package]]
+name = "execnet"
+version = "2.1.1"
+source = { registry = "https://pypi.org/simple" }
+sdist = { url = "https://files.pythonhosted.org/packages/bb/ff/b4c0dc78fbe20c3e59c0c7334de0c27eb4001a2b2017999af398bf730817/execnet-2.1.1.tar.gz", hash = "sha256:5189b52c6121c24feae288166ab41b32549c7e2348652736540b9e6e7d4e72e3", size = 166524 }
+wheels = [
+    { url = "https://files.pythonhosted.org/packages/43/09/2aea36ff60d16dd8879bdb2f5b3ee0ba8d08cbbdcdfe870e695ce3784385/execnet-2.1.1-py3-none-any.whl", hash = "sha256:26dee51f1b80cebd6d0ca8e74dd8745419761d3bef34163928cbebbdc4749fdc", size = 40612 },
+]
+
 [[package]]
 name = "executing"
 version = "2.1.0"
@@ -222,7 +231,7 @@ wheels = [
 \n\
 [[package]]
 name = "fastmcp"
-version = "0.1.1.dev3+gbffea91.d20241130"
+version = "0.2.1.dev8+gfc560b3.d20241130"
 source = { editable = "." }
 dependencies = [
     { name = "httpx" },
@@ -239,6 +248,7 @@ dev = [
     { name = "pdbpp" },
     { name = "pytest" },
     { name = "pytest-asyncio" },
+    { name = "pytest-xdist" },
 ]
 \n\
 [package.metadata]
@@ -257,6 +267,7 @@ dev = [
     { name = "pdbpp", specifier = ">=0.10.3" },
     { name = "pytest", specifier = ">=8.3.3" },
     { name = "pytest-asyncio", specifier = ">=0.23.5" },
+    { name = "pytest-xdist", specifier = ">=3.6.1" },
 ]
 \n\
 [[package]]
@@ -691,6 +702,19 @@ wheels = [
     { url = "https://files.pythonhosted.org/packages/96/31/6607dab48616902f76885dfcf62c08d929796fc3b2d2318faf9fd54dbed9/pytest_asyncio-0.24.0-py3-none-any.whl", hash = "sha256:a811296ed596b69bf0b6f3dc40f83bcaf341b155a269052d82efa2b25ac7037b", size = 18024 },
 ]
 \n\
+[[package]]
+name = "pytest-xdist"
+version = "3.6.1"
+source = { registry = "https://pypi.org/simple" }
+dependencies = [
+    { name = "execnet" },
+    { name = "pytest" },
+]
+sdist = { url = "https://files.pythonhosted.org/packages/41/c4/3c310a19bc1f1e9ef50075582652673ef2bfc8cd62afef9585683821902f/pytest_xdist-3.6.1.tar.gz", hash = "sha256:ead156a4db231eec769737f57668ef58a2084a34b2e55c4a8fa20d861107300d", size = 84060 }
+wheels = [
+    { url = "https://files.pythonhosted.org/packages/6d/82/1d96bf03ee4c0fdc3c0cbe61470070e659ca78dc0086fb88b66c185e2449/pytest_xdist-3.6.1-py3-none-any.whl", hash = "sha256:9ed4adfb68a016610848639bb7e02c9352d5d9f03d04809919e2dafc3be4cca7", size = 46108 },
+]
+
 [[package]]
 name = "python-dotenv"
 version = "1.0.1"\
""",
                    },
                ],
            },
        }
    )


async def test_search_pull_requests(pull_requests_server: PullRequestsServer):
    pull_requests: list[PullRequestWithDetails] = await pull_requests_server.research_pull_requests_by_keywords(
        owner="strawgate", repo="github-issues-e2e-test", keywords={"issue"}
    )
    dumped_pull_requests: list[dict[str, Any]] = [pull_request.model_dump() for pull_request in pull_requests]
    assert dumped_pull_requests == snapshot(
        [
            {
                "pull_request": {
                    "number": 2,
                    "title": "this is a test pull request",
                    "body": """\
it has a description\r
\r
it has a related issue #1\
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
                },
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


async def test_search_pull_requests_fastmcp(pull_requests_server: PullRequestsServer, fastmcp: FastMCP):
    fastmcp.add_tool(tool=Tool.from_function(fn=pull_requests_server.research_pull_requests_by_keywords))

    async with Client[FastMCPTransport](transport=fastmcp) as fastmcp_client:
        pull_requests: CallToolResult = await fastmcp_client.call_tool(
            "research_pull_requests_by_keywords",
            arguments={
                "owner": "jlowin",
                "repo": "fastmcp",
                "keywords": ["schema", "output", "response", "payload", "format", "JSON schema"],
            },
        )

    structured_content_length = get_structured_content_length(pull_requests.structured_content)

    assert structured_content_length > 5000

    assert structured_content_length < 500000

    assert pull_requests.structured_content is not None


@pytest.fixture
def fastmcp(openai_client: OpenAI):
    return FastMCP(
        sampling_handler=OpenAISamplingHandler(
            default_model="gemini-2.0-flash",  # pyright: ignore[reportArgumentType]
            client=openai_client,
        )
    )


async def test_summarize_pull_request(pull_requests_server: PullRequestsServer, fastmcp: FastMCP):
    fastmcp.add_tool(Tool.from_function(pull_requests_server.summarize_pull_request))

    async with Client[FastMCPTransport](fastmcp) as client:
        summary = await client.call_tool(
            "summarize_pull_request",
            arguments={"owner": "strawgate", "repo": "github-issues-e2e-test", "pull_request_number": 2, "summary_focus": "the issue"},
        )

    assert summary.structured_content == snapshot(
        {
            "owner": "strawgate",
            "repo": "github-issues-e2e-test",
            "pull_request_number": 2,
            "summary": IsStr(),
        }
    )


async def test_summarize_search_pull_requests(pull_requests_server: PullRequestsServer, fastmcp: FastMCP):
    fastmcp.add_tool(tool=Tool.from_function(fn=pull_requests_server.summarize_pull_requests_by_keywords))

    async with Client[FastMCPTransport](transport=fastmcp) as fastmcp_client:
        summary: CallToolResult = await fastmcp_client.call_tool(
            "summarize_pull_requests_by_keywords",
            arguments={"owner": "strawgate", "repo": "github-issues-e2e-test", "keywords": ["issue"], "summary_focus": "the issue"},
        )

    assert summary.structured_content == snapshot(
        {
            "owner": "strawgate",
            "repo": "github-issues-e2e-test",
            "keywords": ["issue"],
            "summary": IsStr(),
            "pull_requests_reviewed": [{"number": 2, "title": "this is a test pull request"}],
        }
    )


async def test_summarize_search_pull_requests_fastmcp(pull_requests_server: PullRequestsServer, fastmcp: FastMCP):
    fastmcp.add_tool(tool=Tool.from_function(fn=pull_requests_server.summarize_pull_requests_by_keywords))

    async with Client[FastMCPTransport](transport=fastmcp) as fastmcp_client:
        summary: CallToolResult = await fastmcp_client.call_tool(
            "summarize_pull_requests_by_keywords",
            arguments={
                "owner": "jlowin",
                "repo": "fastmcp",
                "keywords": ["banner", "server", "logs", "startup"],
                "summary_focus": "Pull requests relating to the server banner that appears on server startup",
            },
        )

    assert summary.structured_content is not None

    structured_content_length = get_structured_content_length(summary.structured_content)

    assert structured_content_length > 100

    assert structured_content_length < 10000
