import json
from typing import Any

import pytest
from langchain_core.documents import Document
from syrupy.assertion import SnapshotAssertion

from doc_store_vector_search_mcp.etl.split import (
    JsonSplitter,
)


def generate_large_json_list(n: int) -> list[dict[str, Any]]:
    def new_entry(i: int) -> dict[str, Any]:
        return {
            "id": i,
            "name": f"item {i} name",
            "text": f"item {i} content",
            "author": f"item {i} author",
        }

    return [new_entry(i) for i in range(1, n + 1)]


MOCK_JSON_DICT = json.dumps({"items": generate_large_json_list(2)})
MOCK_JSON_LIST = json.dumps(generate_large_json_list(2))
MOCK_LARGE_JSON_DICT = json.dumps({"items": generate_large_json_list(50)})
MOCK_LARGE_JSON_LIST = json.dumps(generate_large_json_list(50))


@pytest.mark.parametrize("json_data", [MOCK_JSON_DICT, MOCK_LARGE_JSON_DICT], ids=["small", "large"])
def test_split_json_dict_into_documents(json_data: str, snapshot: SnapshotAssertion):
    splitter = JsonSplitter()

    loaded_json = json.loads(json_data)

    split_documents = splitter.split_to_documents(loaded_json)

    assert isinstance(split_documents, list)
    assert len(split_documents) > 0

    for doc in split_documents:
        assert isinstance(doc, Document)

    snapshot.assert_match(split_documents)


@pytest.mark.parametrize("json_data", [MOCK_JSON_LIST, MOCK_LARGE_JSON_LIST], ids=["small", "large"])
def test_split_json_list_into_documents(json_data: str, snapshot: SnapshotAssertion):
    splitter = JsonSplitter()

    loaded_json = json.loads(json_data)

    split_documents = []
    for item in loaded_json:
        split_documents.extend(splitter.split_to_documents(item))

    assert isinstance(split_documents, list)
    assert len(split_documents) > 0

    for doc in split_documents:
        assert isinstance(doc, Document)

    snapshot.assert_match(split_documents)
