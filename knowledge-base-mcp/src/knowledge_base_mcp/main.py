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
from knowledge_base_mcp.servers.ingest.filesystem import FilesystemIngestServer
from knowledge_base_mcp.servers.ingest.github import GitHubIngestServer
from knowledge_base_mcp.servers.ingest.web import WebIngestServer
from knowledge_base_mcp.servers.manage import KnowledgeBaseManagementServer
from knowledge_base_mcp.servers.search.docs import DocumentationSearchServer
from knowledge_base_mcp.servers.search.github import GitHubSearchServer
from knowledge_base_mcp.stores.vector_stores import EnhancedBaseVectorStore
from knowledge_base_mcp.utils.logging import BASE_LOGGER

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
    # code_embeddings: BaseEmbedding
    # code_reranker_model: str
    document_reranker_model: str


class CliContext(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(arbitrary_types_allowed=True)

    docs_stores: Store
    # code_stores: Store


DEFAULT_DOCS_CROSS_ENCODER_MODEL = "cross-encoder/ms-marco-MiniLM-L-2-v2"
DEFAULT_DOCS_EMBEDDINGS_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
DEFAULT_DOCS_EMBEDDINGS_BATCH_SIZE = 64

# DEFAULT_CODE_CROSS_ENCODER_MODEL = "cross-encoder/ms-marco-MiniLM-L-2-v2"
# DEFAULT_CODE_EMBEDDINGS_BATCH_SIZE = 64
# DEFAULT_CODE_EMBEDDINGS_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


@click.group()
@click.pass_context
@click.option("--document-embeddings-model", type=str, default=DEFAULT_DOCS_EMBEDDINGS_MODEL)
@click.option("--document-embeddings-batch-size", type=int, default=DEFAULT_DOCS_EMBEDDINGS_BATCH_SIZE)
@click.option("--document-reranker-model", type=str, default=DEFAULT_DOCS_CROSS_ENCODER_MODEL)
# @click.option("--code-embeddings-model", type=str, default=DEFAULT_CODE_EMBEDDINGS_MODEL)
# @click.option("--code-embeddings-batch-size", type=int, default=DEFAULT_CODE_EMBEDDINGS_BATCH_SIZE)
# @click.option("--code-reranker-model", type=str, default=DEFAULT_CODE_CROSS_ENCODER_MODEL)
def cli(
    ctx: click.Context,
    document_embeddings_model: str,
    document_embeddings_batch_size: int,
    # code_embeddings_model: str,
    # code_embeddings_batch_size: int,
    # code_reranker_model: str,
    document_reranker_model: str,
) -> None:
    logger.info(f"Loading document model {document_embeddings_model} for embeddings")
    from llama_index.embeddings.huggingface import HuggingFaceEmbedding

    ctx.obj = PartialCliContext(
        document_embeddings=HuggingFaceEmbedding(
            model_name=document_embeddings_model,
            embed_batch_size=document_embeddings_batch_size,
        ),
        # code_embeddings=HuggingFaceEmbedding(
        #     model_name=code_embeddings_model,
        #     embed_batch_size=code_embeddings_batch_size,
        # ),
        # code_reranker_model=code_reranker_model,
        document_reranker_model=document_reranker_model,
    )
    logger.info("Done loading document and code models")


@cli.group(name="elasticsearch")
@click.option("--url", type=str, envvar="ES_URL", default="http://localhost:9200")
@click.option("--index-docs-vectors", type=str, envvar="ES_INDEX_DOCS_VECTORS", default="kbmcp-docs-vectors")
@click.option("--index-docs-kv", type=str, envvar="ES_INDEX_DOCS_KV", default="kbmcp-docs-kv")
# @click.option("--index-code-vectors", type=str, envvar="ES_INDEX_CODE_VECTORS", default="kbmcp-code-vectors")
# @click.option("--index-code-kv", type=str, envvar="ES_INDEX_CODE_KV", default="kbmcp-code-kv")
@click.option("--username", type=str, envvar="ES_USERNAME", default=None)
@click.option("--password", type=str, envvar="ES_PASSWORD", default=None)
@click.option("--api-key", type=str, envvar="ES_API_KEY", default=None)
@click.pass_context
async def elasticsearch(
    ctx: click.Context,
    url: str,
    index_docs_vectors: str,
    index_docs_kv: str,
    # index_code_vectors: str,
    # index_code_kv: str,
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

    # elasticsearch_code_vector_store: EnhancedElasticsearchStore = EnhancedElasticsearchStore(
    #     es_client=es_client,
    #     index_name=index_code_vectors,
    # )

    _ = await elasticsearch_docs_vector_store._store._create_index_if_not_exists()  # pyright: ignore[reportPrivateUsage]
    # _ = await elasticsearch_code_vector_store._store._create_index_if_not_exists()  # pyright: ignore[reportPrivateUsage]

    docs_kv_store = ElasticsearchKVStore(es_client=es_client, index_name=index_docs_kv)
    # code_kv_store = ElasticsearchKVStore(es_client=es_client, index_name=index_code_kv)

    ctx.obj = CliContext(
        docs_stores=Store(
            vectors=elasticsearch_docs_vector_store,
            document=ElasticsearchDocumentStore(elasticsearch_kvstore=docs_kv_store),
            index=ElasticsearchIndexStore(elasticsearch_kvstore=docs_kv_store),
            embeddings=old_cli_ctx.document_embeddings,
            rerank_model_name=old_cli_ctx.document_reranker_model,
        ),
        # code_stores=Store(
        #     vectors=elasticsearch_code_vector_store,
        #     document=ElasticsearchDocumentStore(elasticsearch_kvstore=code_kv_store),
        #     index=ElasticsearchIndexStore(elasticsearch_kvstore=code_kv_store),
        #     embeddings=old_cli_ctx.code_embeddings,
        #     rerank_model_name=old_cli_ctx.code_reranker_model,
        # ),
    )


@cli.group(name="duckdb")
def duckdb_group() -> None:
    pass


@duckdb_group.group(name="memory")
@click.pass_context
async def duckdb_memory(ctx: click.Context) -> None:
    from knowledge_base_mcp.stores.vector_stores.duckdb import EnhancedDuckDBVectorStore
    from knowledge_base_mcp.vendored.storage.docstore.duckdb import DuckDBDocumentStore
    from knowledge_base_mcp.vendored.storage.index_store.duckdb import DuckDBIndexStore
    from knowledge_base_mcp.vendored.storage.kvstore.duckdb import DuckDBKVStore

    logger.info("Loading DuckDB document and code stores in memory")

    old_cli_ctx: PartialCliContext = ctx.obj  # pyright: ignore[reportAny]

    docs_vector_store = EnhancedDuckDBVectorStore()
    #code_vector_store = EnhancedDuckDBVectorStore()

    docs_kv_store = DuckDBKVStore(client=docs_vector_store.client)
    #code_kv_store = DuckDBKVStore(client=code_vector_store.client)

    ctx.obj = CliContext(
        docs_stores=Store(
            vectors=docs_vector_store,
            document=DuckDBDocumentStore(duckdb_kvstore=docs_kv_store),
            index=DuckDBIndexStore(duckdb_kvstore=docs_kv_store),
            embeddings=old_cli_ctx.document_embeddings,
            rerank_model_name=old_cli_ctx.document_reranker_model,
        ),
        # code_stores=Store(
        #     vectors=code_vector_store,
        #     document=DuckDBDocumentStore(duckdb_kvstore=code_kv_store),
        #     index=DuckDBIndexStore(duckdb_kvstore=code_kv_store),
        #     embeddings=old_cli_ctx.code_embeddings,
        #     rerank_model_name=old_cli_ctx.code_reranker_model,
        # ),
    )


@duckdb_group.group(name="persistent")
# @click.option("--code-db-dir", type=click.Path(path_type=Path), default="./storage")
# @click.option("--code-db-name", type=str, default="code.duckdb")
@click.option("--docs-db-dir", type=click.Path(path_type=Path), default="./storage")
@click.option("--docs-db-name", type=str, default="documents.duckdb")
@click.pass_context
async def duckdb_persistent(ctx: click.Context, docs_db_dir: Path, docs_db_name: str) -> None:
    from knowledge_base_mcp.stores.vector_stores.duckdb import EnhancedDuckDBVectorStore
    from knowledge_base_mcp.vendored.storage.docstore.duckdb import DuckDBDocumentStore
    from knowledge_base_mcp.vendored.storage.index_store.duckdb import DuckDBIndexStore
    from knowledge_base_mcp.vendored.storage.kvstore.duckdb import DuckDBKVStore

    cli_ctx: PartialCliContext = ctx.obj  # pyright: ignore[reportAny]

    logger.info(f"Loading DuckDB document in persistent mode: {docs_db_dir / docs_db_name}")

    # code_db_path: Path = code_db_dir / code_db_name
    docs_db_path: Path = docs_db_dir / docs_db_name

    # code_vector_store: EnhancedDuckDBVectorStore
    docs_vector_store: EnhancedDuckDBVectorStore

    # if not code_db_path.exists():
    #     code_vector_store = EnhancedDuckDBVectorStore(database_name=code_db_name, persist_dir=str(code_db_dir))
    # else:
    #     code_vector_store = EnhancedDuckDBVectorStore.from_local(database_path=str(code_db_path))  # pyright: ignore[reportAssignmentType, reportUnknownMemberType]

    if not docs_db_path.exists():
        docs_vector_store = EnhancedDuckDBVectorStore(database_name=docs_db_name, persist_dir=str(docs_db_dir))
    else:
        docs_vector_store = EnhancedDuckDBVectorStore.from_local(database_path=str(docs_db_path))  # pyright: ignore[reportAssignmentType, reportUnknownMemberType]

    # code_kv_store = DuckDBKVStore(client=code_vector_store.client)
    docs_kv_store = DuckDBKVStore(client=docs_vector_store.client)

    ctx.obj = CliContext(
        docs_stores=Store(
            vectors=docs_vector_store,
            document=DuckDBDocumentStore(duckdb_kvstore=docs_kv_store),
            index=DuckDBIndexStore(duckdb_kvstore=docs_kv_store),
            embeddings=cli_ctx.document_embeddings,
            rerank_model_name=cli_ctx.document_reranker_model,
        ),
        # code_stores=Store(
        #     vectors=code_vector_store,
        #     document=DuckDBDocumentStore(duckdb_kvstore=code_kv_store),
        #     index=DuckDBIndexStore(duckdb_kvstore=code_kv_store),
        #     embeddings=cli_ctx.code_embeddings,
        #     rerank_model_name=cli_ctx.code_reranker_model,
        # ),
    )


@duckdb_persistent.command()
@click.option("--transport", type=click.Choice(["stdio", "http", "sse", "streamable-http"]), default="stdio")
@click.option("--search-only", is_flag=True, default=False)
@click.pass_context
async def run(ctx: click.Context, transport: Transport, search_only: bool):
    logger.info("Building Knowledge Base MCP Server")

    cli_ctx: CliContext = ctx.obj  # pyright: ignore[reportAny]

    knowledge_base_client: KnowledgeBaseClient = KnowledgeBaseClient(vector_store_index=cli_ctx.docs_stores.vector_store_index)

    kbmcp: FastMCP[Any] = FastMCP(name="Knowledge Base MCP")

    # Documentation MCP Registration
    docs_search_server: DocumentationSearchServer = DocumentationSearchServer(
        knowledge_base_client=knowledge_base_client,
        reranker_model=cli_ctx.docs_stores.rerank_model_name,
    )

    await kbmcp.import_server(server=docs_search_server.as_fastmcp(), prefix="docs")

    # GitHub MCP Registration
    github_search_server: GitHubSearchServer = GitHubSearchServer(
        knowledge_base_client=knowledge_base_client,
        reranker_model=cli_ctx.docs_stores.rerank_model_name,
    )

    await kbmcp.import_server(server=github_search_server.as_fastmcp(), prefix="github")

    # Ingest MCP Registration
    if not search_only:
        filesystem_ingest_server: FilesystemIngestServer = FilesystemIngestServer(knowledge_base_client=knowledge_base_client)
        await kbmcp.import_server(server=filesystem_ingest_server.as_fastmcp())

        github_ingest_server: GitHubIngestServer = GitHubIngestServer(knowledge_base_client=knowledge_base_client)
        await kbmcp.import_server(server=github_ingest_server.as_fastmcp())

        web_ingest_server: WebIngestServer = WebIngestServer(knowledge_base_client=knowledge_base_client)
        await kbmcp.import_server(server=web_ingest_server.as_fastmcp())

        kb_management_server: KnowledgeBaseManagementServer = KnowledgeBaseManagementServer(knowledge_base_client=knowledge_base_client)
        await kbmcp.import_server(server=kb_management_server.as_fastmcp())

    # Run the server
    await kbmcp.run_async(transport=transport)


duckdb_memory.add_command(cmd=run)
elasticsearch.add_command(cmd=run)


def run_mcp():
    logger.info("Starting Knowledge Base MCP")
    asyncio.run(main=cli())  # pyright: ignore[reportAny]


if __name__ == "__main__":
    run_mcp()
