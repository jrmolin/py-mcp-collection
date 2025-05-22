

import uuid

import pytest
from langchain_community.vectorstores import DuckDB
from langchain_core.documents import Document

from doc_store_vector_search_mcp.etl.store import (
    DuckDBSettings,
    KnowledgeBaseVectorStoreManager,
    ProjectVectorStoreManager,
    VectorStoreManager,
)

# Mock data for testing
MOCK_TEXT_CHUNKS = ["chunk 1 content", "chunk 2 content"]
MOCK_CODE_CHUNKS = ["def func():", "    pass"]
MOCK_METADATA = {"source": "mock_source"}
MOCK_PROJECT_NAME = "test_project"
MOCK_KB_ID = "test_kb"


@pytest.mark.asyncio
async def test_adds_documents_to_duckdb():
    # Use in-memory DuckDB
    code_settings = DuckDBSettings(db_path=":memory:")
    document_settings = DuckDBSettings(db_path=":memory:")

    # Use real DuckDB instances and real embedding models
    manager = VectorStoreManager[DuckDB, DuckDBSettings](
        project_name=MOCK_PROJECT_NAME,
        kb_id=MOCK_KB_ID,
        code_settings=code_settings,
        document_settings=document_settings,
        vector_store_class=DuckDB,
    )

    code_documents = [Document(id=str(uuid.uuid4()), page_content=code_chunk, metadata=MOCK_METADATA) for code_chunk in MOCK_CODE_CHUNKS]
    text_documents = [Document(id=str(uuid.uuid4()), page_content=text_chunk, metadata=MOCK_METADATA) for text_chunk in MOCK_TEXT_CHUNKS]

    await manager.add_code_documents(code_documents, MOCK_METADATA)
    await manager.add_documents(text_documents, MOCK_METADATA)

    # Verify documents were added to the real DuckDB instances by querying
    # Note: Similarity search with real embeddings will return documents based on semantic similarity.
    # We are primarily verifying that documents are stored and retrievable.
    code_results = manager.code_vector_store.similarity_search("chunk", k=10)
    doc_results = manager.document_vector_store.similarity_search("chunk", k=10)

    assert len(code_results) == len(MOCK_CODE_CHUNKS)
    assert len(doc_results) == len(MOCK_TEXT_CHUNKS)

    # Verify metadata is present (DuckDB stores metadata)
    assert all("source" in doc.metadata for doc in code_results)
    assert all("source" in doc.metadata for doc in doc_results)


@pytest.mark.asyncio
async def test_adds_project_metadata_to_duckdb():
    # Use in-memory DuckDB
    code_settings = DuckDBSettings(db_path=":memory:")
    document_settings = DuckDBSettings(db_path=":memory:")

    # Instantiate a real VectorStoreManager with real embedding models
    vector_store_manager = VectorStoreManager[DuckDB, DuckDBSettings](
        project_name=MOCK_PROJECT_NAME,
        kb_id="dummy_kb_id",  # KB ID is added by KnowledgeBaseVectorStoreManager
        code_settings=code_settings,
        document_settings=document_settings,
        vector_store_class=DuckDB,
    )

    # Use real add methods and check the metadata in the DuckDB instance
    manager = ProjectVectorStoreManager(
        project_name=MOCK_PROJECT_NAME,
        code_vector_store=vector_store_manager,
        document_vector_store=vector_store_manager,
    )

    code_documents = [Document(id=str(uuid.uuid4()), page_content=code_chunk, metadata=MOCK_METADATA) for code_chunk in MOCK_CODE_CHUNKS]
    text_documents = [Document(id=str(uuid.uuid4()), page_content=text_chunk, metadata=MOCK_METADATA) for text_chunk in MOCK_TEXT_CHUNKS]

    await manager.add_code_documents(code_documents, MOCK_METADATA)
    await manager.add_markdown_documents(text_documents, MOCK_METADATA)

    code_results = vector_store_manager.code_vector_store.similarity_search("chunk", k=10)
    doc_results = vector_store_manager.document_vector_store.similarity_search("chunk", k=10)

    assert all(doc.metadata.get("project_name") == MOCK_PROJECT_NAME for doc in code_results)
    assert all(doc.metadata.get("project_name") == MOCK_PROJECT_NAME for doc in doc_results)


@pytest.mark.asyncio
async def test_adds_kb_metadata_to_duckdb():

    code_settings = DuckDBSettings(db_path=":memory:")
    document_settings = DuckDBSettings(db_path=":memory:")

    vector_store_manager = VectorStoreManager[DuckDB, DuckDBSettings](
        project_name="dummy", kb_id="dummy", code_settings=code_settings, document_settings=document_settings, vector_store_class=DuckDB
    )

    project_vector_store_manager = ProjectVectorStoreManager[DuckDB, DuckDBSettings](
        project_name="dummy_project_name",
        code_vector_store=vector_store_manager,
        document_vector_store=vector_store_manager,
    )

    manager = KnowledgeBaseVectorStoreManager.from_project_vector_store(kb_id=MOCK_KB_ID, project_vector_store=project_vector_store_manager)

    code_documents = [Document(id=str(uuid.uuid4()), page_content=code_chunk, metadata=MOCK_METADATA) for code_chunk in MOCK_CODE_CHUNKS]
    text_documents = [Document(id=str(uuid.uuid4()), page_content=text_chunk, metadata=MOCK_METADATA) for text_chunk in MOCK_TEXT_CHUNKS]

    await manager.add_code_documents(code_documents, MOCK_METADATA)
    await manager.add_markdown_documents(text_documents, MOCK_METADATA)

    code_results = vector_store_manager.code_vector_store.similarity_search("chunk", k=10)
    doc_results = vector_store_manager.document_vector_store.similarity_search("chunk", k=10)

    assert all(doc.metadata.get("kb_id") == MOCK_KB_ID for doc in code_results)
    assert all(doc.metadata.get("kb_id") == MOCK_KB_ID for doc in doc_results)
