from typing import Any, TypeVar

import duckdb
import torch
from langchain_community.vectorstores import DuckDB, ElasticsearchStore
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from transformers import AutoModel, AutoTokenizer

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
    def __init__(self):
        self.device = "cpu"

        self.tokenizer = AutoTokenizer.from_pretrained("Salesforce/codet5p-110m-embedding", trust_remote_code=True)
        self.model = AutoModel.from_pretrained("Salesforce/codet5p-110m-embedding", trust_remote_code=True).to(self.device)

        self.torch = torch

    def embed(self, text: str) -> list[float]:
        inputs = self.tokenizer.encode(text, return_tensors="pt").to(self.device)
        with self.torch.no_grad():
            embedding = self.model(inputs)[0]
        return embedding.cpu().numpy().tolist()

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self.embed(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self.embed(text)


class VectorStoreManager[T: VectorStoreTypes, S: VectorStoreSettings]:
    def __init__(self, project_name: str, kb_id: str, code_settings: S, document_settings: S, vector_store_class: type[T]):
        self.project_name = project_name
        self.kb_id = kb_id

        self.code_embedding = CodeEmbedding()
        self.document_embedding = TextEmbedding()

        self.code_vector_store: T = vector_store_class(embedding=self.code_embedding, connection=code_settings.connect())  # type: ignore
        self.document_vector_store: T = vector_store_class(embedding=self.document_embedding, connection=document_settings.connect())  # type: ignore

    async def add_code_documents(self, documents: list[Document], metadata: dict[str, Any]):
        [document.metadata.update(metadata or {}) for document in documents]

        await self.code_vector_store.aadd_documents(documents)

    async def add_documents(self, documents: list[Document], metadata: dict[str, Any]):
        [document.metadata.update(metadata or {}) for document in documents]
        await self.document_vector_store.aadd_documents(documents)


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

    @classmethod
    def from_project_vector_store(cls, kb_id: str, project_vector_store: ProjectVectorStoreManager) -> "KnowledgeBaseVectorStoreManager":
        return cls(
            kb_id=kb_id,
            project_vector_store=project_vector_store,
        )
