from collections.abc import AsyncGenerator
from typing import Any
import uuid

from langchain_community.document_loaders import DirectoryLoader as LangchainDirectoryLoader
from langchain_community.document_loaders import RecursiveUrlLoader as LangchainRecursiveUrlLoader
from langchain_community.document_loaders import WebBaseLoader as LangchainWebBaseLoader
from langchain_community.document_loaders.json_loader import JSONLoader as LangchainJSONLoader
from langchain_community.document_loaders.sitemap import SitemapLoader as LangchainSitemapLoader
from langchain_core.documents import Document

from doc_store_vector_search_mcp.logging.util import BASE_LOGGER

type LoaderTypes = WebPageLoader | SiteMapLoader | RecursiveWebLoader | DirectoryLoader | JSONJQLoader

logger = BASE_LOGGER.getChild("load")



class WebPageLoader:
    @classmethod
    async def load(cls, url: str, **kwargs: Any) -> AsyncGenerator[Document, None]:
        logger.info(f"Loading webpage: {url}")

        loader = LangchainWebBaseLoader(url, **kwargs)

        async for document in loader.alazy_load():
            logger.info(f"Loaded document: {document.metadata}")
            document.metadata["document_uuid"] = str(uuid.uuid4())
            yield document

        logger.info(f"Finished loading webpage: {url}")


class SiteMapLoader:
    @classmethod
    async def load(cls, url: str, filter_urls: list[str] | None = None, **kwargs: Any) -> AsyncGenerator[Document, None]:
        logger.info(f"Loading sitemap: {url}")

        loader = LangchainSitemapLoader(url, filter_urls=filter_urls, **kwargs)

        async for document in loader.alazy_load():
            logger.info(f"Loaded document: {document.metadata}")
            document.metadata["document_uuid"] = str(uuid.uuid4())
            yield document

        logger.info(f"Finished loading sitemap: {url}")


class RecursiveWebLoader:
    @classmethod
    async def load(cls, url: str, **kwargs: Any) -> AsyncGenerator[Document, None]:
        # regex which runs against links and does not match urls which end with:
        # 1. .js or .css
        # 2. .css
        # 3. .css + query string but not another slash, i.e. _static/pygments.css?v=03e43079
        logger.info(f"Recursively loading url: {url}")

        loader = LangchainRecursiveUrlLoader(url, use_async=True,check_response_status=True, **kwargs)

        async for document in loader.alazy_load():
            content_type = document.metadata.get("content_type", "")

            if content_type.startswith(("text/css", "text/javascript")):
                continue

            logger.info(f"Loaded document: {document.metadata}")
            document.metadata["document_uuid"] = str(uuid.uuid4())
            yield document

        logger.info(f"Finished recursively loading url: {url}")


class DirectoryLoader:
    @classmethod
    async def load(cls, directory_path: str, glob: list[str], **kwargs: Any) -> AsyncGenerator[Document, None]:
        logger.info(f"Loading directory: {directory_path}")

        text_loader_kwargs = {"autodetect_encoding": True}
        loader = LangchainDirectoryLoader(
            directory_path, glob=glob, silent_errors=False, loader_kwargs=text_loader_kwargs, recursive=True, **kwargs
        )

        async for document in loader.alazy_load():
            logger.info(f"Loaded document: {document.metadata}")
            yield document

        logger.info(f"Finished loading directory: {directory_path}")


class JSONJQLoader:
    @classmethod
    async def load(
        cls, json_path: str, jq_schema: str = ".items[]", content_key: str = "text", **kwargs: Any
    ) -> AsyncGenerator[Document, None]:
        logger.info(f"Loading JSON file: {json_path}")
        loader = LangchainJSONLoader(json_path, jq_schema=jq_schema, content_key=content_key, **kwargs)

        async for document in loader.alazy_load():
            logger.info(f"Loaded document: {document.metadata}")
            document.metadata["document_uuid"] = str(uuid.uuid4())
            yield document

        logger.info(f"Finished loading JSON file: {json_path}")
