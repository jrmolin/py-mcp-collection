import pytest
from llama_index.core.indices.vector_store import VectorStoreIndex
from llama_index.core.storage import StorageContext
from llama_index.embeddings.fastembed import FastEmbedEmbedding
from llama_index.storage.docstore.duckdb import DuckDBDocumentStore
from llama_index.storage.kvstore.duckdb import DuckDBKVStore
from llama_index.vector_stores.duckdb import DuckDBVectorStore

from knowledge_base_mcp.clients.knowledge_base import KnowledgeBaseClient
from knowledge_base_mcp.main import DEFAULT_DOCS_CROSS_ENCODER_MODEL
from knowledge_base_mcp.stores.vector_stores.duckdb import EnhancedDuckDBVectorStore

embedding_model: FastEmbedEmbedding | None = None
try:
    embedding_model = FastEmbedEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2", embedding_cache=None)
    test = embedding_model._model.embed(["Hello, world!"])  # pyright: ignore[reportPrivateUsage]
    fastembed_available = True
except Exception:
    fastembed_available = False


@pytest.fixture
def duckdb_vector_store():
    return EnhancedDuckDBVectorStore(
        index_name="test",
        embedding_model=embedding_model,
        nodes=[],
    )


@pytest.fixture
def duckdb_docstore(duckdb_vector_store: DuckDBVectorStore):
    kv_store = DuckDBKVStore(client=duckdb_vector_store.client)
    return DuckDBDocumentStore(duckdb_kvstore=kv_store)


@pytest.fixture
def vector_store_index(duckdb_vector_store: DuckDBVectorStore, duckdb_docstore: DuckDBDocumentStore):
    storage_context = StorageContext.from_defaults(vector_store=duckdb_vector_store, docstore=duckdb_docstore)
    return VectorStoreIndex(storage_context=storage_context, embed_model=embedding_model, nodes=[])


@pytest.fixture
def knowledge_base_client(vector_store_index: VectorStoreIndex):
    return KnowledgeBaseClient(vector_store_index=vector_store_index, reranker_model=DEFAULT_DOCS_CROSS_ENCODER_MODEL)
