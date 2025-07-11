from functools import cached_property
from typing import TYPE_CHECKING, Any, ClassVar

from llama_index.core.embeddings import BaseEmbedding
from llama_index.core.indices.vector_store import VectorStoreIndex
from llama_index.core.ingestion.pipeline import IngestionPipeline
from llama_index.core.postprocessor.types import BaseNodePostprocessor
from llama_index.core.schema import BaseNode, NodeWithScore, RelatedNodeInfo
from llama_index.core.storage.docstore.keyval_docstore import KVDocumentStore
from llama_index.core.storage.kvstore.types import BaseKVStore
from llama_index.core.vector_stores.types import FilterCondition, FilterOperator, MetadataFilter, MetadataFilters
from llama_index.postprocessor.flashrank_rerank import FlashRankRerank
from pydantic import BaseModel, ConfigDict

from knowledge_base_mcp.llama_index.hierarchical_node_parsers.collapse_only_children import CollapseSmallFamilies
from knowledge_base_mcp.llama_index.hierarchical_node_parsers.leaf_semantic_merging import LeafSemanticMergerNodeParser
from knowledge_base_mcp.llama_index.transformations.batch_embeddings import BatchedNodeEmbedding
from knowledge_base_mcp.llama_index.transformations.check_docstore import CheckDocstore
from knowledge_base_mcp.llama_index.transformations.large_node_detector import LargeNodeDetector
from knowledge_base_mcp.llama_index.transformations.metadata import ExcludeMetadata, FlattenMetadata
from knowledge_base_mcp.llama_index.transformations.write_to_docstore import WriteToDocstore
from knowledge_base_mcp.stores.vector_stores.base import EnhancedBaseVectorStore
from knowledge_base_mcp.utils.logging import BASE_LOGGER
from knowledge_base_mcp.utils.patches import VectorIndexRetriever

if TYPE_CHECKING:
    from llama_index.core.base.base_retriever import BaseRetriever
    from llama_index.core.storage.docstore.types import BaseDocumentStore, RefDocInfo

logger = BASE_LOGGER.getChild(__name__)


def get_kb_metadata_filter(knowledge_base: list[str] | str) -> MetadataFilter:
    if isinstance(knowledge_base, str):
        knowledge_base = [knowledge_base]

    return MetadataFilter(key="knowledge_base", value=knowledge_base, operator=FilterOperator.IN)


def get_kb_metadata_filter_by_type(knowledge_base_types: list[str] | str) -> MetadataFilter:
    if isinstance(knowledge_base_types, str):
        knowledge_base_types = [knowledge_base_types]

    return MetadataFilter(key="knowledge_base_type", value=knowledge_base_types, operator=FilterOperator.IN)


class KnowledgeBaseClient(BaseModel):
    """A client for vector store backed knowledge bases."""

    model_config: ClassVar[ConfigDict] = ConfigDict(arbitrary_types_allowed=True)

    vector_store_index: VectorStoreIndex

    reranker_model: str

    @cached_property
    def reranker(self) -> BaseNodePostprocessor:
        # return SentenceTransformerRerank(top_n=1000, device="cpu")
        return FlashRankRerank(model=self.reranker_model, top_n=1000)

    @property
    def docstore(self) -> KVDocumentStore:
        doc_store: BaseDocumentStore = self.vector_store_index.docstore
        if not isinstance(doc_store, KVDocumentStore):
            msg = "Doc store must be a KVDocumentStore"
            raise TypeError(msg)

        return doc_store

    @property
    def embed_model(self) -> BaseEmbedding:
        return self.vector_store_index._embed_model  # pyright: ignore[reportPrivateUsage]

    @property
    def _kv_store(self) -> BaseKVStore:
        return self.docstore._kvstore  # pyright: ignore[reportPrivateUsage]

    @property
    def vector_store(self) -> EnhancedBaseVectorStore:
        if not isinstance(self.vector_store_index.vector_store, EnhancedBaseVectorStore):
            msg = "Vector store must be an EnhancedVectorStore"
            raise TypeError(msg)

        return self.vector_store_index.vector_store

    async def get_knowledge_base_nodes(self, knowledge_base: list[str] | str) -> list[BaseNode]:
        """Get all nodes from the vector store."""

        return self.vector_store.get_nodes(
            filters=MetadataFilters(condition=FilterCondition.AND, filters=[get_kb_metadata_filter(knowledge_base)])
        )

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

    @property
    def duplicate_document_checker(self) -> CheckDocstore:
        """Get a hash checker for the docstore."""

        return CheckDocstore(docstore=self.docstore)

    async def get_document(self, knowledge_base_type: str, knowledge_base: str, title: str) -> BaseNode:
        """Get a document from the knowledge base."""

        filters = MetadataFilters(
            condition=FilterCondition.AND,
            filters=[
                MetadataFilter(key="knowledge_base_type", value=knowledge_base_type),
                MetadataFilter(key="knowledge_base", value=knowledge_base),
                MetadataFilter(key="title", value=title),
            ],
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

    @cached_property
    def document_to_knowledge_base_pipeline(
        self,
    ) -> IngestionPipeline:
        """Create a new knowledge base. Returns two pipeline groups, one for storing nodes and one for storing documents."""

        return IngestionPipeline(
            name="Ingesting documents into Knowledge Base",
            transformations=[
                # Clean-up
                FlattenMetadata(include_related_nodes=True),
                WriteToDocstore(docstore=self.docstore),
            ],
            vector_store=None,
            disable_cache=True,
        )

    @cached_property
    def node_to_knowledge_base_pipeline(
        self,
    ) -> IngestionPipeline:
        """Create a new knowledge base. Returns two pipeline groups, one for storing nodes and one for storing documents."""

        return IngestionPipeline(
            name="Ingesting nodes into Knowledge Base",
            transformations=[
                # Clean-up
                ExcludeMetadata(embed_keys=["knowledge_base", "knowledge_base_type"], llm_keys=["knowledge_base", "knowledge_base_type"]),
                FlattenMetadata(include_related_nodes=True),
                # Embeddings
                LargeNodeDetector.from_embed_model(embed_model=self.embed_model, node_type="leaf", extra_size=1024),
                BatchedNodeEmbedding(embed_model=self.embed_model),
                # Write to docstore
                WriteToDocstore(docstore=self.docstore),
            ],
            vector_store=self.vector_store_index.vector_store,
            disable_cache=True,
        )

    @cached_property
    def hierarchical_node_to_knowledge_base_pipeline(
        self,
    ) -> IngestionPipeline:
        """Create a new knowledge base. Returns two pipeline groups, one for storing nodes and one for storing documents."""

        knowledge_base_pipeline: IngestionPipeline = IngestionPipeline(
            name="Ingesting nodes into Knowledge Base",
            transformations=[
                # Clean-up
                ExcludeMetadata(embed_keys=["knowledge_base", "knowledge_base_type"], llm_keys=["knowledge_base", "knowledge_base_type"]),
                FlattenMetadata(include_related_nodes=True),
                # Embeddings
                LargeNodeDetector.from_embed_model(embed_model=self.embed_model, node_type="leaf", extra_size=1024),
                BatchedNodeEmbedding(embed_model=self.embed_model, leaf_node_only=True),
                LeafSemanticMergerNodeParser(embed_model=self.embed_model),
                CollapseSmallFamilies(),
                # Write to docstore
                WriteToDocstore(docstore=self.docstore),
            ],
            vector_store=self.vector_store_index.vector_store,
            # docstore=self.vector_store_index.docstore,
            # docstore_strategy=DocstoreStrategy.DUPLICATES_ONLY,
            # TODO https://github.com/run-llama/llama_index/issues/19277
            disable_cache=True,
        )

        return knowledge_base_pipeline

    async def aretrieve(
        self,
        query: str,
        knowledge_base: list[str] | str | None = None,
        knowledge_base_types: list[str] | str | None = None,
        extra_filters: MetadataFilters | None = None,
        top_k: int = 200,  # A high number is needed to produce the summary and then should be reduced by the server
    ) -> list[NodeWithScore]:
        """Get a retriever for the specified knowledge base, if none is provided, return a retriever for all knowledge bases."""

        retriever: BaseRetriever = self.get_knowledge_base_retriever(
            knowledge_base_types=knowledge_base_types,
            knowledge_base=knowledge_base,
            extra_filters=extra_filters,
            top_k=top_k,
        )

        return await retriever.aretrieve(query)

    def get_knowledge_base_retriever(
        self,
        knowledge_base_types: list[str] | str | None,
        knowledge_base: list[str] | str | None = None,
        extra_filters: MetadataFilters | None = None,
        top_k: int = 50,
    ) -> VectorIndexRetriever:
        """Get a retriever for the specified knowledge base, if none is provided, return a retriever for all knowledge bases."""

        metadata_filters: MetadataFilters = MetadataFilters(condition=FilterCondition.AND, filters=[])

        if knowledge_base:
            metadata_filters.filters.append(get_kb_metadata_filter(knowledge_base))

        if knowledge_base_types:
            metadata_filters.filters.append(get_kb_metadata_filter_by_type(knowledge_base_types))

        if extra_filters:
            metadata_filters.filters.extend(extra_filters.filters)

        retriever: BaseRetriever = self.vector_store_index.as_retriever(
            similarity_top_k=top_k,
            filters=metadata_filters if metadata_filters.filters else None,
        )

        if not isinstance(retriever, VectorIndexRetriever):
            msg = "Retriever must be a VectorIndexRetriever"
            raise TypeError(msg)

        return retriever
