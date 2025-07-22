import tempfile
from pathlib import Path

import pytest
from aiofiles import open as aopen

from filesystem_operations_mcp.filesystem.file_system import FileSystem
from filesystem_operations_mcp.filesystem.nodes import FileEntry, FileEntryTypeEnum


# Helper function to create test files
async def create_test_file(path: Path, content: str) -> None:
    async with aopen(path, "w") as f:
        await f.write(content)


# Helper function to create test directory structure
async def create_test_structure(root: Path) -> None:
    # Create a large text file for content searching
    large_text = "Line 1\n" * 100 + "Target line\n" + "Line 2\n" * 100
    await create_test_file(root / "large.txt", large_text)

    # Create code files
    await create_test_file(root / "code.py", "def hello():\n    print('Hello, World!')")
    await create_test_file(root / "script.sh", "#!/bin/bash\necho 'Hello'")
    await create_test_file(root / "no_extension_code", "def test():\n    return True")

    # Create data files
    await create_test_file(root / "data.json", '{"key": "value", "nested": {"array": [1, 2, 3]}}')
    await create_test_file(root / "config.yaml", "app:\n  name: test\n  version: 1.0")
    await create_test_file(root / "no_extension_data", '{"type": "data"}')

    # Create text files
    await create_test_file(root / "readme.md", "# Test Project\n\nThis is a test project.")
    await create_test_file(root / "notes.txt", "Important notes:\n1. First point\n2. Second point")
    await create_test_file(
        root / "no_extension_text",
        """
    This is a text file without extension. It contains a fair amount of text.
    It contains a lot of text. It should be able to be identified as text by its content even
    though it doesn't have an extension.
    """,
    )

    # Create nested directory structure
    nested = root / "nested"
    nested.mkdir()
    await create_test_file(nested / "deep.py", "def deep():\n    return 'deep'")
    await create_test_file(nested / "config.json", '{"nested": true}')

    # Create another level of nesting
    deeper = nested / "deeper"
    deeper.mkdir()
    await create_test_file(deeper / "very_deep.py", "def very_deep():\n    return 'very deep'")

    # Create hidden files and directories
    await create_test_file(root / ".hidden", "Hidden content")
    hidden_dir = root / ".hidden_dir"
    hidden_dir.mkdir()
    await create_test_file(hidden_dir / "secret.txt", "Secret content")

    # Create files with special characters
    await create_test_file(root / "file with spaces.txt", "Content with spaces")
    await create_test_file(root / "file-with-dashes.txt", "Content with dashes")
    await create_test_file(root / "file_with_underscores.txt", "Content with underscores")


@pytest.fixture
async def temp_dir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        root = Path(tmpdirname)
        await create_test_structure(root)
        yield root


@pytest.fixture
async def file_system(temp_dir: Path):
    return FileSystem(path=temp_dir)


@pytest.mark.asyncio
async def test_get_root(file_system: FileSystem):
    files = [file async for file in file_system.aget_root()]
    assert len(files) == 11


@pytest.mark.asyncio
async def test_get_structure(file_system: FileSystem):
    filesystem_structure = file_system.get_structure(depth=1)
    assert len(filesystem_structure.directories) == 1 # nested

    # Test with different depths
    filesystem_structure = file_system.get_structure(depth=2)
    assert len(filesystem_structure.directories) == 2 # nested, deeper


    filesystem_structure = file_system.get_structure(depth=2, max_results=1)
    assert len(filesystem_structure.directories) == 1 # nested
    assert filesystem_structure.max_results_reached



@pytest.mark.asyncio
async def test_file_type_detection(file_system: FileSystem):
    # Test files with extensions
    files: list[FileEntry] = [file async for file in file_system.aget_files(["code.py", "data.json", "readme.md"])]
    assert files[0].type == FileEntryTypeEnum.CODE
    assert files[1].type == FileEntryTypeEnum.DATA
    assert files[2].type == FileEntryTypeEnum.TEXT

    # Test files without extensions
    files = [file async for file in file_system.aget_files(["no_extension_code", "no_extension_data", "no_extension_text"])]
    assert files[0].type == FileEntryTypeEnum.CODE
    assert files[1].type == FileEntryTypeEnum.DATA
    assert files[2].type == FileEntryTypeEnum.TEXT


@pytest.mark.asyncio
async def test_special_characters(file_system: FileSystem):
    # Test files with spaces, dashes, and underscores
    files = [file async for file in file_system.aget_files(["file with spaces.txt", "file-with-dashes.txt", "file_with_underscores.txt"])]
    assert len(files) == 3
    assert all(f.type == FileEntryTypeEnum.TEXT for f in files)
