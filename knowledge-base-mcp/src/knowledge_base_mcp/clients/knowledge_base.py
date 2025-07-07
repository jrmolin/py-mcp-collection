from collections.abc import Sequence
from functools import cached_property
from typing import TYPE_CHECKING, Any

from llama_index.core.indices.vector_store import VectorIndexRetriever, VectorStoreIndex
from llama_index.core.ingestion.pipeline import DocstoreStrategy, IngestionPipeline
from llama_index.core.schema import BaseNode, RelatedNodeInfo
from llama_index.core.storage.docstore.keyval_docstore import KVDocumentStore
from llama_index.core.storage.kvstore.types import BaseKVStore
from llama_index.core.vector_stores.types import FilterCondition, MetadataFilter, MetadataFilters

from knowledge_base_mcp.llama_index.hierarchical_node_parsers.leaf_semantic_merging import LeafSemanticMergerNodeParser
from knowledge_base_mcp.llama_index.ingestion_pipelines.batching import PipelineGroup
from knowledge_base_mcp.llama_index.transformations.large_node_detector import LargeNodeDetector
from knowledge_base_mcp.llama_index.transformations.leaf_embeddings import LeafNodeEmbedding
from knowledge_base_mcp.llama_index.transformations.metadata import AddMetadata, ExcludeMetadata, FlattenMetadata
from knowledge_base_mcp.llama_index.transformations.write_to_docstore import WriteToDocstore
from knowledge_base_mcp.stores.vector_stores.base import EnhancedBaseVectorStore
from knowledge_base_mcp.utils.logging import BASE_LOGGER
from knowledge_base_mcp.utils.models import BaseKBArbitraryModel

if TYPE_CHECKING:
    from llama_index.core.base.base_retriever import BaseRetriever
    from llama_index.core.storage.docstore.types import BaseDocumentStore, RefDocInfo

logger = BASE_LOGGER.getChild(__name__)


def get_kb_metadata_filters(knowledge_base: list[str] | str) -> MetadataFilters:
    if isinstance(knowledge_base, str):
        knowledge_base = [knowledge_base]

    return MetadataFilters(condition=FilterCondition.OR, filters=[MetadataFilter(key="knowledge_base", value=kb) for kb in knowledge_base])


def new_kb_retriever(
    vector_store_index: VectorStoreIndex, top_k: int = 50, metadata_filters: MetadataFilters | None = None
) -> VectorIndexRetriever:
    retriever: BaseRetriever = vector_store_index.as_retriever(
        similarity_top_k=top_k,
        filters=metadata_filters,
    )

    if not isinstance(retriever, VectorIndexRetriever):
        msg = "Retriever must be a VectorIndexRetriever"
        raise TypeError(msg)

    return retriever


class KnowledgeBaseClient(BaseKBArbitraryModel):
    """A client for vector store backed knowledge bases."""

    vector_store_index: VectorStoreIndex

    @property
    def docstore(self) -> KVDocumentStore:
        doc_store: BaseDocumentStore = self.vector_store_index.docstore
        if not isinstance(doc_store, KVDocumentStore):
            msg = "Doc store must be a KVDocumentStore"
            raise TypeError(msg)

        return doc_store

    @property
    def _kv_store(self) -> BaseKVStore:
        return self.docstore._kvstore  # pyright: ignore[reportPrivateUsage]

    @property
    def vector_store(self) -> EnhancedBaseVectorStore:
        if not isinstance(self.vector_store_index.vector_store, EnhancedBaseVectorStore):
            msg = "Vector store must be an EnhancedVectorStore"
            raise TypeError(msg)

        return self.vector_store_index.vector_store

    def get_knowledge_base_retriever(self, knowledge_base: list[str] | str | None = None, top_k: int = 50) -> VectorIndexRetriever:
        """Get a retriever for the specified knowledge base, if none is provided, return a retriever for all knowledge bases."""

        if not knowledge_base:
            return new_kb_retriever(vector_store_index=self.vector_store_index, top_k=top_k)

        return new_kb_retriever(
            vector_store_index=self.vector_store_index, metadata_filters=get_kb_metadata_filters(knowledge_base), top_k=top_k
        )

    async def get_knowledge_base_nodes(self, knowledge_base: list[str] | str) -> list[BaseNode]:
        """Get all nodes from the vector store."""

        return self.vector_store.get_nodes(filters=get_kb_metadata_filters(knowledge_base))

    async def clean_knowledge_base_hash_store(self) -> None:
        """Clean any leftover hashes from the doc store metadata."""

        hash_doc_ids: dict[str, dict[str, Any]] = self._kv_store.get_all(  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType]
            collection=self.docstore._metadata_collection,  # pyright: ignore[reportPrivateUsage]
        )

        cleanup_ids: list[str] = [doc_id for doc_id in hash_doc_ids if doc_id not in self.docstore.docs]

        for cleanup_id in cleanup_ids:
            _ = await self._kv_store.adelete(
                key=cleanup_id,
                collection=self.docstore._metadata_collection,  # pyright: ignore[reportPrivateUsage]
            )

    async def delete_knowledge_base(self, knowledge_base: str) -> None:
        """Remove a knowledge base from the vector store."""

        vector_store_nodes: list[BaseNode] = await self.get_knowledge_base_nodes(knowledge_base)

        reference_documents: set[str] = {node.source_node.node_id for node in vector_store_nodes if node.source_node is not None}

        logger.info(msg=f"Deleting {len(reference_documents)} reference documents for {knowledge_base}")
        [await self.vector_store_index.docstore.adelete_ref_doc(ref_doc_id=doc_id, raise_error=False) for doc_id in reference_documents]

        # TODO: Simplify the cleanup code
        logger.info(msg=f"Deleting {len(vector_store_nodes)} nodes from docstore for {knowledge_base}")
        [await self.vector_store_index.docstore.adelete_document(doc_id=node.node_id, raise_error=False) for node in vector_store_nodes]

        logger.info(msg=f"Deleting {len(vector_store_nodes)} nodes from vector store for {knowledge_base}")
        await self.vector_store_index.adelete_nodes(node_ids=[node.node_id for node in vector_store_nodes], delete_from_docstore=False)

        # logger.info(msg=f"Cleaning hash store for {knowledge_base}")
        # await self.clean_knowledge_base_hash_store()

    async def delete_all_knowledge_bases(self) -> None:
        """Remove all knowledge bases from the vector store."""

        knowledge_bases = await self.get_knowledge_bases()

        for knowledge_base in knowledge_bases:
            await self.delete_knowledge_base(knowledge_base)

        # Clean-up the ref_docs

        # TODO: Simplify the cleanup code
        ref_docs: dict[str, RefDocInfo] = await self.vector_store_index.docstore.aget_all_ref_doc_info() or {}
        for ref_doc_id in ref_docs:
            await self.vector_store_index.docstore.adelete_ref_doc(ref_doc_id=ref_doc_id, raise_error=False)

        # Clean-up the docstore documents

        docs: dict[str, BaseNode] = self.vector_store_index.docstore.docs

        for doc_id in docs:
            self.vector_store_index.docstore.delete_document(doc_id=doc_id, raise_error=False)

    async def get_knowledge_base_stats(self) -> dict[str, int]:
        """Get statistics about the knowledge bases."""

        hashes = len(await self.vector_store_index.docstore.aget_all_document_hashes() or {})
        ref_docs = len(await self.vector_store_index.docstore.aget_all_ref_doc_info() or {})
        nodes = len(self.vector_store_index.docstore.docs)

        return {
            "hashes": hashes,
            "ref_docs": ref_docs,
            "nodes": nodes,
        }

    async def get_knowledge_bases(self) -> dict[str, int]:
        """Get all knowledge bases from the vector store."""

        return await self.vector_store.metadata_agg(key="knowledge_base")

    async def get_document(self, knowledge_base: str, title: str) -> BaseNode:
        """Get a document from the knowledge base."""

        filters = MetadataFilters(
            condition=FilterCondition.AND,
            filters=[MetadataFilter(key="knowledge_base", value=knowledge_base), MetadataFilter(key="title", value=title)],
        )

        nodes = self.vector_store.get_nodes(filters=filters)

        if len(nodes) == 0:
            msg = f"No document found in {knowledge_base} with title {title}"
            raise ValueError(msg)

        first_result: BaseNode = nodes[0]

        if first_result.source_node is None:
            msg = f"Source node not missing for document matching title {title} in {knowledge_base}"
            raise ValueError(msg)

        source_node: RelatedNodeInfo = first_result.source_node

        document: BaseNode | None = self.docstore.get_document(doc_id=source_node.node_id)

        if document is None:
            msg = f"No document found for {source_node.node_id}"
            raise ValueError(msg)

        return document

    async def new_knowledge_base(
        self,
        knowledge_base: str,
        pre_vector_store_pipelines: Sequence[IngestionPipeline] | None = None,
        pre_document_store_pipelines: Sequence[IngestionPipeline] | None = None,
    ) -> tuple[PipelineGroup, PipelineGroup]:
        """Create a new knowledge base. Returns two pipeline groups, one for storing nodes and one for storing documents."""

        await self.delete_knowledge_base(knowledge_base)

        vector_store_pipeline: PipelineGroup = PipelineGroup(
            name=f"Ingesting Vectors into Knowledge Base {knowledge_base}",
            pipelines=[
                *(pre_vector_store_pipelines or []),
                self._tag_nodes_for_kb(knowledge_base),
                self._cleanup_for_kb,
                self._embeddings_for_kb,
                self._semantic_merger_for_kb,
                self._store_in_kb,
            ],
        )

        document_store_pipeline: PipelineGroup = PipelineGroup(
            name=f"Ingesting Documents into Knowledge Base {knowledge_base}",
            pipelines=[
                *(pre_document_store_pipelines or []),
                self._tag_nodes_for_kb(knowledge_base),
                self._cleanup_for_kb,
                self._store_in_docstore,
            ],
        )

        return vector_store_pipeline, document_store_pipeline

    def _tag_nodes_for_kb(self, knowledge_base: str) -> IngestionPipeline:
        """Tag nodes for the vector store."""

        return IngestionPipeline(
            name="Tag knowledge_base",
            transformations=[
                AddMetadata(metadata={"knowledge_base": knowledge_base}),
                ExcludeMetadata(embed_keys=["knowledge_base"], llm_keys=["knowledge_base"]),
            ],
            # TODO https://github.com/run-llama/llama_index/issues/19277
            disable_cache=True,
        )

    @cached_property
    def _cleanup_for_kb(self) -> IngestionPipeline:
        """Cleanup nodes for the vector store."""

        return IngestionPipeline(
            name="Flatten metadata",
            transformations=[
                FlattenMetadata(include_related_nodes=True),
            ],
            # TODO https://github.com/run-llama/llama_index/issues/19277
            disable_cache=True,
        )

    @cached_property
    def _store_in_docstore(self) -> IngestionPipeline:
        """Write documents and nodes to the doc store."""

        write_to_docstore: WriteToDocstore = WriteToDocstore(docstore=self.docstore, embed_model=self.vector_store_index._embed_model)  # pyright: ignore[reportPrivateUsage]

        return IngestionPipeline(
            name="Push to docstore",
            transformations=[
                write_to_docstore,
            ],
        )

    @cached_property
    def _embeddings_for_kb(self) -> IngestionPipeline:
        """Embed nodes for the vector store."""
        
        return IngestionPipeline(
            name="Embeddings",
            transformations=[
                LargeNodeDetector.from_embed_model(embed_model=self.vector_store_index._embed_model, node_type="leaf"),  # pyright: ignore[reportPrivateUsage]
                LeafNodeEmbedding(embed_model=self.vector_store_index._embed_model)],  # pyright: ignore[reportPrivateUsage]
        )

    @cached_property
    def _semantic_merger_for_kb(self) -> IngestionPipeline:
        """Merge nodes for the vector store."""
        
        return IngestionPipeline(
            name="Semantic Merging",
            transformations=[LeafSemanticMergerNodeParser(embed_model=self.vector_store_index._embed_model)],  # pyright: ignore[reportPrivateUsage]
        )

    @cached_property
    def _store_in_kb(self) -> IngestionPipeline:
        """Create a new knowledge base."""

        return IngestionPipeline(
            name="Push to Vector Store",
            transformations=[],
            vector_store=self.vector_store_index.vector_store,
            docstore=self.vector_store_index.docstore,
            docstore_strategy=DocstoreStrategy.DUPLICATES_ONLY,
            # TODO https://github.com/run-llama/llama_index/issues/19277
            disable_cache=True,
        )
