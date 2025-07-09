"""Tests for the async_web_reader."""

from datetime import UTC, datetime, timedelta

import pytest
from aiohttp import web
from aiohttp.test_utils import TestClient

from knowledge_base_mcp.llama_index.readers.web import (
    AsyncWebReader,
    FailedRequest,
    FinishedRequest,
    QueuedRequest,
    StartRequest,
    SuccessfulRequest,
    WebPage,
    build_url,
)


def test_build_url():
    """Test the build_url function."""
    assert build_url("http://example.com/foo/", "/bar") == "http://example.com/bar"
    assert build_url("http://example.com/foo/", "bar") == "http://example.com/foo/bar"
    assert build_url("http://example.com/foo", "bar") == "http://example.com/bar"
    assert build_url("http://example.com/foo", "/bar") == "http://example.com/bar"


def test_start_request_from_queued():
    """Test creating a StartRequest from a QueuedRequest."""
    url = "http://example.com"
    queued_request = QueuedRequest(url=url)
    start_request = StartRequest.from_queued_request(queued_request)
    assert start_request.url == url
    assert start_request.queued == queued_request.queued
    assert isinstance(start_request.started, datetime)


def test_failed_request_from_start():
    """Test creating a FailedRequest from a StartRequest."""
    url = "http://example.com"
    start_request = StartRequest(url=url)
    error_message = "File not found"
    failed_request = FailedRequest.from_start_request(start_request, error_message)
    assert failed_request.url == url
    assert failed_request.queued == start_request.queued
    assert failed_request.started == start_request.started
    assert failed_request.error == error_message
    assert isinstance(failed_request.finished, datetime)


def test_successful_request_from_start():
    """Test creating an SuccessfulRequest from a StartRequest."""
    url = "http://example.com"
    webpage = WebPage(url=url, title="title", content="content")
    start_request = StartRequest(url=url)

    successful_request = SuccessfulRequest.from_start_request(start_request, webpage)

    assert successful_request.url == url
    assert successful_request.webpage == webpage
    assert successful_request.queued == start_request.queued
    assert successful_request.started == start_request.started
    assert isinstance(successful_request.finished, datetime)


def test_finished_request_durations():
    """Test the duration properties of a FinishedRequest."""
    now = datetime.now(tz=UTC)
    queued_time = now - timedelta(seconds=2)
    start_time = now - timedelta(seconds=1)
    finished_time = now

    finished_request = FinishedRequest(url="http://example.com", queued=queued_time, started=start_time, finished=finished_time)

    assert finished_request.wait_duration == pytest.approx(1.0)
    assert finished_request.request_duration == pytest.approx(1.0)
    assert finished_request.total_duration == pytest.approx(2.0)


async def test_extract_title_with_child_urls() -> None:
    """Test the extract_title function."""
    html = (
        "<html><head><title>Test</title></head><body>Hello, world<a href='/child1'>Child 1</a><a href='/child2'>Child 2</a></body></html>"
    )
    base_url = "http://example.com"

    reader = AsyncWebReader(urls=[base_url])

    title, child_urls = reader._extract_relevant_bits(html, base_url)  # pyright: ignore[reportPrivateUsage]
    assert title == "Test"
    assert len(child_urls) == 2
    assert "http://example.com/child1" in child_urls
    assert "http://example.com/child2" in child_urls


async def test_avoid_child_urls_to_images() -> None:
    """Test the extract_title function."""
    html = """
    <a class="reference internal image-reference" href="/docs/reference/query-languages/esql/images/functions/st_xmax.svg" target="_blank">
        <img loading="lazy"  alt="Embedded" src="/docs/reference/query-languages/esql/images/functions/st_xmax.svg" />
    </a>
    """
    base_url = "http://example.com"

    reader = AsyncWebReader(urls=[base_url])

    _, child_urls = reader._extract_relevant_bits(html, base_url)  # pyright: ignore[reportPrivateUsage]

    assert len(child_urls) == 0


async def test_extract_no_title_with_child_urls():
    """Test the extract_child_urls function."""
    html = "<html><body><a href='/child1'>Child 1</a><a href='/child2'>Child 2</a></body></html>"
    base_url = "http://example.com"

    reader = AsyncWebReader(urls=[base_url])
    title, child_urls = reader._extract_relevant_bits(html, base_url)  # pyright: ignore[reportPrivateUsage]
    assert len(child_urls) == 2
    assert "http://example.com/child1" in child_urls
    assert "http://example.com/child2" in child_urls


class TestIntegration:
    """Integration tests for the AsyncWebReader."""

    @pytest.fixture
    async def web_server(self, aiohttp_client):
        """A fixture that sets up a simple test web server."""

        async def success_handler(request):
            """A simple request handler for the test server."""
            return web.Response(
                text="<html><head><title>Test</title></head><body>Hello, world<a href='/child'>link</a></body></html>",
                content_type="text/html",
            )

        async def error_handler(request):
            raise web.HTTPInternalServerError

        async def child_handler(request):
            return web.Response(text="<html><head><title>Child</title></head><body>Child page</body></html>", content_type="text/html")

        app = web.Application()
        app.router.add_get("/", success_handler)
        app.router.add_get("/error", error_handler)
        app.router.add_get("/child", child_handler)

        return await aiohttp_client(app)

    async def test_async_web_reader_success(self, web_server: TestClient):
        """Test the AsyncWebReader for a successful request."""
        url = str(web_server.make_url("/"))
        reader = AsyncWebReader(urls=[url], session=web_server.session)

        documents = [doc async for doc in reader.alazy_load_data()]

        assert len(documents) == 1
        doc = documents[0]
        assert doc.metadata["url"] == url
        assert doc.metadata["title"] == "Test"
        assert "Hello, world" in doc.text

    async def test_async_web_reader_failure(self, web_server):
        """Test the AsyncWebReader for a failed request."""
        url = str(web_server.make_url("/error"))
        reader = AsyncWebReader(urls=[url], session=web_server.session, ignore_errors=True)
        documents = [doc async for doc in reader.alazy_load_data()]
        assert len(documents) == 0

    @pytest.fixture
    async def recursive_web_server(self, aiohttp_client):
        """A fixture that sets up a multi-page server for recursive crawling tests."""

        async def start_page(request):
            return web.Response(
                text="<html><title>Start</title><body><a href='/child1'>Child 1</a><a href='/child2'>Child 2</a></body></html>",
                content_type="text/html",
            )

        async def child1_page(request):
            return web.Response(text="<html><title>Child 1</title><body>Child 1 content</body></html>", content_type="text/html")

        async def child2_page(request):
            # This page should be ignored due to exclude patterns
            return web.Response(text="<html><title>Child 2</title><body>Child 2 content</body></html>", content_type="text/html")

        app = web.Application()
        app.router.add_get("/", start_page)
        app.router.add_get("/child1", child1_page)
        app.router.add_get("/child2", child2_page)

        return await aiohttp_client(app)

    # def test_recursive_web_reader_url_matching(self):
    #     """Test the URL matching logic of the RecursiveAsyncWebReader."""
    #     reader = RecursiveAsyncWebReader(
    #         urls=[],
    #         include_url_patterns=[r"http://example\.com/docs/.*"],
    #         exclude_url_patterns=[r".*/private/.*"],
    #     )

    #     assert reader._url_matches_pattern("http://example.com/docs/main") is True
    #     assert reader._url_matches_pattern("http://example.com/docs/private/page") is False
    #     assert reader._url_matches_pattern("http://example.com/other") is False
    #     assert reader._url_matches_pattern("http://another.com/docs/main") is False

    # async def test_recursive_web_reader_integration(self, recursive_web_server: TestClient):
    #     """Test the RecursiveAsyncWebReader with a live server."""
    #     client = recursive_web_server
    #     base_url = str(client.make_url("/"))

    #     reader = RecursiveAsyncWebReader(
    #         urls=[base_url],
    #         max_requests_per_crawl=10,
    #         include_url_patterns=[f"{base_url}.*"],
    #         exclude_url_patterns=[".*child2"],
    #         max_workers_per_crawl=2,
    #     )
    #     docs = [doc async for doc in reader.alazy_load_data()]

    #     assert len(docs) >= 2
    #     urls = {doc.metadata["url"] for doc in docs}
    #     titles = {doc.metadata["title"] for doc in docs}

    #     assert base_url in urls
    #     assert str(client.make_url("/child1")) in urls
    #     assert str(client.make_url("/child2")) not in urls

    #     assert "Start" in titles
    #     assert "Child 1" in titles
    #     assert "Child 2" not in titles
