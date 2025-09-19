from typing import Any

import pytest
from dirty_equals import IsStr
from fastmcp import FastMCP
from fastmcp.client import Client
from fastmcp.client.transports import FastMCPTransport
from fastmcp.exceptions import ToolError
from fastmcp.tools import Tool
from githubkit.github import GitHub
from inline_snapshot import snapshot

from github_research_mcp.clients.github import get_github_client
from github_research_mcp.models.query.base import AnySymbolsQualifier
from github_research_mcp.models.repository.tree import RepositoryFileCountEntry, RepositoryTreeDirectory
from github_research_mcp.servers.models.repository import FileLines
from github_research_mcp.servers.repository import (
    RepositoryFileWithContent,
    RepositoryServer,
    RepositoryTree,
)


def test_repository_server():
    repository_server = RepositoryServer(github_client=get_github_client())
    assert repository_server is not None


@pytest.fixture
def github_client() -> GitHub[Any]:
    return get_github_client()


@pytest.fixture
def repository_server(github_client: GitHub[Any]):
    return RepositoryServer(github_client=github_client)


async def test_get_repo_files(repository_server: RepositoryServer):
    files = await repository_server.get_files(owner="strawgate", repo="github-issues-e2e-test", paths=["README.md", "test.md"], truncate=10)
    assert files == snapshot(
        [
            RepositoryFileWithContent(
                path="README.md",
                content=FileLines(
                    root={
                        1: "# G.I.T.H.U.B. - The Existential Code Companion",
                        2: "",
                        3: "**Generally Introspective Text Handler for Unrealized Brilliance**",
                        4: "",
                        5: "An AI-powered code editor extension that doesn't just check for syntax errors, but also prompts you with philosophical questions about your code's purpose and your life choices as a developer.",
                        6: "",
                        7: "## What is G.I.T.H.U.B.?",
                        8: "",
                        9: "G.I.T.H.U.B. is more than just another code linter. It's your existential coding companion that asks the deep questions:",
                        10: "",
                    }
                ),
            )
        ]
    )


async def test_get_readmes(repository_server: RepositoryServer):
    context = await repository_server.get_readmes(owner="strawgate", repo="github-issues-e2e-test", truncate=10)
    assert context == snapshot(
        [
            RepositoryFileWithContent(
                path="AGENTS.md",
                content=FileLines(
                    root={
                        1: "# G.I.T.H.U.B. AI Agents Documentation",
                        2: "",
                        3: '*"In the digital realm, we are not alone. Our code is watched over by digital spirits of wisdom and contemplation."*',
                        4: "",
                        5: "This document describes the existential AI agents and automated systems that guide your coding journey in G.I.T.H.U.B.",
                        6: "",
                        7: "## Agent Overview",
                        8: "",
                        9: "### The Philosopher Agent",
                        10: "- **Purpose**: Existential code analysis and philosophical guidance",
                    }
                ),
            ),
            RepositoryFileWithContent(
                path="CONTRIBUTING.md",
                content=FileLines(
                    root={
                        1: "# Contributing to G.I.T.H.U.B. - The Existential Code Companion",
                        2: "",
                        3: '*"Every contribution is a step on the path of digital enlightenment. Welcome, fellow seeker of code wisdom."*',
                        4: "",
                        5: "Thank you for your interest in contributing to G.I.T.H.U.B.! This document provides guidelines for those brave souls who wish to join us on this journey of existential coding.",
                        6: "",
                        7: "## Getting Started",
                        8: "",
                        9: "### Prerequisites",
                        10: "- Python 3.13 or higher",
                    }
                ),
            ),
            RepositoryFileWithContent(
                path="CONTRIBUTORS.md",
                content=FileLines(
                    root={
                        1: "# Contributors",
                        2: "",
                        3: "This project exists thanks to all the people who contribute.",
                        4: "",
                        5: "## Core Team",
                        6: "",
                        7: "- **Test User** - *Project Lead* - [@testuser](https://github.com/testuser)",
                        8: "- **Jane Developer** - *Core Developer* - [@janedev](https://github.com/janedev)",
                        9: "- **Bob Maintainer** - *Maintainer* - [@bobmaintainer](https://github.com/bobmaintainer)",
                        10: "",
                    }
                ),
            ),
            RepositoryFileWithContent(
                path="README.md",
                content=FileLines(
                    root={
                        1: "# G.I.T.H.U.B. - The Existential Code Companion",
                        2: "",
                        3: "**Generally Introspective Text Handler for Unrealized Brilliance**",
                        4: "",
                        5: "An AI-powered code editor extension that doesn't just check for syntax errors, but also prompts you with philosophical questions about your code's purpose and your life choices as a developer.",
                        6: "",
                        7: "## What is G.I.T.H.U.B.?",
                        8: "",
                        9: "G.I.T.H.U.B. is more than just another code linter. It's your existential coding companion that asks the deep questions:",
                        10: "",
                    }
                ),
            ),
        ]
    )


async def test_find_files(repository_server: RepositoryServer):
    tree = await repository_server.find_files(owner="strawgate", repo="github-issues-e2e-test", include=[".py"])
    assert tree == snapshot(
        RepositoryTree(
            directories=[
                RepositoryTreeDirectory(
                    path="src",
                    files=[
                        "__init__.py",
                        "cli.py",
                        "existential_coder.py",
                        "oracle.py",
                        "philosopher_agent.py",
                        "utils.py",
                        "zen_master.py",
                    ],
                ),
                RepositoryTreeDirectory(path="tests", files=["__init__.py", "test_existential_coder.py"]),
            ],
            files=[".python-version", "main.py"],
        )
    )


async def test_count_files(repository_server: RepositoryServer):
    count = await repository_server.get_file_extensions(owner="strawgate", repo="github-issues-e2e-test", top_n=10)
    assert count == snapshot(
        [
            RepositoryFileCountEntry(extension="py", count=10),
            RepositoryFileCountEntry(extension="md", count=9),
            RepositoryFileCountEntry(extension="gitignore", count=1),
            RepositoryFileCountEntry(extension="python-version", count=1),
            RepositoryFileCountEntry(extension="ini", count=1),
            RepositoryFileCountEntry(extension="toml", count=1),
        ]
    )


async def test_search_files(repository_server: RepositoryServer):
    files = await repository_server.search_files(
        owner="strawgate", repo="github-issues-e2e-test", keywords_or_symbols=AnySymbolsQualifier(symbols={"zen"})
    )
    assert files == snapshot([])


async def test_summarize_repository(fastmcp: FastMCP, repository_server: RepositoryServer):
    fastmcp.add_tool(tool=Tool.from_function(fn=repository_server.summarize))

    async with Client[FastMCPTransport](transport=fastmcp) as fastmcp_client:
        context = await fastmcp_client.call_tool(
            "summarize",
            arguments={"owner": "strawgate", "repo": "github-issues-e2e-test"},
        )

    assert context.structured_content == snapshot({"result": IsStr()})


async def test_summarize_repository_error(fastmcp: FastMCP, repository_server: RepositoryServer):
    fastmcp.add_tool(tool=Tool.from_function(fn=repository_server.summarize))

    async with Client[FastMCPTransport](transport=fastmcp) as fastmcp_client:
        with pytest.raises(
            ToolError,
            match=r"Validate repository strawgate/repo-that-does-not-exist: Note -- Repositories that are private will report as not found.",
        ):
            await fastmcp_client.call_tool(
                "summarize",
                arguments={"owner": "strawgate", "repo": "repo-that-does-not-exist"},
            )


async def test_summarize_repository_fastmcp(fastmcp: FastMCP, repository_server: RepositoryServer):
    fastmcp.add_tool(tool=Tool.from_function(fn=repository_server.summarize))

    async with Client[FastMCPTransport](transport=fastmcp) as fastmcp_client:
        context = await fastmcp_client.call_tool(
            "summarize",
            arguments={"owner": "jlowin", "repo": "fastmcp"},
        )

    assert context.structured_content == snapshot({"result": IsStr()})


async def test_summarize_repository_elasticsearch(fastmcp: FastMCP, repository_server: RepositoryServer):
    fastmcp.add_tool(tool=Tool.from_function(fn=repository_server.summarize))

    async with Client[FastMCPTransport](transport=fastmcp) as fastmcp_client:
        context = await fastmcp_client.call_tool(
            "summarize",
            arguments={"owner": "elastic", "repo": "elasticsearch"},
        )
    assert context.structured_content == snapshot({"result": IsStr()})


class TestPrivateMethods:
    async def test_get_repository_tree(self, repository_server: RepositoryServer):
        tree = await repository_server.get_repository_tree(owner="strawgate", repo="github-issues-e2e-test")
        assert tree == snapshot(
            RepositoryTree(
                directories=[
                    RepositoryTreeDirectory(path=".github", files=["PULL_REQUEST_TEMPLATE.md"]),
                    RepositoryTreeDirectory(
                        path=".github/ISSUE_TEMPLATE",
                        files=["bug_report.md", "enlightenment_journey.md", "feature_request.md", "philosophical_question.md"],
                    ),
                    RepositoryTreeDirectory(
                        path="src",
                        files=[
                            "__init__.py",
                            "cli.py",
                            "existential_coder.py",
                            "oracle.py",
                            "philosopher_agent.py",
                            "utils.py",
                            "zen_master.py",
                        ],
                    ),
                    RepositoryTreeDirectory(path="tests", files=["__init__.py", "test_existential_coder.py"]),
                ],
                files=[
                    ".gitignore",
                    ".python-version",
                    "AGENTS.md",
                    "CONTRIBUTING.md",
                    "CONTRIBUTORS.md",
                    "README.md",
                    "main.py",
                    "mypy.ini",
                    "pyproject.toml",
                ],
            )
        )
