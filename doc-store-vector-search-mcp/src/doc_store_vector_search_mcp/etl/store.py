import json
from typing import Any, TypeVar

import duckdb
from flashrank import Ranker, RerankRequest
from langchain.retrievers.contextual_compression import ContextualCompressionRetriever
from langchain.retrievers.document_compressors.base import DocumentCompressorPipeline
from langchain.retrievers.document_compressors.embeddings_filter import EmbeddingsFilter
from langchain_community.document_transformers import EmbeddingsRedundantFilter
from langchain_community.vectorstores import DuckDB, ElasticsearchStore
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

from doc_store_vector_search_mcp.logging.util import BASE_LOGGER

from .splitters.semantic import SemanticChunker

logger = BASE_LOGGER.getChild("store")

type VectorStoreTypes = DuckDB | ElasticsearchStore


class ElasticsearchStoreSettings(BaseModel):
    es_url: str
    es_index: str

    def connect(self) -> None:
        pass


class DuckDBSettings(BaseModel):
    db_path: str

    def connect(self) -> duckdb.DuckDBPyConnection:
        return duckdb.connect(database=self.db_path, config={"enable_external_access": "false"})


type VectorStoreSettings = ElasticsearchStoreSettings | DuckDBSettings

T = TypeVar("T", bound=VectorStoreTypes)
S = TypeVar("S", bound=VectorStoreSettings)


class TextEmbedding(Embeddings):
    def __init__(self, model: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model)

    def embed(self, text: str) -> list[float]:
        return self.model.encode([text])[0].tolist()

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self.model.encode(texts).tolist()

    def embed_query(self, text: str) -> list[float]:
        return self.model.encode([text])[0].tolist()


class CodeEmbedding(Embeddings):
    def __init__(self, model: str = "flax-sentence-embeddings/st-codesearch-distilroberta-base"):
        self.model = SentenceTransformer(model)

    def embed(self, text: str) -> list[float]:
        return self.model.encode([text])[0].tolist()

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self.model.encode(texts).tolist()

    def embed_query(self, text: str) -> list[float]:
        return self.model.encode([text])[0].tolist()


class SearchResult(BaseModel):
    before_context: str | None = None
    highlight: str
    after_context: str | None = None
    source: str
    title: str
    kb_id: str
    score: float


# class CodeEmbedding(Embeddings):
#     def __init__(self):
#         self.device = "cpu"

#         self.tokenizer = AutoTokenizer.from_pretrained("Salesforce/codet5p-110m-embedding", trust_remote_code=True)
#         self.model = AutoModel.from_pretrained("Salesforce/codet5p-110m-embedding", trust_remote_code=True).to(self.device)

#         self.torch = torch

#     def embed(self, text: str) -> list[float]:
#         inputs = self.tokenizer.encode(text, return_tensors="pt").to(self.device)
#         with self.torch.no_grad():
#             embedding = self.model(inputs)[0]
#         return embedding.cpu().numpy().tolist()

#     def embed_documents(self, texts: list[str]) -> list[list[float]]:
#         return [self.embed(text) for text in texts]

#     def embed_query(self, text: str) -> list[float]:
#         return self.embed(text)


class VectorStoreManager[T: VectorStoreTypes, S: VectorStoreSettings]:
    def __init__(self, project_name: str, kb_id: str, code_settings: S, document_settings: S, vector_store_class: type[T]):
        self.project_name = project_name
        self.kb_id = kb_id

        self.document_embedding = TextEmbedding()
        self.document_vector_store: T = vector_store_class(embedding=self.document_embedding, connection=document_settings.connect())  # type: ignore
        document_redundant_filter = EmbeddingsRedundantFilter(embeddings=self.document_embedding)
        document_relevant_filter = EmbeddingsFilter(embeddings=self.document_embedding, similarity_threshold=0.10)
        document_pipeline_compressor = DocumentCompressorPipeline(transformers=[document_redundant_filter, document_relevant_filter])

        self.document_retriever = ContextualCompressionRetriever(
            base_compressor=document_pipeline_compressor,
            base_retriever=self.document_vector_store.as_retriever(),
        )
        self.document_semantic_splitter = SemanticChunker(embeddings=self.document_embedding, breakpoint_threshold_type="gradient")

        self.code_embedding = CodeEmbedding()
        self.code_vector_store: T = vector_store_class(embedding=self.code_embedding, connection=code_settings.connect())  # type: ignore
        code_redundant_filter = EmbeddingsRedundantFilter(embeddings=self.code_embedding)
        code_relevant_filter = EmbeddingsFilter(embeddings=self.code_embedding, similarity_threshold=0.10)
        code_pipeline_compressor = DocumentCompressorPipeline(transformers=[code_redundant_filter, code_relevant_filter])

        self.code_retriever = ContextualCompressionRetriever(
            base_compressor=code_pipeline_compressor,
            base_retriever=self.code_vector_store.as_retriever(),
        )

        self.reranker = Ranker(max_length=1200)

    def _trim_overlap(self, first: str, second: str) -> str:
        """
        Trim the overlap between the end of one string and the beginning of the next string.
        """
        # Find the longest common substring between the end of the first string and the beginning of the second string
        longest_common_substring = ""
        for i in range(min(len(first), len(second))):
            if first[i] == second[i]:
                longest_common_substring += first[i]
            else:
                break

        return first[len(longest_common_substring) :] + second

    async def remove_adjacent_results(self, documents: list[Document]) -> list[Document]:
        """
        If a higher ranked result will cover the same content (-1, 0, +1 order), as a lower ranked result, remove the lower ranked result.
        """

        documents_by_uuid = {document.metadata["document_uuid"]: document for document in documents}

        new_documents = []
        new_document_uuids = []

        for document in documents:
            # first time we've seen this document
            if document.metadata["document_uuid"] not in new_document_uuids:
                new_document_uuids.append(document.metadata["document_uuid"])
                new_documents.append(document)
                continue

            # we've seen this document before
            previous_documents = [
                document for document in new_documents if document.metadata["document_uuid"] == document.metadata["document_uuid"]
            ]

            previous_document_orders = [document.metadata["order"] for document in previous_documents]
            previous_document_orders.extend([order - 1 for order in previous_document_orders])
            previous_document_orders.extend([order + 1 for order in previous_document_orders])

            previous_document_orders = list(set(previous_document_orders))

            if document.metadata["order"] in previous_document_orders:
                continue

            new_documents.append(document)

        return new_documents

    def rerank_results(self, query: str, documents: list[Document]) -> list[Document]:
        """
        Rerank the results based on the order of the documents.
        """

        passages = [
            {
                "id": document.metadata["document_uuid"] + "_" + str(document.metadata["order"]),
                "text": document.page_content,
                "original_document": document,
            }
            for document in documents
        ]

        rerank_request = RerankRequest(
            query=query,
            passages=passages,
        )
        rerank_response = self.reranker.rerank(rerank_request)

        # reorder our original documents array based on the rerank response
        return [passage["original_document"] for passage in rerank_response]

    async def get_adjacent_chunk_bodies(self, document: Document) -> tuple[str | None, str | None]:
        """
        Get the adjacent chunks of a document.
        """
        # Get the document ID from the document metadata
        document_uuid = document.metadata["document_uuid"]

        related_documents = self.document_vector_store._table.query(  # type: ignore
            virtual_table_name="related_documents",
            sql_query=f"""
        SELECT *
        FROM related_documents
        WHERE CAST(metadata AS JSON)->>'$.document_uuid' = '{document_uuid}'
        """,
        ).fetchall()

        chunk_order = document.metadata["order"]

        previous_chunk = None
        next_chunk = None

        for _, _, _, metadata in related_documents:
            metadata_dict = json.loads(metadata)

            if metadata_dict["order"] == chunk_order - 1:
                previous_chunk = metadata_dict["chunk_body"]
            elif metadata_dict["order"] == chunk_order + 1:
                next_chunk = metadata_dict["chunk_body"]

        return previous_chunk, next_chunk

    async def add_code_documents(self, documents: list[Document], metadata: dict[str, Any]):
        logger.info(f"Adding {len(documents)} code documents to vector store")
        [document.metadata.update(metadata or {}) for document in documents]

        await self.code_vector_store.aadd_documents(documents)

    async def add_documents(self, documents: list[Document], metadata: dict[str, Any]):
        logger.info(f"Adding {len(documents)} text documents to vector store")
        [document.metadata.update(metadata or {}) for document in documents]
        await self.document_vector_store.aadd_documents(documents)

    async def search_code(self, query: str, documents: int = 5) -> list[Document]:
        logger.info(f"Searching code documents for query: {query}")
        # query_embedding: list[float] = self.code_embedding.embed_query(query)
        result = await self.code_retriever.aget_relevant_documents(query=query)
        logger.info(f"Result: {result}")
        return result

    async def search_documents(self, query: str, documents: int = 5) -> list[SearchResult]:
        logger.info(f"Searching text documents for query: {query}")

        # Get relevant documents
        result_list = await self.document_retriever.aget_relevant_documents(query=query)

        # Rerank the results
        result_list = self.rerank_results(query, result_list)

        # Convert documents to Search Results
        result_list = [await self.format_search_result(document) for document in result_list]

        # trim to desired number of documents
        result_list = result_list[:documents]

        logger.info(f"Result: {result_list}")

        return result_list

    async def format_search_result(self, result: Document) -> SearchResult:
        previous_chunk, next_chunk = await self.get_adjacent_chunk_bodies(result)
        return SearchResult(
            before_context=previous_chunk,
            highlight=result.metadata["chunk_body"],
            after_context=next_chunk,
            source=result.metadata["source"],
            title=result.metadata["title"],
            kb_id=result.metadata["kb_id"],
            score=result.metadata["_similarity_score"],
        )

    def prepare_document_for_embedding(self, document: Document) -> Document:
        """Takes a document with delayed replacements and prepares it for embedding.
        Put the original body of the document into the metadata as "chunk_body", and
        the cleaned version of the document into the page_content for embedding.
        """
        preserved_elements = document.metadata.pop("delayed_replacements", {})

        if not preserved_elements:
            document.metadata["chunk_body"] = document.page_content
            return document

        # Rebuild the original body of the document
        chunk_body = document.page_content

        for placeholder, element in preserved_elements.items():
            chunk_body = chunk_body.replace(placeholder, element)

        # Build a version of the document that can be used for embeddings
        text_for_embeddings = document.page_content

        for placeholder, element in preserved_elements.items():
            if len(element) < 100 and "\n" not in element:
                # Leave small one-line code blocks as is
                text_for_embeddings = text_for_embeddings.replace(placeholder, element)
            else:
                text_for_embeddings = text_for_embeddings.replace(placeholder, "<code>...stripped...</code>")

        # Create a new document
        return Document(
            page_content=text_for_embeddings,
            metadata={
                **document.metadata,
                "chunk_body": chunk_body,
            },
        )


class ProjectVectorStoreManager[T: VectorStoreTypes, S: VectorStoreSettings]:
    def __init__(self, project_name: str, code_vector_store: VectorStoreManager[T, S], document_vector_store: VectorStoreManager[T, S]):
        self.project_name = project_name
        self.code_vector_store = code_vector_store
        self.document_vector_store = document_vector_store

    async def add_code_documents(self, documents: list[Document], metadata: dict[str, Any]):
        updated_metadata = {
            **metadata,
            "project_name": self.project_name,
        }
        await self.code_vector_store.add_code_documents(documents, updated_metadata)

    async def add_markdown_documents(self, documents: list[Document], metadata: dict[str, Any]):
        updated_metadata = {
            **metadata,
            "project_name": self.project_name,
        }

        await self.document_vector_store.add_documents(documents, updated_metadata)

    async def search_code(self, query: str, documents: int = 5) -> list[Document]:
        return await self.code_vector_store.search_code(query, documents)

    async def search_documents(self, query: str, documents: int = 5) -> list[SearchResult]:
        return await self.document_vector_store.search_documents(query, documents)


class KnowledgeBaseVectorStoreManager:
    def __init__(self, kb_id: str, project_vector_store: ProjectVectorStoreManager):
        self.kb_id = kb_id
        self.project_vector_store = project_vector_store

    async def add_code_documents(self, documents: list[Document], metadata: dict[str, Any]):
        updated_metadata = {
            **metadata,
            "kb_id": self.kb_id,
        }
        await self.project_vector_store.add_code_documents(documents, updated_metadata)

    async def add_markdown_documents(self, documents: list[Document], metadata: dict[str, Any]):
        updated_metadata = {
            **metadata,
            "kb_id": self.kb_id,
        }

        await self.project_vector_store.add_markdown_documents(documents, updated_metadata)

    async def search_code(self, query: str, documents: int = 5) -> list[Document]:
        return await self.project_vector_store.search_code(query, documents)

    async def search_documents(self, query: str, documents: int = 5) -> list[SearchResult]:
        return await self.project_vector_store.search_documents(query, documents)

    @classmethod
    def from_project_vector_store(cls, kb_id: str, project_vector_store: ProjectVectorStoreManager) -> "KnowledgeBaseVectorStoreManager":
        return cls(
            kb_id=kb_id,
            project_vector_store=project_vector_store,
        )
