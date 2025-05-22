from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from typing import Any

from langchain_community.document_loaders import DirectoryLoader as LangchainDirectoryLoader
from langchain_community.document_loaders import RecursiveUrlLoader as LangchainRecursiveUrlLoader
from langchain_community.document_loaders import WebBaseLoader as LangchainWebBaseLoader
from langchain_community.document_loaders.json_loader import JSONLoader as LangchainJSONLoader
from langchain_community.document_loaders.sitemap import SitemapLoader as LangchainSitemapLoader
from langchain_core.documents import Document


type LoaderTypes = WebPageLoader | SiteMapLoader | RecursiveWebLoader | DirectoryLoader | JSONJQLoader


class WebPageLoader:

    @classmethod
    async def load(cls, url: str, **kwargs: Any) -> AsyncGenerator[list[Document], None]:
        loader = LangchainWebBaseLoader(url, **kwargs)

        async for document in loader.alazy_load():
            yield document


class SiteMapLoader:

    @classmethod
    async def load(cls, url: str, filter_urls: list[str] | None = None, **kwargs: Any) -> AsyncGenerator[list[Document], None]:
        loader = LangchainSitemapLoader(url, filter_urls=filter_urls, **kwargs)

        async for document in loader.alazy_load():
            yield document


class RecursiveWebLoader:

    async def load(cls, url: str, **kwargs: Any) -> AsyncGenerator[list[Document], None]:
        loader = LangchainRecursiveUrlLoader(url, use_async=True, **kwargs)

        async for document in loader.alazy_load():
            yield document


class DirectoryLoader:

    @classmethod
    async def load(
        cls, directory_path: str, glob: str = "**/*.{md,mdx,txt}", **kwargs: Any
    ) -> AsyncGenerator[list[Document], None]:
        text_loader_kwargs = {"autodetect_encoding": True}
        loader = LangchainDirectoryLoader(
            directory_path, glob=glob, silent_errors=False, loader_kwargs=text_loader_kwargs, **kwargs
        )

        async for document in loader.alazy_load():
            yield document


class JSONJQLoader:

    @classmethod
    def load(cls, json_path: str, jq_schema: str = ".items[]", content_key: str = "text", **kwargs: Any) -> AsyncGenerator[list[Document], None]:
        loader = LangchainJSONLoader(json_path, jq_schema=jq_schema, content_key=content_key, **kwargs)

        yield from loader.lazy_load()
