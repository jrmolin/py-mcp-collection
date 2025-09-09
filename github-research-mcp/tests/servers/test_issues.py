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
from github_research_mcp.servers.issues import IssuesServer, IssueWithDetails

if TYPE_CHECKING:
    from fastmcp.client.client import CallToolResult


def test_issues_server():
    issues_server = IssuesServer(client=get_github_client())
    assert issues_server is not None


def get_structured_content_length(structured_content: dict[str, Any] | None) -> int:
    if structured_content is None:
        return 0

    return len(json.dumps(structured_content))


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
                }
            ],
        }
    )


@pytest.mark.asyncio
async def test_research_issue_fastmcp(issues_server: IssuesServer):
    issue: IssueWithDetails = await issues_server.research_issue(owner="jlowin", repo="fastmcp", issue_number=815)

    assert issue.model_dump() == snapshot(
        {
            "issue": {
                "number": 815,
                "title": "support expand the fields contained in a pydandic model in the parameters of a tool",
                "body": """\
### Enhancement Description

https://fastapi.tiangolo.com/tutorial/body-multiple-params/?h=embed#embed-a-single-body-parameter

When using fastapi, we can use the embed field to decide whether to embed all fields of the pydandic model object.
like this:

```python
from typing import Annotated

from fastapi import Body, FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None


@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Annotated[Item, Body(embed=True)]):
    results = {"item_id": item_id, "item": item}
    return results
```

if embed is false, then we can use `update_item(name, description, price, tax) ` but not `update_item(item_object)`

I want the following effect:
```python
from fasctmcp import Body
...
class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None

@mcp.tool(
  name="update_item"
)
async def update_item(item: Annotated[Item, Body(embed=False)]):
    results = {"item": item}
    return results
```
then the json schema exclude item but include name, description, price and tax

### Use Case

_No response_

### Proposed Implementation

```Python

```\
""",
                "state": "CLOSED",
                "state_reason": "COMPLETED",
                "author": {"user_type": "User", "login": "lichenglin020"},
                "author_association": "NONE",
                "created_at": "2025-06-12T06:48:46+00:00",
                "updated_at": "2025-06-12T15:23:10+00:00",
                "closed_at": None,
                "labels": [{"name": "enhancement"}],
                "assignees": [],
            },
            "comments": [
                {
                    "body": "Personally I think FastAPI's embed behavior is bad practice because it means adding a second body parameter to your function signature is a breaking change. I think the current implementation is very clear; whatever is in your function signature is exposed to the LLM, and you can use `exclude_args` and `tool.from_tool` to make changes to it deterministically. I don't think the framework should have an opinion on how to transform those args in unpredictable ways, and as a user you can deconstruct and construct the `Item` object yourself from any combination of fields.",
                    "author": {"user_type": "User", "login": "jlowin"},
                    "author_association": "OWNER",
                    "created_at": "2025-06-12T15:23:10+00:00",
                    "updated_at": "2025-06-12T15:23:10+00:00",
                }
            ],
            "related": [{'number':1784 ,'title':'Support unpacking Pydantic models into top-level tool parameters','body':"""\
### Enhancement

Currently, when using a Pydantic model as a single argument in a tool, the generated tool schema nests the entire model under that argument name. For example:

```python
class Params(BaseModel):
    image_url: str
    resize: bool = False
    width: int = 800
    format: Literal["jpeg", "png", "webp"] = "jpeg"

@mcp.tool
def process_image(params: Params) -> dict:
    ...
```

Generates a JSON schema like:

```json
{
  "properties": {
    "params": {
      "type": "object",
      "properties": {
        "image_url": {"type": "string"},
        "resize": {"type": "boolean"},
        "width": {"type": "integer"},
        "format": {"enum": ["jpeg", "png", "webp"]}
      }
    }
  }
}
```

This means all model fields are wrapped under `params`, which is not ideal for LLM-facing schemas.
Instead, I want the ability to **unpack** the model so that its fields are exposed as **top-level tool parameters**, like this:

```json
{
  "properties": {
    "image_url": {"type": "strin

... [the middle portion has been truncated, retrieve object directly to get the full body] ... \n\

ack[Params]) -> dict:
    ...
```

Or via annotation:

```python
@mcp.tool
def process_image(
    params: Annotated[Params, mcp.Unpack]
) -> dict:
    ...
```

The `Unpack` marker would signal that `Params` should be flattened into top-level fields in the schema.
This would be **explicit and opt-in**, avoiding the implicit/ambiguous semantics that some dislike in FastAPI’s `embed` behavior.

---

## Closing note

I know [[issue #815](https://github.com/jlowin/fastmcp/issues/815)](https://github.com/jlowin/fastmcp/issues/815) discussed this and was closed with the argument that “the current implementation is clear.”
However, in practice for complex tools, unpacking provides:

* A **much better LLM interaction experience**,
* Cleaner developer ergonomics,
* And the ability to **reuse parameter models** across tools without forcing extra nesting.

I believe having an **explicit, opt-in mechanism** (not implicit) would address previous concerns while giving users the flexibility they need.

... [the middle portion has been truncated, retrieve object directly to get the full body]\
""",'state':'CLOSED','state_reason':'COMPLETED','author':{'user_type':'User','login':'Haskely'},'author_association':'NONE','created_at':'2025-09-08T06:59:43+00:00','updated_at':'2025-09-09T04:06:18+00:00','closed_at':None ,'labels':[{'name':'enhancement'},{'name':'server'}],'assignees':[]}],
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
                    }
                ],
            }
        ]
    )


async def test_search_issues_fastmcp(issues_server: IssuesServer, fastmcp: FastMCP):
    fastmcp.add_tool(tool=Tool.from_function(fn=issues_server.research_issues_by_keywords))

    async with Client[FastMCPTransport](transport=fastmcp) as fastmcp_client:
        issues: CallToolResult = await fastmcp_client.call_tool(
            "research_issues_by_keywords",
            arguments={
                "owner": "jlowin",
                "repo": "fastmcp",
                "keywords": ["schema", "output", "response", "payload", "format", "JSON schema"],
            },
        )

    structured_content_length = get_structured_content_length(issues.structured_content)

    assert structured_content_length > 5000

    assert structured_content_length < 500000

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
            "issues_reviewed": [{"number": 1, "title": "This is an issue"}],
        }
    )


async def test_summarize_search_issues_fastmcp(issues_server: IssuesServer, fastmcp: FastMCP):
    fastmcp.add_tool(tool=Tool.from_function(fn=issues_server.summarize_issues_by_keywords))

    async with Client[FastMCPTransport](transport=fastmcp) as fastmcp_client:
        summary: CallToolResult = await fastmcp_client.call_tool(
            "summarize_issues_by_keywords",
            arguments={
                "owner": "jlowin",
                "repo": "fastmcp",
                "keywords": ["banner", "server", "logs", "startup"],
                "summary_focus": "Issues with the server banner appearing in the logs on server startup",
            },
        )

    assert summary.structured_content is not None

    structured_content_length = get_structured_content_length(summary.structured_content)

    assert structured_content_length > 100

    assert structured_content_length < 10000
