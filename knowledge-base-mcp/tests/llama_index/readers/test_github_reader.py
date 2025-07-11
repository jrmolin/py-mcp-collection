from typing import TYPE_CHECKING

import pytest

from knowledge_base_mcp.llama_index.readers.github import GithubIssuesReader

if TYPE_CHECKING:
    from llama_index.core.schema import Document


@pytest.mark.not_on_ci
def test_github_reader():
    client = GithubIssuesReader(
        owner="strawgate",
        repo="fastmcp-agents",
    )

    first_issue: Document | None = None
    first_comment: Document | None = None

    for issue in client.lazy_load_data(include_comments=True, sort="created", direction="asc"):
        if issue.metadata["type"] == "issue":
            first_issue = issue
        if issue.metadata["type"] == "comment":
            first_comment = issue

        if first_issue is not None and first_comment is not None:
            break

    assert first_issue is not None
    assert first_comment is not None

    assert first_issue.metadata["issue"] == 11
    assert first_comment.metadata["issue"] == 11


@pytest.mark.not_on_ci
async def test_github_reader_async():
    client = GithubIssuesReader(
        owner="strawgate",
        repo="fastmcp-agents",
    )

    async for issue in client.alazy_load_data(include_comments=True):
        print(issue)
