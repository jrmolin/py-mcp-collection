import tempfile
from pathlib import Path

import pytest

from filesystem_operations_mcp.filesystem.file_system import FileSystem
from tests.conftest import create_test_structure


@pytest.fixture
async def temp_dir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        root = Path(tmpdirname)
        await create_test_structure(root)
        yield root


@pytest.fixture
async def filesystem(temp_dir: Path):
    return FileSystem(path=temp_dir)


async def test_get_structure(filesystem: FileSystem):
    structure = filesystem.get_structure()
    assert structure.directories == ["subdir"]


async def test_get_structure_with_path(filesystem: FileSystem):
    structure = filesystem.get_structure(path=Path("subdir"))
    assert structure.directories == ["."]


async def test_get_files(filesystem: FileSystem):
    files = [file async for file in filesystem.aget_files([Path("subdir/nested.txt"), Path("subdir/script_with_hello.sh")])]
    assert len(files) == 2
    assert {f.name for f in files} == {"nested.txt", "script_with_hello.sh"}


async def test_get_files_with_directory(filesystem: FileSystem):
    files = [file async for file in filesystem.aget_files([Path("subdir")])]
    assert len(files) == 3
    assert {f.name for f in files} == {"nested.txt", "script_with_hello.sh", "should_be_ignored.env"}
