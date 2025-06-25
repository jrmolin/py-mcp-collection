from llama_index.core.base.base_query_engine import BaseQueryEngine
from llama_index.core.indices.vector_store import VectorStoreIndex
from llama_index.core.llms import MockLLM
from llama_index.core.postprocessor import SentenceTransformerRerank
from llama_index.core.query_engine.retriever_query_engine import RetrieverQueryEngine
from llama_index.core.response_synthesizers.no_text import NoText
from llama_index.core.vector_stores.types import MetadataFilters

from knowledge_base_mcp.llama_index.post_processors.duplicate_node import DuplicateNodePostprocessor
from knowledge_base_mcp.llama_index.post_processors.vector_previous_next import VectorPrevNextNodePostprocessor


def summary_query_engine(
    vector_store_index: VectorStoreIndex,
    filters: MetadataFilters | None = None,
) -> BaseQueryEngine:
    """Get a query engine for a specific knowledge base"""
    synthesizer = NoText(llm=MockLLM())

    retriever = vector_store_index.as_retriever(
        similarity_top_k=1000,
        filters=filters,
    )

    return RetrieverQueryEngine(
        retriever=retriever,
        response_synthesizer=synthesizer,
    )


def retriever_query_engine(
    reranker_model: str,
    vector_store_index: VectorStoreIndex,
    result_count: int,
    filters: MetadataFilters | None = None,
) -> BaseQueryEngine:
    synthesizer = NoText(llm=MockLLM())

    retriever = vector_store_index.as_retriever(
        similarity_top_k=50,
        filters=filters,
    )

    pre_rerank_expander = VectorPrevNextNodePostprocessor(
        vector_store=vector_store_index.vector_store,
        num_nodes=5,
        mode="both",
    )

    reranker = SentenceTransformerRerank(model=reranker_model, top_n=result_count)

    duplicate_node_postprocessor = DuplicateNodePostprocessor()

    post_rerank_expander = VectorPrevNextNodePostprocessor(
        vector_store=vector_store_index.vector_store,
        num_nodes=1,
        mode="both",
    )

    return RetrieverQueryEngine(
        retriever=retriever,
        node_postprocessors=[
            pre_rerank_expander,
            duplicate_node_postprocessor,
            reranker,
            post_rerank_expander,
            duplicate_node_postprocessor,
        ],
        response_synthesizer=synthesizer,
    )
