from llama_index.vector_stores.elasticsearch import ElasticsearchStore
from llama_index.vector_stores.elasticsearch.base import asyncio


class EnhancedElasticsearchStore(ElasticsearchStore):
    """An enhanced Elasticsearch vector store."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        asyncio.get_event_loop().run_until_complete(self._store._create_index_if_not_exists())

    async def aclear(self) -> None:
        await super().aclear()

        await self._store._create_index_if_not_exists()

    async def metadata_agg(self, key: str) -> dict[str, int]:
        """
        Get the unique values for a metadata key in the index
        """
        query = {"size": 0, "aggs": {"metadata_keys": {"terms": {"field": f"metadata.{key}.keyword", "size": 1000}}}}
        response = await self._store.client.search(index=self.index_name, body=query)
        return {doc["key"]: doc["doc_count"] for doc in response["aggregations"]["metadata_keys"]["buckets"]}
