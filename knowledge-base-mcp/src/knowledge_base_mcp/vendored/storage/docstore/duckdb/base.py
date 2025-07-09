from typing import Optional, override

from llama_index.core.storage.docstore.keyval_docstore import KVDocumentStore
from llama_index.core.storage.docstore.types import DEFAULT_BATCH_SIZE
from knowledge_base_mcp.vendored.storage.kvstore.duckdb import DuckDBKVStore


class DuckDBDocumentStore(KVDocumentStore):
    """
    DuckDB Document (Node) store.

    A DuckDB store for Document and Node objects.

    Args:
        duckdb_kvstore (DuckDBKVStore): DuckDB key-value store
        namespace (str): namespace for the docstore

    """

    def __init__(
        self,
        duckdb_kvstore: DuckDBKVStore,
        namespace: Optional[str] = None,
        batch_size: int = DEFAULT_BATCH_SIZE,
    ) -> None:
        """Init a DuckDBDocumentStore."""
        super().__init__(duckdb_kvstore, namespace=namespace, batch_size=batch_size)
        # avoid conflicts with duckdb index store
        self._node_collection = f"{self._namespace}/doc"

    # TODO: UNDO https://github.com/run-llama/llama_index/pull/19362/files

    @override
    def get_all_document_hashes(self) -> dict[str, str]:
        """Get the stored hash for all documents."""
        return {
            doc_hash: doc_id
            for doc_id, doc in (self._kvstore.get_all(collection=self._metadata_collection)).items()  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
            if (doc_hash := doc.get("doc_hash"))  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
        }

    @override
    async def aget_all_document_hashes(self) -> dict[str, str]:
        """Get the stored hash for all documents."""
        return {
            doc_hash: doc_id
            for doc_id, doc in (await self._kvstore.aget_all(collection=self._metadata_collection)).items()  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
            if (doc_hash := doc.get("doc_hash"))  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
        }
