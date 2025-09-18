import os

from elasticsearch import AsyncElasticsearch


def get_elasticsearch_client() -> AsyncElasticsearch | None:
    if not (host := os.getenv("ES_URL")):
        return None

    if not (api_key := os.getenv("ES_API_KEY")):
        return None

    return AsyncElasticsearch(
        hosts=[host],
        api_key=api_key,
        http_compress=True,
        retry_on_timeout=True,
    )
