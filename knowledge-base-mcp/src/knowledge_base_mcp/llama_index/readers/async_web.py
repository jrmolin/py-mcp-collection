import os
from asyncio import Queue as AsyncQueue
from collections.abc import AsyncIterable
from datetime import UTC, datetime
from enum import StrEnum
from functools import cached_property
from pathlib import PurePosixPath
from re import Pattern, match
from typing import Any
from urllib.parse import ParseResult, unquote, urljoin, urlparse

import lxml.html
from aiohttp import ClientSession
from aiohttp.client import ClientTimeout
from fsspec.exceptions import asyncio
from llama_index.core.readers.base import BasePydanticReader
from llama_index.core.schema import Document
from pydantic import BaseModel, ConfigDict, Field, PrivateAttr

from knowledge_base_mcp.utils.logging import BASE_LOGGER

logger = BASE_LOGGER.getChild(__name__)


def build_url(base_url: str, relative_url: str) -> str:
    """Build a full URL from a base URL and a relative URL."""
    return urljoin(base_url, relative_url)


class Url(BaseModel):
    """A URL."""

    model_config = ConfigDict(frozen=True, use_attribute_docstrings=True)

    url: str = Field(...)
    """The URL."""

    _parsed_url: ParseResult = PrivateAttr()
    """The parsed URL."""

    def model_post_init(self, __context: Any) -> None:
        """Post model init."""
        self._parsed_url = urlparse(self.url)

    @property
    def scheme(self) -> str:
        """The scheme of the URL."""
        return self._parsed_url.scheme

    @property
    def hostname(self) -> str | None:
        """The hostname of the URL."""
        return self._parsed_url.hostname

    @property
    def port(self) -> int | None:
        """The port of the URL."""
        return self._parsed_url.port

    @property
    def directory_segments(self) -> list[str]:
        """The directory of the URL."""
        if self.is_directory:
            return self.path_segments

        return self.path_segments[:-1]

    @property
    def is_directory(self) -> bool:
        """Whether the URL is a directory."""
        return self._parsed_url.path.endswith("/")

    @cached_property
    def path_segments(self) -> list[str]:
        """The path segments of the URL."""
        return list(PurePosixPath(unquote(self._parsed_url.path)).parts)

    @property
    def without_query(self) -> str:
        """The URL without the query parameters."""
        return f"{self._parsed_url.netloc}{self._parsed_url.path}"


class CrawlError(Exception):
    """A crawl error."""

    def __init__(self, message: str):
        super().__init__(message)


class CrawlRequestError(CrawlError):
    """A crawl request error."""

    def __init__(self, url: str, error: str):
        super().__init__(f"Error fetching {url}: {error}")


class SharedBaseModel(BaseModel):
    """A base model that is shared in this module."""

    model_config = ConfigDict(frozen=True, use_attribute_docstrings=True)


class WebPage(SharedBaseModel):
    """A model for a web page."""

    url: str
    """URL of the web page."""

    title: str
    """Title of the web page."""

    content: str
    """Content of the web page."""

    child_urls: list[str] = Field(default_factory=list)
    """Child URLs extracted from the web page."""

    headers: dict = Field(default_factory=dict)
    """Headers of the web page."""

    # metadata: dict = Field(default_factory=dict)
    # """Metadata of the web page."""

    def to_document(self) -> Document:
        return Document(
            text=self.content,
            metadata={"url": self.url, "title": self.title, **self.headers},
        )


class QueuedRequest(SharedBaseModel):
    """A queued request"""

    queued: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    """The time the request was queued."""

    url: str
    """The URL of the request."""


class StartRequest(QueuedRequest):
    """A request that work has been started on."""

    started: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    """The time the request was started."""

    @classmethod
    def from_queued_request(cls, queued_request: QueuedRequest) -> "StartRequest":
        return cls(**queued_request.model_dump(), started=datetime.now(tz=UTC))


class FinishedRequest(StartRequest):
    """A request that has been finished."""

    finished: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    """The time the request was finished."""

    @property
    def wait_duration(self) -> float:
        """The duration of the wait time."""
        return (self.started - self.queued).total_seconds()

    @property
    def request_duration(self) -> float:
        """The duration of the request time."""
        return (self.finished - self.started).total_seconds()

    @property
    def total_duration(self) -> float:
        """The total duration of the request."""
        return self.request_duration + self.wait_duration


class FailedRequest(FinishedRequest):
    """A request that failed."""

    error: str
    """The error that occurred."""

    @classmethod
    def from_start_request(cls, start_request: StartRequest, error: str) -> "FailedRequest":
        return cls(**start_request.model_dump(), error=error)

    def to_finished_request(self) -> FinishedRequest:
        return FinishedRequest(
            **self.model_dump(),
        )


class SuccessfulRequest(FinishedRequest):
    """A request that was successful."""

    webpage: WebPage
    """The web page that was requested."""

    @classmethod
    def from_start_request(cls, start_request: StartRequest, webpage: WebPage) -> "SuccessfulRequest":
        return cls(
            **start_request.model_dump(),
            webpage=webpage,
        )

    def to_finished_request(self) -> FinishedRequest:
        return FinishedRequest(
            **self.model_dump(),
        )


class TrackStartCrawl(SharedBaseModel):
    """A started crawl."""

    urls: list[str] = Field(default_factory=list)
    """The URLs to crawl."""

    start_time: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    """The time the crawl was started."""


class TrackEndCrawl(TrackStartCrawl):
    """A completed crawl."""

    end_time: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    """The time the crawl was finished."""

    @classmethod
    def from_start_crawl(cls, start_crawl: TrackStartCrawl) -> "TrackEndCrawl":
        return cls(**start_crawl.model_dump())

    @property
    def duration(self) -> float:
        """The duration of the crawl."""
        return (self.end_time - self.start_time).total_seconds()


class AsyncWebReader(BasePydanticReader):
    """Loader that uses aiohttp to load HTML files."""

    model_config = ConfigDict(arbitrary_types_allowed=True, use_attribute_docstrings=True)

    is_remote: bool = Field(default=True)
    """Whether the data is loaded from a remote API or a local file."""

    urls: list[str]
    """The URLs to read."""

    ignore_errors: bool = Field(default=True)
    """Whether to ignore errors."""

    keep_headers: list[str] = Field(default_factory=lambda: ["content-type"])
    """The headers to keep."""

    session: ClientSession = Field(default_factory=lambda: ClientSession(timeout=ClientTimeout(total=10)))
    """The aiohttp Client session to use."""

    _failed_requests: list[FailedRequest] = PrivateAttr(default_factory=list)
    """Any failed requests."""

    _finished_requests: list[SuccessfulRequest] = PrivateAttr(default_factory=list)
    """Any finished requests."""

    def _extract_child_urls(self, html: lxml.html.HtmlElement, base_url: str) -> list[str]:
        raw_urls = html.xpath("//a/@href").copy()

        urls: set[str] = set()

        for url in raw_urls:
            if not url.startswith(("http", "https")):
                urls.add(build_url(base_url, url))
            else:
                urls.add(url)

        return list(urls)

    def _extract_title(self, html: lxml.html.HtmlElement) -> str:
        return html.xpath("//title/text()")[0]

    def _extract_relevant_bits(self, html: str, base_url: str) -> tuple[str, list[str]]:
        """Extract the relevant bits of the HTML."""
        html_element = lxml.html.fromstring(html)

        title = self._extract_title(html=html_element)
        child_urls = self._extract_child_urls(html=html_element, base_url=base_url)
        return title, child_urls

    async def alazy_load_data(self) -> AsyncIterable[Document]:  # type: ignore
        """Load a webpage."""
        queued_requests = [QueuedRequest(url=url) for url in self.urls]

        async with self.session or ClientSession() as session:
            for queued_request in queued_requests:
                document: SuccessfulRequest | FailedRequest = await self._perform_queued_request(
                    queued_request=queued_request, session=session
                )

                if isinstance(document, FailedRequest):
                    continue

                yield document.webpage.to_document()

    async def _perform_queued_request(self, queued_request: QueuedRequest, session: ClientSession) -> SuccessfulRequest | FailedRequest:
        url = queued_request.url

        start_request = StartRequest.from_queued_request(queued_request)
        try:
            async with session.get(url) as response:
                response.raise_for_status()

                data = await response.text()

                headers = {k: v for k, v in response.headers.items() if k in self.keep_headers}

                title: str
                child_urls: list[str]

                title, child_urls = self._extract_relevant_bits(html=data, base_url=url)

                web_page = WebPage(url=url, title=title, content=data, child_urls=child_urls, headers=headers)

                successful_request = SuccessfulRequest.from_start_request(start_request, web_page)

                logger.info(
                    f"Finished URL {url} in {successful_request.request_duration}s (queued for {successful_request.wait_duration}s)."
                )

                self._finished_requests.append(successful_request)

                return successful_request
        except Exception as e:
            failed_request = FailedRequest.from_start_request(start_request, str(e))
            logger.error(f"Failed to process URL {url}: {e}")  # noqa: TRY400
            self._failed_requests.append(failed_request)
            return failed_request


class CrawlScope(StrEnum):
    """The scope of the crawl."""

    SAME_SCHEME = "same_scheme"
    """Follow links where the scheme (http or https) is the same.

    With a Seed URL of http://docs.example.com:8080, any URLs that have a scheme of `HTTP` will be in scope.
    """

    SAME_PORT = "same_port"
    """Follow links where the port is the same.

    With a Seed URL of http://docs.example.com:8080, any URLs that have a port of `8080` will be in scope.
    """

    SAME_HOSTNAME = "same_hostname"
    """Follow links where the hostname is the same.

    With a Seed URL of http://docs.example.com:8080, any URLs with a hostname of `docs.example.com` will be in scope.
    """

    SAME_DIRECTORY = "same_directory"
    """Follow links where the directory part of the path is the same.

    With a Seed URL of http://.../v1/getting-started/how-to-use, any pages in the `/v1/getting-started/` directory will be in scope.
    """

    SAME_OR_DESCENDENT_DIRECTORY = "same_or_descendent_directory"
    """Follow links where the directory part of the path is the same or a descendent of the seed_url's directory.

    With a Seed URL of http://.../v1/getting-started/how-to-use, any URLs starting with `/v1/getting-started/` will be in scope.
    """


class RecursiveAsyncWebReader(AsyncWebReader):
    """A reader that crawls a website recursively."""

    max_requests_per_crawl: int = Field(default=1000)
    """The maximum number of requests per crawl."""

    max_workers_per_crawl: int = Field(default_factory=lambda: max((os.cpu_count() or 4) // 2, 1))
    """The number of workers to use."""

    crawl_scope: list[CrawlScope] = Field(
        default_factory=lambda: [
            CrawlScope.SAME_SCHEME,
            CrawlScope.SAME_HOSTNAME,
            CrawlScope.SAME_PORT,
            CrawlScope.SAME_OR_DESCENDENT_DIRECTORY,
        ]
    )
    """The scope of the crawl. Each URL found during the crawl must match ALL provided scopes to be crawled.
    If no scopes are provided, all URLs will be crawled. See CrawlScope for details on scope matching."""

    urls: list[str] = Field(alias="seed_urls")
    """The seed URLs to use for the crawl. Seed Urls bypass both crawl scope and url_pattern checks."""

    include_url_patterns: list[str | Pattern] = Field(default_factory=lambda: [r".*"])
    """A list of patterns to apply to child URLs to decide if they should be included in the crawl."""

    exclude_url_patterns: list[str | Pattern] = Field(default_factory=list)
    """A list of patterns to apply to child URLs to decide if they should be excluded from the crawl."""

    _work_to_do: AsyncQueue[QueuedRequest] = PrivateAttr(default_factory=AsyncQueue)
    """The work that is pending to be worked on."""

    _work_to_yield: AsyncQueue[SuccessfulRequest] = PrivateAttr()
    """The work that is ready to be yielded."""

    _urls_seen: set[str] = PrivateAttr(default_factory=set)
    """The URLs that have been seen."""

    _urls_skipped: set[str] = PrivateAttr(default_factory=set)
    """The URLs that have been skipped."""

    _max_requests_hit: bool = PrivateAttr(default=False)
    """Whether the max requests per crawl has been hit."""

    def model_post_init(self, __context: Any) -> None:
        """Post init."""
        self._work_to_yield = AsyncQueue(maxsize=self.max_workers_per_crawl * 2)

        for url in self.urls:
            self._enqueue_url(url=url, force=True)

    @cached_property
    def _parsed_seed_urls(self) -> list[Url]:
        """Parse the seed URLs and return the parsed URLs with their path segments."""
        return [Url(url=url) for url in self.urls]

    def _url_matches_scope(self, parsed_url: Url) -> bool:  # noqa: PLR0911
        """Determine if a URL matches the crawl scope."""
        if len(self.crawl_scope) == 0:
            return True

        for seed_url in self._parsed_seed_urls:
            same_scheme = parsed_url.scheme == seed_url.scheme
            same_hostname = parsed_url.hostname == seed_url.hostname
            same_port = parsed_url.port == seed_url.port

            same_directory = parsed_url.directory_segments == seed_url.directory_segments
            descendent_directory = parsed_url.directory_segments[: len(seed_url.directory_segments)] == seed_url.directory_segments

            for scope in self.crawl_scope:
                if scope == CrawlScope.SAME_SCHEME and not same_scheme:
                    return False
                if scope == CrawlScope.SAME_HOSTNAME and not same_hostname:
                    return False
                if scope == CrawlScope.SAME_PORT and not same_port:
                    return False
                if scope == CrawlScope.SAME_DIRECTORY and not same_directory:
                    return False
                if scope == CrawlScope.SAME_OR_DESCENDENT_DIRECTORY and not same_directory and not descendent_directory:
                    return False

            return True

        return True

    def _url_matches_pattern(self, parsed_url: Url) -> bool:
        """Determine if a URL should be crawled."""
        include = False

        for pattern in self.include_url_patterns:
            if match(pattern, parsed_url.url):
                include = True
                break

        if not include:
            return False

        exclude = False

        for pattern in self.exclude_url_patterns:
            if match(pattern, parsed_url.url):
                exclude = True
                break

        return include and not exclude

    def _enqueue_url(self, url: str, force: bool = False):
        """Enqueue a URL for crawling. Ensuring that matches our patterns and has not been queued."""

        parsed_url = Url(url=url)

        if len(self._urls_seen) >= self.max_requests_per_crawl:
            if not self._max_requests_hit:
                logger.warning(f"Max requests per crawl reached ({self.max_requests_per_crawl}) for {url}")
                self._max_requests_hit = True

            return

        if not force:
            if parsed_url.without_query in self._urls_seen:
                return

            if parsed_url.without_query in self._urls_skipped:
                return

            if not self._url_matches_scope(parsed_url=parsed_url):
                self._urls_skipped.add(parsed_url.without_query)
                return

            if not self._url_matches_pattern(parsed_url=parsed_url):
                self._urls_skipped.add(parsed_url.without_query)
                return

        self._urls_seen.add(parsed_url.without_query)

        self._work_to_do.put_nowait(QueuedRequest(url=url))

    async def alazy_load_data(self) -> AsyncIterable[Document]:  # type: ignore
        """Load a webpage."""

        self._urls_seen.clear()
        self._urls_skipped.clear()
        self._failed_requests.clear()
        self._finished_requests.clear()

        start_crawl = TrackStartCrawl(urls=self.urls)

        async with asyncio.TaskGroup() as tg:
            # Create a task that detects when the crawl is complete
            tg.create_task(self._completion_detector())

            # Create a task for each worker
            for i in range(self.max_workers_per_crawl):
                tg.create_task(self._crawler(worker_id=i))

            # Yield documents as they are completed
            try:
                while successful_request := await self._work_to_yield.get():
                    logger.info(f"Yielding document from {successful_request.webpage.url}")
                    yield successful_request.webpage.to_document()
                    self._work_to_yield.task_done()
                    logger.info(f"{self._work_to_yield.qsize()} buffered documents left to yield")

            # If the queue is shut down, we're done
            except asyncio.QueueShutDown:
                logger.info("Completed crawl, no more work to yield.")

        end_crawl = TrackEndCrawl.from_start_crawl(start_crawl)
        self._log_crawl_summary(end_crawl)

    async def _completion_detector(self) -> None:
        """A task that detects when the crawl is complete."""
        # Wait until the work to do queue is empty
        await self._work_to_do.join()

        # Wait until the work to yield queue is empty
        await self._work_to_yield.join()

        # Shutdown the queues
        self._work_to_do.shutdown()
        self._work_to_yield.shutdown()

    async def _crawler(self, worker_id: int):
        """A worker that crawls a URL."""

        # Create a dedicated client session for the worker
        async with self.session or ClientSession() as session:
            while True:
                try:
                    await self._crawler_step(session=session, worker_id=worker_id)
                except asyncio.QueueShutDown:
                    break

    async def _crawler_step(self, session: ClientSession, worker_id: int) -> None:
        """An individual step of the Crawler worker loop."""

        # Block until a request is available
        queued_request = await self._work_to_do.get()

        logger.debug(f"Worker {worker_id} working on {queued_request.url}")

        # Perform the request
        completed_request: SuccessfulRequest | FailedRequest = await self._perform_queued_request(
            queued_request=queued_request, session=session
        )

        if isinstance(completed_request, FailedRequest):
            self._work_to_do.task_done()
            return

        for child_url in completed_request.webpage.child_urls:
            self._enqueue_url(url=child_url)

        logger.debug(f"Worker {worker_id} done with {queued_request.url}")

        # Block until there is room in the yield queue
        await self._work_to_yield.put(completed_request)

        self._work_to_do.task_done()

    def _log_crawl_summary(self, end_crawl: TrackEndCrawl):
        """Log the crawl summary."""

        average_request_duration = sum(request.request_duration for request in self._finished_requests) / len(self._finished_requests)

        summary = {
            "requests": len(self._finished_requests),
            "failed_requests": len(self._failed_requests),
            "average_request_duration": average_request_duration,
        }

        logger.info(f"Crawl of {len(self.urls)} seed URLs took {end_crawl.duration}: {summary}")
