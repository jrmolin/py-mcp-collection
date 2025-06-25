from llama_index.core.embeddings import BaseEmbedding
from llama_index.core.ingestion import IngestionPipeline


def embeddings_pipeline_factory(embedding_model: BaseEmbedding) -> IngestionPipeline:
    """An Ingest Pipeline that calculates embeddings for the documents."""

    return IngestionPipeline(name="Calculate Embeddings", transformations=[embedding_model], disable_cache=True)
