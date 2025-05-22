from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from typing import Any

from langchain_community.document_loaders import DirectoryLoader as LangchainDirectoryLoader
from langchain_community.document_loaders import RecursiveUrlLoader as LangchainRecursiveUrlLoader
from langchain_community.document_loaders import WebBaseLoader as LangchainWebBaseLoader
from langchain_community.document_loaders.json_loader import JSONLoader as LangchainJSONLoader
from langchain_community.document_loaders.sitemap import SitemapLoader as LangchainSitemapLoader
from langchain_core.documents import Document


class Loader(ABC):
    @classmethod
    @abstractmethod
    async def load(cls, to_load: Any) -> AsyncGenerator[list[Document], None]:
        pass


class WebPageLoader(Loader):
    @classmethod
    async def load(cls, to_load: Any, **kwargs: Any) -> AsyncGenerator[list[Document], None]:
        return await cls.load_webpage(to_load, **kwargs)

    @classmethod
    async def load_webpage(cls, url: str, **kwargs: Any) -> AsyncGenerator[list[Document], None]:
        loader = LangchainWebBaseLoader(url, use_async=True, **kwargs)

        async for document in loader.alazy_load():
            yield document


class SiteMapLoader(Loader):
    @classmethod
    async def load(cls, to_load: Any, **kwargs: Any) -> AsyncGenerator[list[Document], None]:
        return await cls.load_sitemap(to_load, **kwargs)

    @classmethod
    async def load_sitemap(cls, url: str, filter_urls: list[str] | None = None, **kwargs: Any) -> AsyncGenerator[list[Document], None]:
        loader = LangchainSitemapLoader(url, use_async=True, filter_urls=filter_urls, **kwargs)

        async for document in loader.alazy_load():
            yield document


class RecursiveWebLoader(Loader):
    @classmethod
    async def load(cls, to_load: Any, **kwargs: Any) -> AsyncGenerator[list[Document], None]:
        return await cls.load_recursive_web(to_load, **kwargs)

    @classmethod
    async def load_recursive_web(cls, url: str, **kwargs: Any) -> AsyncGenerator[list[Document], None]:
        loader = LangchainRecursiveUrlLoader(url, use_async=True, **kwargs)

        async for document in loader.alazy_load():
            yield document


class DirectoryLoader(Loader):
    @classmethod
    async def load(cls, to_load: Any, **kwargs: Any) -> AsyncGenerator[list[Document], None]:
        return await cls.load_directory(to_load, **kwargs)

    @classmethod
    async def load_directory(
        cls, directory_path: str, glob_pattern: str = "**/*.{md,mdx,txt}", **kwargs: Any
    ) -> AsyncGenerator[list[Document], None]:
        text_loader_kwargs = {"autodetect_encoding": True}
        loader = LangchainDirectoryLoader(
            directory_path, use_async=True, glob_pattern=glob_pattern, silent_errors=True, text_loader_kwargs=text_loader_kwargs, **kwargs
        )

        async for document in loader.alazy_load():
            yield document


class JSONJQLoader(Loader):
    @classmethod
    async def load(cls, to_load: Any, **kwargs: Any) -> AsyncGenerator[list[Document], None]:
        async for document in await cls.load_json(to_load, **kwargs):
            yield document

    @classmethod
    async def load_json(cls, json_path: str, jq_schema: str = ".items[]", content_key: str = "text", **kwargs: Any) -> AsyncGenerator[list[Document], None]:
        loader = LangchainJSONLoader(json_path, jq_schema=jq_schema, content_key=content_key, **kwargs)

        for document in loader.lazy_load():
            yield document
