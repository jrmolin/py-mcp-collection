import os
from pathlib import Path
import tempfile
from unittest.mock import patch

import pytest
from langchain_core.documents import Document

from doc_store_vector_search_mcp.etl.load import (
    DirectoryLoader,
    JSONJQLoader,
    RecursiveWebLoader,
    SiteMapLoader,
    WebPageLoader,
)

# Mock data for testing
MOCK_WEBPAGE_CONTENT = "<html><body><p>This is a mock webpage.</p></body></html>"
MOCK_SITEMAP_XML = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>http://mockurl.com/page1</loc>
    </url>
    <url>
        <loc>http://mockurl.com/page2</loc>
    </url>
    <url>
        <loc>http://mockurl.com/other</loc>
    </url>
</urlset>
"""
MOCK_JSON_CONTENT = """
{
    "items": [
        {"id": 1, "text": "item 1 content", "category": "A"},
        {"id": 2, "text": "item 2 content", "category": "B"}
    ]
}
"""
MOCK_JSONL_CONTENT = """
{"id": 1, "text": "item 1 content", "category": "A"}
{"id": 2, "text": "item 2 content", "category": "B"}
"""

@pytest.fixture
def temp_dir() -> Path:
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)

@pytest.mark.asyncio
@patch("doc_store_vector_search_mcp.etl.load.WebBaseLoader.alazy_load")
async def test_webpageloader_loads_content(mock_alazy_load):
    mock_document = Document(page_content="This is a mock webpage.", metadata={"source": "http://mockurl.com"})
    mock_alazy_load.return_value = [mock_document].__aiter__()

    url = "http://mockurl.com"
    loader = WebPageLoader()
    documents = [doc async for doc in loader.load(url)]

    assert len(documents) == 1
    assert documents[0].page_content == "This is a mock webpage."
    assert documents[0].metadata["source"] == url


@pytest.mark.asyncio
@patch("doc_store_vector_search_mcp.etl.load.SitemapLoader.alazy_load")
async def test_sitemaploader_loads_filtered_urls(mock_alazy_load):
    mock_document1 = Document(page_content="Page 1 content.", metadata={"source": "http://mockurl.com/page1"})
    mock_document2 = Document(page_content="Page 2 content.", metadata={"source": "http://mockurl.com/page2"})
    mock_alazy_load.return_value = [mock_document1, mock_document2].__aiter__()

    url = "http://mockurl.com/sitemap.xml"
    filter_urls = ["http://mockurl.com/page"]
    loader = SiteMapLoader()
    documents = [doc async for doc in loader.load(url, filter_urls=filter_urls)]

    assert len(documents) == 2
    sources = [doc.metadata["source"] for doc in documents]
    assert "http://mockurl.com/page1" in sources
    assert "http://mockurl.com/page2" in sources
    assert "http://mockurl.com/other" not in sources


@pytest.mark.asyncio
@patch("doc_store_vector_search_mcp.etl.load.RecursiveUrlLoader.alazy_load")
async def test_recursivewebloader_loads_linked_pages(mock_alazy_load):
    mock_document1 = Document(page_content="Main page.", metadata={"source": "http://mockurl.com/main"})
    mock_document2 = Document(page_content="Linked page.", metadata={"source": "http://mockurl.com/linked"})
    mock_alazy_load.return_value = [mock_document1, mock_document2].__aiter__()

    url = "http://mockurl.com/main"
    loader = RecursiveWebLoader()
    documents = [doc async for doc in loader.load(url)]

    assert len(documents) == 2
    sources = [doc.metadata["source"] for doc in documents]
    assert "http://mockurl.com/main" in sources
    assert "http://mockurl.com/linked" in sources


@pytest.mark.asyncio
@patch("doc_store_vector_search_mcp.etl.load.DirectoryLoader.alazy_load")
async def test_directoryloader_loads_specific_file_types(mock_alazy_load):
    mock_document1 = Document(page_content="Markdown content.", metadata={"source": "mock_dir/file.md"})
    mock_document2 = Document(page_content="Text content.", metadata={"source": "mock_dir/file.txt"})
    mock_alazy_load.return_value = [mock_document1, mock_document2].__aiter__()

    with tempfile.TemporaryDirectory() as tmpdir:
        directory_path = tmpdir
        glob_pattern = "**/*.{md,txt}"
        loader = DirectoryLoader()
        documents = [doc async for doc in loader.load(directory_path, glob_pattern=glob_pattern)]

        assert len(documents) == 2
        sources = [doc.metadata["source"] for doc in documents]
        assert "mock_dir/file.md" in sources
        assert "mock_dir/file.txt" in sources
        # Add assertions for content and encoding handling if needed


@pytest.mark.asyncio
async def test_json_jq(temp_dir):
    json_path = temp_dir / "test.json"
    json_path.write_text(MOCK_JSON_CONTENT)
    loader = JSONJQLoader()
    documents = [doc async for doc in loader.load_json(str(json_path), content_key="text")]

    assert len(documents) == 2
    assert documents[0].page_content == "item 1 content"
    assert documents[1].page_content == "item 2 content"

