import pytest
from langchain_core.documents import Document
from syrupy.assertion import SnapshotAssertion

from doc_store_vector_search_mcp.etl.split import (
    CodeSplitter,
    CodeSplitterLanguage,
)

MOCK_PYTHON_CODE = """
import os

class Manager:
    '''Docstring for Manager class'''
    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return f"Manager(name={self.name})"

class SubManager(Manager):
    def __init__(self, name: str, age: int):
        super().__init__(name)
        self.age = age

    def __str__(self):
        return f"SubManager(name={self.name}, age={self.age})"

def main():
    manager = Manager("John")
    print(manager)

    subManager = SubManager(manager, 30)
    print(subManager)

if __name__ == "__main__":
    main()
"""

MOCK_GOLANG_CODE = """
package main

import "fmt"

type Manager struct {
    name string
}

type SubManager struct {
    Manager
    age int
}

func (m *Manager) String() string {
    return fmt.Sprintf("Manager(name=%s)", m.name)
}

func (m *SubManager) String() string {
    return fmt.Sprintf("SubManager(name=%s, age=%d)", m.name, m.age)
}

func main() {
    manager := Manager{name: "John"}
    fmt.Println(manager)

    subManager := SubManager{Manager: manager, age: 30}
    fmt.Println(subManager)
}
"""


@pytest.mark.parametrize(
    ("code", "language"),
    [
        (MOCK_PYTHON_CODE, CodeSplitterLanguage.PYTHON),
        (MOCK_GOLANG_CODE, CodeSplitterLanguage.GO),
    ],
    ids=["python", "golang"],
)
def test_codesplitter_splits_by_language_syntax(code: str, language: CodeSplitterLanguage, snapshot: SnapshotAssertion):
    splitter = CodeSplitter(language=language)

    split_documents = splitter.split_to_documents(code)

    assert isinstance(split_documents, list)
    assert len(split_documents) > 0
    for doc in split_documents:
        assert isinstance(doc, Document)

    snapshot.assert_match(split_documents)
