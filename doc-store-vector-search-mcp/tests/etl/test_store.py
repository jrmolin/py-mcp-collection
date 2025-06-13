import uuid
from typing import Any

import pytest
from langchain_community.vectorstores import DuckDB
from langchain_core.documents import Document

from doc_store_vector_search_mcp.etl.store import (
    DuckDBSettings,
    KnowledgeBaseVectorStoreManager,
    ProjectVectorStoreManager,
    VectorStoreManager,
)
from tests.etl.samples import CODE_DOCS

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


@pytest.mark.asyncio
async def test_search_vectorstoremanager():
    code_settings = DuckDBSettings(db_path=":memory:")
    document_settings = DuckDBSettings(db_path=":memory:")

    manager = VectorStoreManager[DuckDB, DuckDBSettings](
        project_name=MOCK_PROJECT_NAME,
        kb_id=MOCK_KB_ID,
        code_settings=code_settings,
        document_settings=document_settings,
        vector_store_class=DuckDB,
    )

    code_documents = [Document(id=str(uuid.uuid4()), page_content=code_chunk, metadata=MOCK_METADATA) for code_chunk in MOCK_CODE_CHUNKS]
    text_documents = [Document(id=str(uuid.uuid4()), page_content=text_chunk, metadata=MOCK_METADATA) for text_chunk in MOCK_TEXT_CHUNKS]

    # Add documents
    await manager.add_code_documents(code_documents, MOCK_METADATA)
    await manager.add_documents(text_documents, MOCK_METADATA)

    # Search documents
    found_docs = await manager.search_documents("chunk", documents=10)
    found_code = await manager.search_code("def", documents=10)

    assert any("chunk" in doc.page_content for doc in found_docs)
    assert any("def" in doc.page_content for doc in found_code)
    assert all("source" in doc.metadata for doc in found_docs)
    assert all("source" in doc.metadata for doc in found_code)


@pytest.mark.asyncio
async def test_search_projectvectorstoremanager():
    code_settings = DuckDBSettings(db_path=":memory:")
    document_settings = DuckDBSettings(db_path=":memory:")

    vector_store_manager = VectorStoreManager[DuckDB, DuckDBSettings](
        project_name=MOCK_PROJECT_NAME,
        kb_id="dummy_kb_id",
        code_settings=code_settings,
        document_settings=document_settings,
        vector_store_class=DuckDB,
    )

    manager = ProjectVectorStoreManager(
        project_name=MOCK_PROJECT_NAME,
        code_vector_store=vector_store_manager,
        document_vector_store=vector_store_manager,
    )

    code_documents = [Document(id=str(uuid.uuid4()), page_content=code_chunk, metadata=MOCK_METADATA) for code_chunk in MOCK_CODE_CHUNKS]
    text_documents = [Document(id=str(uuid.uuid4()), page_content=text_chunk, metadata=MOCK_METADATA) for text_chunk in MOCK_TEXT_CHUNKS]

    await manager.add_code_documents(code_documents, MOCK_METADATA)
    await manager.add_markdown_documents(text_documents, MOCK_METADATA)

    found_docs = await manager.search_documents("chunk", documents=10)
    found_code = await manager.search_code("def", documents=10)

    assert any("chunk" in doc.page_content for doc in found_docs)
    assert any("def" in doc.page_content for doc in found_code)
    assert all(doc.metadata.get("project_name") == MOCK_PROJECT_NAME for doc in found_docs)
    assert all(doc.metadata.get("project_name") == MOCK_PROJECT_NAME for doc in found_code)


@pytest.mark.asyncio
async def test_search_knowledgebasevectorstoremanager():
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

    found_docs = await manager.search_documents("chunk", documents=10)
    found_code = await manager.search_code("def", documents=10)

    assert any("chunk" in doc.page_content for doc in found_docs)
    assert any("def" in doc.page_content for doc in found_code)
    assert all(doc.metadata.get("kb_id") == MOCK_KB_ID for doc in found_docs)
    assert all(doc.metadata.get("kb_id") == MOCK_KB_ID for doc in found_code)


@pytest.mark.asyncio
async def test_semantic_search_documents():
    code_settings = DuckDBSettings(db_path=":memory:")
    document_settings = DuckDBSettings(db_path=":memory:")

    manager = VectorStoreManager[DuckDB, DuckDBSettings](
        project_name="semantic_test_project",
        kb_id="semantic_test_kb",
        code_settings=code_settings,
        document_settings=document_settings,
        vector_store_class=DuckDB,
    )

    # Insert a variety of documents with distinct topics
    docs = [
        ("Soccer is a popular sport played worldwide.", {"topic": "sports"}),
        ("Python is a programming language used for AI.", {"topic": "tech"}),
        ("Pizza is a delicious Italian food.", {"topic": "food"}),
        ("Dogs are loyal and friendly animals.", {"topic": "animals"}),
        ("Basketball involves shooting hoops.", {"topic": "sports"}),
        ("Quantum computing is the future of technology.", {"topic": "tech"}),
        ("Sushi is a traditional Japanese dish.", {"topic": "food"}),
        ("Cats are independent pets.", {"topic": "animals"}),
        ("Tennis is played on a court with rackets.", {"topic": "sports"}),
        ("Machine learning enables computers to learn from data.", {"topic": "tech"}),
    ]
    text_documents = [Document(id=str(uuid.uuid4()), page_content=content, metadata=meta) for content, meta in docs]

    await manager.add_documents(text_documents, {"source": "semantic_test"})

    # Search for sports
    sports_results = await manager.search_documents("What is a popular sport?", documents=3)
    assert any("Soccer" in doc.page_content or "Basketball" in doc.page_content or "Tennis" in doc.page_content for doc in sports_results)
    assert all(doc.metadata["topic"] == "sports" for doc in sports_results[:1])  # Top result should be sports

    # Search for tech
    tech_results = await manager.search_documents("What is a programming language for AI?", documents=3)
    assert any(
        "Python" in doc.page_content or "Machine learning" in doc.page_content or "Quantum computing" in doc.page_content
        for doc in tech_results
    )
    assert all(doc.metadata["topic"] == "tech" for doc in tech_results[:1])

    # Search for food
    food_results = await manager.search_documents("What is a traditional Japanese dish?", documents=2)
    assert any("Sushi" in doc.page_content for doc in food_results)
    assert all(doc.metadata["topic"] == "food" for doc in food_results[:1])

    # Search for animals
    animal_results = await manager.search_documents("What is a loyal pet?", documents=2)
    assert any("Dogs" in doc.page_content for doc in animal_results)
    assert all(doc.metadata["topic"] == "animals" for doc in animal_results[:1])


@pytest.mark.asyncio
async def test_semantic_search_code():
    code_settings = DuckDBSettings(db_path=":memory:")
    document_settings = DuckDBSettings(db_path=":memory:")

    manager = VectorStoreManager[DuckDB, DuckDBSettings](
        project_name="semantic_test_project",
        kb_id="semantic_test_kb",
        code_settings=code_settings,
        document_settings=document_settings,
        vector_store_class=DuckDB,
    )

    code_documents = [Document(id=str(uuid.uuid4()), page_content=code_chunk, metadata=meta) for code_chunk, meta in CODE_DOCS]
    await manager.add_code_documents(code_documents, MOCK_METADATA)

    found_code = await manager.search_code("def", documents=10)
    found_topics = [doc.metadata.get("topic") for doc in found_code]
    assert len(found_topics) == 4
    assert "calculators" in found_topics
    assert "employees" in found_topics
    assert "vegetables" in found_topics
    assert "cars" in found_topics

    found_code = await manager.search_code("class", documents=10)
    found_topics = [doc.metadata.get("topic") for doc in found_code]
    assert len(found_topics) == 4
    assert "calculators" in found_topics
    assert "employees" in found_topics
    assert "vegetables" in found_topics
    assert "cars" in found_topics

    # calculate is not a word in the code, but it is semantically similar to the word "calculate"
    found_code = await manager.search_code("calculate", documents=10)

    # Highest score should be for calculators
    assert get_topic(found_code[0]) == "calculators"
    scores = [get_similarity_score(doc) for doc in found_code]

    assert scores[0] > 0.5  # calculators has a higher score
    assert scores[1] < 0.3

    found_code = await manager.search_code("working during the day", documents=10)

    assert get_topic(found_code[0]) == "employees"
    scores = [get_similarity_score(doc) for doc in found_code]

    assert scores[0] > 0.30  # employees has a higher score
    assert scores[1] < 0.22

    found_code = await manager.search_code("Tastes good when cooked into a stew?", documents=10)

    assert get_topic(found_code[0]) == "vegetables"
    scores = [get_similarity_score(doc) for doc in found_code]
    assert scores[0] > 0.40  # vegetables has a higher score
    assert scores[1] < 0.20

    found_code = await manager.search_code("A 1992 Ford Mustang!", documents=10)

    assert get_topic(found_code[0]) == "cars"
    scores = [get_similarity_score(doc) for doc in found_code]
    assert scores[0] > 0.40  # cars has a higher score
    assert scores[1] < 0.20


def get_topic(doc: Document) -> str:
    metadata: dict[str, Any] = doc.metadata
    assert metadata is not None
    assert "topic" in metadata

    topic = metadata.get("topic")
    assert topic is not None
    return topic


def get_similarity_score(doc: Document) -> float:
    metadata: dict[str, Any] = doc.metadata
    assert metadata is not None

    assert "_similarity_score" in metadata
    score = metadata.get("_similarity_score")
    assert score is not None

    return score
