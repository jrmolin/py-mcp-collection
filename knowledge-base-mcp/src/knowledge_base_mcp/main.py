import asyncio
from functools import cached_property
from logging import Logger
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar

import asyncclick as click
from fastmcp import FastMCP
from fastmcp.server.server import Transport
from llama_index.core.base.embeddings.base import BaseEmbedding
from llama_index.core.bridge.pydantic import BaseModel, ConfigDict
from llama_index.core.indices.loading import load_indices_from_storage  # pyright: ignore[reportUnknownVariableType]
from llama_index.core.indices.vector_store import VectorStoreIndex
from llama_index.core.storage.docstore.types import BaseDocumentStore
from llama_index.core.storage.index_store.types import BaseIndexStore
from llama_index.core.storage.storage_context import StorageContext

from knowledge_base_mcp.clients.knowledge_base import KnowledgeBaseClient
from knowledge_base_mcp.servers.github import GitHubServer
from knowledge_base_mcp.servers.ingest.filesystem import FilesystemIngestServer
from knowledge_base_mcp.servers.ingest.web import WebIngestServer
from knowledge_base_mcp.servers.manage import KnowledgeBaseManagementServer
from knowledge_base_mcp.servers.search.docs import DocumentationSearchServer
from knowledge_base_mcp.stores.vector_stores import EnhancedBaseVectorStore
from knowledge_base_mcp.utils.logging import BASE_LOGGER
from knowledge_base_mcp.utils.patches import apply_patches

apply_patches()

if TYPE_CHECKING:
    from elasticsearch import AsyncElasticsearch
    from llama_index.core.data_structs.data_structs import IndexStruct
    from llama_index.core.indices.base import BaseIndex

logger: Logger = BASE_LOGGER.getChild(suffix=__name__)


class Store(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(arbitrary_types_allowed=True)

    vectors: EnhancedBaseVectorStore
    document: BaseDocumentStore
    index: BaseIndexStore
    embeddings: BaseEmbedding
    rerank_model_name: str

    @cached_property
    def storage_context(self) -> StorageContext:
        return StorageContext.from_defaults(
            docstore=self.document,
            vector_store=self.vectors,  # pyright: ignore[reportArgumentType]
            index_store=self.index,
        )

    @cached_property
    def vector_store_index(self) -> VectorStoreIndex:
        persisted_indices: list[BaseIndex[IndexStruct]] = load_indices_from_storage(  # pyright: ignore[reportUnknownVariableType]
            storage_context=self.storage_context, embed_model=self.embeddings
        )
        persisted_vector_store_indices: list[VectorStoreIndex] = [
            index for index in persisted_indices if isinstance(index, VectorStoreIndex)
        ]

        if stored_vector_store_index := next(iter(persisted_vector_store_indices), None):
            return stored_vector_store_index

        vector_store_index: VectorStoreIndex = VectorStoreIndex(
            nodes=[],
            storage_context=self.storage_context,
            vector_store=self.vectors,
            embed_model=self.embeddings,
        )

        return vector_store_index


class PartialCliContext(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(arbitrary_types_allowed=True)

    document_embeddings: BaseEmbedding
    document_reranker_model: str


class CliContext(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(arbitrary_types_allowed=True)

    docs_stores: Store


DEFAULT_DOCS_CROSS_ENCODER_MODEL = "ms-marco-TinyBERT-L-2-v2"
DEFAULT_DOCS_EMBEDDINGS_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
DEFAULT_DOCS_EMBEDDINGS_BATCH_SIZE = 64


@click.group()
@click.pass_context
@click.option("--document-embeddings-model", type=str, default=DEFAULT_DOCS_EMBEDDINGS_MODEL)
@click.option("--document-embeddings-batch-size", type=int, default=DEFAULT_DOCS_EMBEDDINGS_BATCH_SIZE)
@click.option("--document-reranker-model", type=str, default=DEFAULT_DOCS_CROSS_ENCODER_MODEL)
def cli(
    ctx: click.Context,
    document_embeddings_model: str,
    document_embeddings_batch_size: int,
    document_reranker_model: str,
) -> None:
    logger.info(f"Loading document model {document_embeddings_model} for embeddings")
    from llama_index.embeddings.huggingface import HuggingFaceEmbedding

    ctx.obj = PartialCliContext(
        document_embeddings=HuggingFaceEmbedding(
            model_name=document_embeddings_model,
            embed_batch_size=document_embeddings_batch_size,
        ),
        document_reranker_model=document_reranker_model,
    )
    logger.info("Done loading document and code models")


@cli.group(name="elasticsearch")
@click.option("--url", type=str, envvar="ES_URL", default="http://localhost:9200", show_envvar=True)
@click.option("--index-docs-vectors", type=str, envvar="ES_INDEX_DOCS_VECTORS", default="kbmcp-docs-vectors", show_envvar=True)
@click.option("--index-docs-kv", type=str, envvar="ES_INDEX_DOCS_KV", default="kbmcp-docs-kv", show_envvar=True)
@click.option("--username", type=str, envvar="ES_USERNAME", default=None, show_envvar=True)
@click.option("--password", type=str, envvar="ES_PASSWORD", default=None, show_envvar=True)
@click.option("--api-key", type=str, envvar="ES_API_KEY", default=None, show_envvar=True)
@click.pass_context
async def elasticsearch(
    ctx: click.Context,
    url: str,
    index_docs_vectors: str,
    index_docs_kv: str,
    username: str | None,
    password: str | None,
    api_key: str | None,
) -> None:
    old_cli_ctx: PartialCliContext = ctx.obj  # pyright: ignore[reportAny]
    from llama_index.storage.docstore.elasticsearch import ElasticsearchDocumentStore
    from llama_index.storage.index_store.elasticsearch import ElasticsearchIndexStore
    from llama_index.storage.kvstore.elasticsearch import ElasticsearchKVStore

    from knowledge_base_mcp.stores.vector_stores.elasticsearch import EnhancedElasticsearchStore

    logger.info(f"Loading Elasticsearch document and code stores: {url}")

    elasticsearch_docs_vector_store: EnhancedElasticsearchStore = EnhancedElasticsearchStore(
        es_url=url,
        index_name=index_docs_vectors,
        es_username=username,
        es_password=password,
        es_api_key=api_key,
    )

    es_client: AsyncElasticsearch = elasticsearch_docs_vector_store.client  # pyright: ignore[reportAny]

    _ = await elasticsearch_docs_vector_store._store._create_index_if_not_exists()  # pyright: ignore[reportPrivateUsage]

    docs_kv_store = ElasticsearchKVStore(es_client=es_client, index_name=index_docs_kv)

    ctx.obj = CliContext(
        docs_stores=Store(
            vectors=elasticsearch_docs_vector_store,
            document=ElasticsearchDocumentStore(elasticsearch_kvstore=docs_kv_store),
            index=ElasticsearchIndexStore(elasticsearch_kvstore=docs_kv_store),
            embeddings=old_cli_ctx.document_embeddings,
            rerank_model_name=old_cli_ctx.document_reranker_model,
        ),
    )


@cli.group(name="duckdb")
def duckdb_group() -> None:
    pass


@duckdb_group.group(name="memory")
@click.option("--db-in-memory", envvar="DUCKDB_MEMORY_DB_IN_MEMORY", type=bool, default=True)
@click.pass_context
async def duckdb_memory(ctx: click.Context, db_in_memory: bool) -> None:  # noqa: ARG001  # pyright: ignore[reportUnusedParameter]
    from llama_index.storage.docstore.duckdb import DuckDBDocumentStore
    from llama_index.storage.index_store.duckdb import DuckDBIndexStore
    from llama_index.storage.kvstore.duckdb import DuckDBKVStore

    from knowledge_base_mcp.stores.vector_stores.duckdb import EnhancedDuckDBVectorStore

    logger.info("Loading DuckDB document and code stores in memory")

    old_cli_ctx: PartialCliContext = ctx.obj  # pyright: ignore[reportAny]

    docs_vector_store = EnhancedDuckDBVectorStore()

    docs_kv_store = DuckDBKVStore(client=docs_vector_store.client)

    ctx.obj = CliContext(
        docs_stores=Store(
            vectors=docs_vector_store,
            document=DuckDBDocumentStore(duckdb_kvstore=docs_kv_store),
            index=DuckDBIndexStore(duckdb_kvstore=docs_kv_store),
            embeddings=old_cli_ctx.document_embeddings,
            rerank_model_name=old_cli_ctx.document_reranker_model,
        ),
    )


@duckdb_group.group(name="persistent")
@click.option("--db-dir", envvar="DUCKDB_PERSISTENT_DB_DIR", type=click.Path(path_type=Path), default="./storage")
@click.option("--db-name-docs", envvar="DUCKDB_PERSISTENT_DB_NAME_DOCS", type=str, default="documents.duckdb")
@click.option("--db-name-vectors", envvar="DUCKDB_PERSISTENT_DB_NAME_VECTORS", type=str, default="vectors.duckdb")
@click.pass_context
async def duckdb_persistent(ctx: click.Context, db_dir: Path, db_name_docs: str, db_name_vectors: str) -> None:
    from llama_index.storage.docstore.duckdb import DuckDBDocumentStore
    from llama_index.storage.index_store.duckdb import DuckDBIndexStore
    from llama_index.storage.kvstore.duckdb import DuckDBKVStore

    from knowledge_base_mcp.stores.vector_stores.duckdb import EnhancedDuckDBVectorStore

    cli_ctx: PartialCliContext = ctx.obj  # pyright: ignore[reportAny]

    logger.info(f"Loading DuckDB document in persistent mode: {db_dir / db_name_docs}")

    if not db_dir.exists():
        db_dir.mkdir(parents=True, exist_ok=True)

    docs_kv_store = DuckDBKVStore(database_name=db_name_docs, persist_dir=str(db_dir))

    ctx.obj = CliContext(
        docs_stores=Store(
            vectors=EnhancedDuckDBVectorStore(database_name=db_name_vectors, persist_dir=str(db_dir)),
            document=DuckDBDocumentStore(duckdb_kvstore=docs_kv_store),
            index=DuckDBIndexStore(duckdb_kvstore=docs_kv_store),
            embeddings=cli_ctx.document_embeddings,
            rerank_model_name=cli_ctx.document_reranker_model,
        ),
    )


@duckdb_persistent.command()
@click.option("--transport", type=click.Choice(["stdio", "http", "sse", "streamable-http"]), default="stdio")
@click.option("--search-only", is_flag=True, default=False)
@click.pass_context
async def run(ctx: click.Context, transport: Transport, search_only: bool):
    logger.info("Building Knowledge Base MCP Server")

    cli_ctx: CliContext = ctx.obj  # pyright: ignore[reportAny]

    knowledge_base_client: KnowledgeBaseClient = KnowledgeBaseClient(
        vector_store_index=cli_ctx.docs_stores.vector_store_index,
        reranker_model=cli_ctx.docs_stores.rerank_model_name,
    )

    kbmcp: FastMCP[Any] = FastMCP(name="Knowledge Base MCP")

    # Documentation MCP Registration
    docs_search_server: DocumentationSearchServer = DocumentationSearchServer(
        knowledge_base_client=knowledge_base_client,
        reranker_model=cli_ctx.docs_stores.rerank_model_name,
    )
    _ = await kbmcp.import_server(server=docs_search_server.as_search_server(), prefix="docs")

    # GitHub MCP Registration
    github_server: GitHubServer = GitHubServer(knowledge_base_client=knowledge_base_client)
    _ = await kbmcp.import_server(server=github_server.as_search_server(), prefix="github")

    if not search_only:
        _ = await kbmcp.import_server(server=github_server.as_ingest_server())

        # Filesystem Ingest MCP Registration
        filesystem_ingest_server: FilesystemIngestServer = FilesystemIngestServer(knowledge_base_client=knowledge_base_client)
        _ = await kbmcp.import_server(server=filesystem_ingest_server.as_ingest_server())

        # Management MCP Registration
        kb_management_server: KnowledgeBaseManagementServer = KnowledgeBaseManagementServer(knowledge_base_client=knowledge_base_client)
        _ = await kbmcp.import_server(server=kb_management_server.as_management_server())

        web_ingest_server: WebIngestServer = WebIngestServer(knowledge_base_client=knowledge_base_client)
        _ = await kbmcp.import_server(server=web_ingest_server.as_ingest_server())

    # Run the server
    await kbmcp.run_async(transport=transport)


duckdb_memory.add_command(cmd=run)
elasticsearch.add_command(cmd=run)


def run_mcp():
    logger.info("Starting Knowledge Base MCP")
    asyncio.run(main=cli(auto_envvar_prefix=None))  # pyright: ignore[reportAny]


if __name__ == "__main__":
    run_mcp()
