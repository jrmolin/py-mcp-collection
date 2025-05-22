import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest
from langchain_core.documents import Document

from doc_store_vector_search_mcp.etl.store import DuckDBSettings
from doc_store_vector_search_mcp.servers.load import DocumentServer

# Mock data for testing
MOCK_PROJECT_NAME = "test_project"
MOCK_KB_ID = "test_kb"
MOCK_DIRECTORY_PATH = "/mock/directory"
MOCK_SOURCE_DOCUMENT = Document(page_content="source document content", metadata={"source": "mock_dir/mock_file.md"})
MOCK_SPLIT_CHUNKS = [
    Document(page_content="chunk 1", metadata={"source": "mock_dir/mock_file.md"}),
    Document(page_content="chunk 2", metadata={"source": "mock_dir/mock_file.md"}),
]


# Mock Embedding Model for DuckDB
class MockEmbeddingModel:
    def embed(self, text: str) -> list[float]:
        return [1.0] * 10  # Dummy vector


@pytest.mark.asyncio
@patch("doc_store_vector_search_mcp.servers.load.DirectoryLoader.load_directory")
@patch("doc_store_vector_search_mcp.servers.load.MarkdownSplitter")
@patch("doc_store_vector_search_mcp.servers.load.KnowledgeBaseVectorStoreManager")
async def test_load_directories_tool_orchestrates_etl_with_duckdb(
    mock_kb_vectorstore_manager, mock_markdown_splitter, mock_directory_loader
):
    # Configure mocks
    mock_directory_loader.return_value = [MOCK_SOURCE_DOCUMENT].__aiter__()

    mock_splitter_instance = MagicMock()
    mock_splitter_instance.split.return_value = MOCK_SPLIT_CHUNKS
    mock_markdown_splitter.return_value = mock_splitter_instance

    mock_kb_vectorstore_instance = MagicMock()
    mock_kb_vectorstore_manager.from_project_vectorstore.return_value = mock_kb_vectorstore_instance

    # Create a real DuckDB instance for the underlying vector store manager (though it's mocked here)
    # This part of the test focuses on the server's orchestration, not the vector store's internal logic
    # The actual DuckDB interaction is tested in test_store.py
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_server.duckdb")
        code_settings = DuckDBSettings(db_path=db_path)
        document_settings = DuckDBSettings(db_path=db_path)

        # Mock the ProjectVectorStoreManager that DocumentServer expects
        mock_project_vectorstore = MagicMock()
        mock_project_vectorstore.code_settings = code_settings
        mock_project_vectorstore.document_settings = document_settings

        server = DocumentServer(
            project_name=MOCK_PROJECT_NAME,
            project_vectorstore=mock_project_vectorstore,
        )

        # Call the tool
        load_summary = await server.load_directories(knowledge_base=MOCK_KB_ID, directories=[MOCK_DIRECTORY_PATH])

        # Assertions
        mock_directory_loader.assert_called_once_with(MOCK_DIRECTORY_PATH)
        mock_markdown_splitter.assert_called_once()
        mock_splitter_instance.split.assert_called_once_with([MOCK_SOURCE_DOCUMENT])
        mock_kb_vectorstore_manager.from_project_vectorstore.assert_called_once_with(MOCK_KB_ID, mock_project_vectorstore)
        mock_kb_vectorstore_instance.add_document.assert_called_once_with(
            MOCK_SPLIT_CHUNKS,
            {
                "knowledge_base": MOCK_KB_ID,
                "project": MOCK_PROJECT_NAME,
                "source": MOCK_DIRECTORY_PATH,
                "fetched": load_summary.start_time,  # Compare fetched time with start time
            },
        )

        assert load_summary.source_documents == 1
        assert load_summary.documents == 1
        assert load_summary.chunks == len(MOCK_SPLIT_CHUNKS)
        assert load_summary.took >= 0  # Ensure took time is calculated
