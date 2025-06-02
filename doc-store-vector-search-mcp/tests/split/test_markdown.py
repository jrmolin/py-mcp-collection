from langchain_core.documents import Document
from syrupy.assertion import SnapshotAssertion

from doc_store_vector_search_mcp.etl.split import (
    MarkdownSplitter,
)

MOCK_MARKDOWN_DOCUMENT = """
# Header 1

CONTENT 1

## Header 2

CONTENT 2

### Header 3

CONTENT 3

# Header 4

CONTENT 4
"""


def test_markdownsplitter_splits_by_headers_and_chunks(snapshot: SnapshotAssertion):
    splitter = MarkdownSplitter()

    split_documents = splitter.split_to_documents(MOCK_MARKDOWN_DOCUMENT)

    assert isinstance(split_documents, list)
    assert len(split_documents) > 0

    for doc in split_documents:
        assert isinstance(doc, Document)

        assert any(header in doc.metadata for header in ["Header 1", "Header 2", "Header 3", "Header 4"])

    snapshot.assert_match(split_documents)
