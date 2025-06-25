import asyncio
from functools import cached_property
from pathlib import Path

import asyncclick as click
import torch
from fastmcp import FastMCP
from fastmcp.tools import Tool
from llama_index.core import VectorStoreIndex
from llama_index.core.ingestion import IngestionPipeline
from llama_index.embeddings.fastembed import FastEmbedEmbedding
from pydantic import BaseModel, ConfigDict

from knowledge_base_mcp.servers.documentation import DocumentationServer
from knowledge_base_mcp.utils.logging import BASE_LOGGER
from knowledge_base_mcp.vector_stores.duckdb import EnhancedDuckDBVectorStore
from knowledge_base_mcp.vector_stores.elasticsearch import EnhancedElasticsearchStore
from knowledge_base_mcp.vendored.huggingface import HuggingFaceEmbedding

logger = BASE_LOGGER.getChild(__name__)


class CliContext(BaseModel):
    vector_store: EnhancedDuckDBVectorStore | EnhancedElasticsearchStore | None = None

    embed_model: FastEmbedEmbedding | HuggingFaceEmbedding | None = None

    reranker_model: str | None = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @cached_property
    def embeddings_pipeline(self) -> IngestionPipeline:
        if not self.embed_model:
            msg = "Embed model and embedding ingestion pipeline must be set"
            raise ValueError(msg)

        return IngestionPipeline(name="Calculate Embeddings", transformations=[self.embed_model], disable_cache=True)

    @cached_property
    def vector_store_index(self) -> VectorStoreIndex:
        if not self.vector_store or not self.embed_model:
            msg = "Vector store and embed model must be set"
            raise ValueError(msg)

        return VectorStoreIndex.from_vector_store(self.vector_store, embed_model=self.embed_model)

    @cached_property
    def vector_store_pipeline(self) -> IngestionPipeline:
        if not self.vector_store:
            msg = "Vector store must be set"
            raise ValueError(msg)

        return IngestionPipeline(name="Vector Store Ingestion", transformations=[], vector_store=self.vector_store)


DEFAULT_EMBEDDINGS_BATCH_SIZE = 48
DEFAULT_CROSS_ENCODER_MODEL = "cross-encoder/ms-marco-MiniLM-L-2-v2"
DEFAULT_EMBEDDINGS_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def _pick_device() -> str:
    """Return 'cuda', 'mps', or 'cpu' depending on what's available."""
    if torch.cuda.is_available():
        return "cuda"
    if torch.backends.mps.is_available():
        return "mps"
    return "cpu"


@click.group()
@click.pass_context
@click.option("--embed-model", type=str, default=DEFAULT_EMBEDDINGS_MODEL)
@click.option("--embed-batch-size", type=int, default=DEFAULT_EMBEDDINGS_BATCH_SIZE)
@click.option("--reranker-model", type=str, default=DEFAULT_CROSS_ENCODER_MODEL)
def cli(ctx: click.Context, embed_model: str, embed_batch_size: int, reranker_model: str) -> None:
    new_embed_model: HuggingFaceEmbedding = HuggingFaceEmbedding(
        model_name=embed_model,
        device=_pick_device(),
        embed_batch_size=embed_batch_size,
    )

    # new_embed_model: FastEmbedEmbedding = FastEmbedEmbedding(model_name=embed_model, threads=2, embed_batch_size=embed_batch_size)
    new_reranker_model: str = reranker_model

    ctx.obj = CliContext(
        embed_model=new_embed_model,
        reranker_model=new_reranker_model,
    )


@cli.group(name="elasticsearch")
@click.option("--es-url", type=str, envvar="ES_URL", default="http://localhost:9200")
@click.option("--es-index-name", type=str, envvar="ES_INDEX_NAME", default="kbmcp")
@click.option("--es-username", type=str, envvar="ES_USERNAME", default=None)
@click.option("--es-password", type=str, envvar="ES_PASSWORD", default=None)
@click.option("--es-api-key", type=str, envvar="ES_API_KEY", default=None)
@click.pass_context
async def elasticsearch(
    ctx: click.Context, es_url: str, es_index_name: str, es_username: str | None, es_password: str | None, es_api_key: str | None
) -> None:
    elasticsearch_store = EnhancedElasticsearchStore(
        es_url=es_url,
        index_name=es_index_name,
        es_username=es_username,
        es_password=es_password,
        es_api_key=es_api_key,
    )

    await elasticsearch_store._store._create_index_if_not_exists()

    ctx.obj.vector_store = elasticsearch_store


@cli.group(name="duckdb")
def duckdb_group() -> None:
    pass


@duckdb_group.group(name="memory")
@click.pass_context
async def duckdb_memory(ctx: click.Context) -> None:
    ctx.obj.vector_store = EnhancedDuckDBVectorStore()


@duckdb_group.group(name="persistent")
@click.option("--db-dir", type=click.Path(exists=True, path_type=Path), default="./storage")
@click.option("--db-name", type=str, default="knowledge_base.duckdb")
@click.pass_context
async def duckdb_persistent(ctx: click.Context, db_dir: Path, db_name: str) -> None:
    existing_db = (db_dir / db_name).exists()

    if not existing_db:
        logger.info(f"Creating new DuckDB vector store at {db_dir / db_name}")
        ctx.obj.vector_store = EnhancedDuckDBVectorStore(database_name=db_name, persist_dir=str(db_dir))
        return

    logger.info(f"Loading existing DuckDB vector store at {db_dir / db_name}")

    ctx.obj.vector_store = EnhancedDuckDBVectorStore.from_local(database_path=str(db_dir / db_name))


@duckdb_persistent.command()
@click.pass_context
async def run(ctx: click.Context):
    logger.info("Starting Knowledge Base MCP")

    vector_store_index: VectorStoreIndex = ctx.obj.vector_store_index

    logger.info("Vector store loaded")

    mcp = FastMCP(name="Local Knowledge Base MCP")

    documentation_server: DocumentationServer = DocumentationServer(
        embeddings_pipeline=ctx.obj.embeddings_pipeline,
        vector_store_pipeline=ctx.obj.vector_store_pipeline,
        vector_store_index=vector_store_index,
        reranker_model=ctx.obj.reranker_model,
    )

    mcp.add_tool(Tool.from_function(documentation_server.load_website))
    mcp.add_tool(Tool.from_function(documentation_server.query))
    mcp.add_tool(Tool.from_function(documentation_server.query_knowledge_bases))
    mcp.add_tool(Tool.from_function(documentation_server.get_knowledge_bases))
    mcp.add_tool(Tool.from_function(documentation_server.remove_knowledge_base))
    mcp.add_tool(Tool.from_function(documentation_server.remove_all_knowledge_bases))

    await mcp.run_async(transport="sse")


duckdb_memory.add_command(run)
elasticsearch.add_command(run)


def run_mcp():
    asyncio.run(cli())


if __name__ == "__main__":
    run_mcp()
