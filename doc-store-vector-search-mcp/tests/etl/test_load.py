import asyncio

import aiohttp
import pytest

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


# Utility for network check
def is_url_reachable(url):
    async def _check():
        try:
            async with aiohttp.ClientSession() as session, session.get(url) as resp:
                return resp.status == 200
        except Exception:
            return False

    return asyncio.get_event_loop().run_until_complete(_check())


async def test_directoryloader_loads_specific_file_types(tmp_path):
    md_file = tmp_path / "file.md"
    md_file.write_text("Markdown content.")

    txt_file = tmp_path / "file.txt"
    txt_file.write_text("Text content.")

    directory_path = str(tmp_path)

    glob_pattern = "*.md"

    loader = DirectoryLoader()
    documents = [value async for value in loader.load(directory_path, glob=glob_pattern)]

    assert len(documents) == 1
    assert documents[0].page_content == "Markdown content."

    sources = [doc.metadata["source"] for doc in documents]
    assert any("file.md" in s for s in sources)


async def test_load_json_jq(tmp_path):
    json_path = tmp_path / "test.json"
    json_path.write_text(MOCK_JSON_CONTENT)

    loader = JSONJQLoader()

    documents = [value async for value in loader.load(str(json_path), content_key="text")]

    assert len(documents) == 2
    assert documents[0].page_content == "item 1 content"
    assert documents[1].page_content == "item 2 content"


async def test_load_webpage():
    url = "https://www.example.com"

    loader = WebPageLoader()

    documents = [value async for value in loader.load(url)]

    assert any("example" in doc.page_content.lower() for doc in documents)
    assert all("source" in doc.metadata for doc in documents)


async def test_load_sitemap():
    url = "https://www.sitemaps.org/sitemap.xml"

    filter_urls = ["https://www.sitemaps.org/"]
    loader = SiteMapLoader()
    documents = [value async for value in loader.load(url, filter_urls=filter_urls)]

    assert len(documents) > 0
    sources = [doc.metadata["source"] for doc in documents]
    assert any("sitemaps.org" in s for s in sources)


def test_recursivewebloader_loads_linked_pages():
    url = "https://www.sitemaps.org"
    if not is_url_reachable(url):
        pytest.skip(f"{url} is not reachable.")
    loader = RecursiveWebLoader()
    documents = []

    async def gather_docs():
        documents.extend([doc async for doc in loader.load(url)])

    asyncio.get_event_loop().run_until_complete(gather_docs())
    flat_docs = []
    for d in documents:
        if isinstance(d, list):
            flat_docs.extend(d)
        else:
            flat_docs.append(d)
    assert len(flat_docs) > 1
    sources = [doc.metadata["source"] for doc in flat_docs]
    assert any("sitemaps.org" in s for s in sources)
