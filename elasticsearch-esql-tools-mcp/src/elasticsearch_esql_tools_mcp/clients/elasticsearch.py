import os

from elasticsearch import AsyncElasticsearch


def build_es_client() -> AsyncElasticsearch:
    es_host = os.getenv("ES_HOST")
    api_key = os.getenv("ES_API_KEY")

    if not es_host or not api_key:
        msg = "ES_HOST and ES_API_KEY must be set"
        raise ValueError(msg)

    return AsyncElasticsearch(es_host, api_key=api_key, http_compress=True)
