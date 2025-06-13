from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest
from langchain_core.documents import Document
from syrupy.assertion import SnapshotAssertion

from doc_store_vector_search_mcp.etl.store import (
    KnowledgeBaseVectorStoreManager,
)
from doc_store_vector_search_mcp.servers.load import DocumentServer

MEATY_CONTENT_CHUNK = """
This is a chunk of meaty content.

It has multiple lines. The lines are separated by a newline character. And they get pretty long.
This is another line. That is also pretty long. It is also separated by a newline character.

And it has multiple paragraphs.
"""


@pytest.fixture
def test_files(tmp_path: Path):
    md_file = tmp_path / "file.md"
    md_file.write_text(f"""
# Header 1a

{MEATY_CONTENT_CHUNK}

## Header 2

{MEATY_CONTENT_CHUNK}

### Header 3

{MEATY_CONTENT_CHUNK}

#### Header 4

{MEATY_CONTENT_CHUNK}

# Header 1b

{MEATY_CONTENT_CHUNK}

## Header 2b

{MEATY_CONTENT_CHUNK}
""")
    txt_file = tmp_path / "file.txt"
    txt_file.write_text("Just a plain text file.")
    return tmp_path


@pytest.fixture
def dummy_project_vectorstore():
    # This can be None or a simple object, since we patch the only method used
    return object()


@pytest.fixture(autouse=True)
def freezer_time(freezer):
    freezer.move_to("2025-01-01 12:00:00")


@pytest.mark.asyncio
async def test_load_directories_loader_splitter_combo(test_files, dummy_project_vectorstore, snapshot: SnapshotAssertion):
    server = DocumentServer(project_name="test_project", project_vectorstore=dummy_project_vectorstore)

    captured = []

    async def fake_add_markdown_documents(self, docs: list[Document], metadata: dict[str, Any]):  # noqa: ARG001
        metadata["source"] = "test_files"
        for d in docs:
            d.metadata["source"] = "test_files"
        captured.append(
            {
                "docs": [{"page_content": d.page_content, "metadata": d.metadata} for d in docs],
                "metadata": metadata,
            }
        )

    with patch.object(KnowledgeBaseVectorStoreManager, "add_markdown_documents", new=fake_add_markdown_documents):
        summary = await server.load_directories(
            knowledge_base="test_kb",
            directories=[str(test_files)],
        )

    snapshot.assert_match(
        {
            "summary": summary,
            "calls": captured,
        }
    )


async def test_load_webpage(dummy_project_vectorstore, snapshot: SnapshotAssertion):
    server = DocumentServer(project_name="test_project", project_vectorstore=dummy_project_vectorstore)

    captured = []

    async def fake_add_markdown_documents(self, docs: list[Document], metadata: dict[str, Any]):  # noqa: ARG001
        metadata["source"] = "test_files"
        for d in docs:
            d.metadata["source"] = "test_files"
        captured.append(
            {
                "docs": [{"page_content": d.page_content, "metadata": d.metadata} for d in docs],
                "metadata": metadata,
            }
        )

    with patch.object(KnowledgeBaseVectorStoreManager, "add_markdown_documents", new=fake_add_markdown_documents):
        summary = await server.load_webpage(
            knowledge_base="test_kb",
            urls=["https://www.example.com"],
        )

    snapshot.assert_match(
        {
            "summary": summary,
            "calls": captured,
        }
    )


async def test_load_webpage_recursive(dummy_project_vectorstore, snapshot: SnapshotAssertion):
    server = DocumentServer(project_name="test_project", project_vectorstore=dummy_project_vectorstore)

    captured = []

    async def fake_add_markdown_documents(self, docs: list[Document], metadata: dict[str, Any]):  # noqa: ARG001
        metadata["source"] = "test_files"
        for d in docs:
            d.metadata["source"] = "test_files"
        captured.append(
            {
                "docs": [{"page_content": d.page_content, "metadata": d.metadata} for d in docs],
                "metadata": metadata,
            }
        )

    with patch.object(KnowledgeBaseVectorStoreManager, "add_markdown_documents", new=fake_add_markdown_documents):
        summary = await server.load_webpage(
            knowledge_base="test_kb",
            urls=["https://www.example.com"],
            recursive=True,
        )

    snapshot.assert_match(
        {
            "summary": summary,
            "calls": captured,
        }
    )
