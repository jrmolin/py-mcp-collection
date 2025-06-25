from llama_index.core.indices.vector_store import VectorStoreIndex
from llama_index.core.ingestion import IngestionPipeline


def vector_store_pipeline_factory(vector_store_index: VectorStoreIndex) -> IngestionPipeline:
    """An Ingest Pipeline that stores the documents in a vector store."""

    return IngestionPipeline(name="Push to Vector Store", transformations=[], vector_store=vector_store_index.vector_store)
