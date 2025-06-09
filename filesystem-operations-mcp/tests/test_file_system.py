import tempfile
from pathlib import Path

import pytest
from aiofiles import open as aopen

from filesystem_operations_mcp.filesystem.file_system import FileSystem


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
async def file_system(temp_dir):
    return FileSystem(root=temp_dir)


@pytest.mark.asyncio
async def test_get_root(file_system, temp_dir):
    root = await file_system.get_root()
    assert root.absolute_path == temp_dir.resolve()
    assert root.relative_path == Path()


@pytest.mark.asyncio
async def test_get_structure(file_system: FileSystem):
    structure = await file_system.get_structure(depth=1)
    assert len(structure) == 3  # root, nested, deeper

    # Test with different depths
    structure = await file_system.get_structure(depth=0)
    assert len(structure) == 2  # root, nested

    # Test with includes
    structure = await file_system.get_structure(depth=2, includes=["deeper"])
    assert len(structure) == 1

    # Test with excludes
    structure = await file_system.get_structure(depth=2, excludes=["*.py"])
    assert len(structure) == 3

    # Test with skip_hidden
    structure = await file_system.get_structure(depth=2, skip_hidden=True)
    assert len(structure) == 3


@pytest.mark.asyncio
async def test_get_files(file_system: FileSystem):
    # Test getting specific files
    files = await file_system.get_files(["code.py", "readme.md"])
    assert len(files) == 2
    assert {f.name for f in files} == {"code.py", "readme.md"}

    # Test getting text files
    text_files = await file_system.get_text_files(["code.py", "readme.md", "large.txt"])
    assert len(text_files) == 3
    assert all(not f.is_binary for f in text_files)


@pytest.mark.asyncio
async def test_get_directories(file_system: FileSystem):
    dirs = await file_system.get_directories(["nested", "nested/deeper"])
    assert len(dirs) == 2
    assert {d.name for d in dirs} == {"nested", "deeper"}


@pytest.mark.asyncio
async def test_get_file_matches(file_system: FileSystem):
    # Test simple content matching
    matches = await file_system.get_file_matches("large.txt", "Target line")
    assert len(matches) == 1
    assert "Target line" in matches[0].match.lines()[0]

    # Test regex matching
    matches = await file_system.get_file_matches("code.py", r"def \w+", pattern_is_regex=True)
    assert len(matches) == 1
    assert "def hello" in matches[0].match.lines()[0]

    # Test context lines
    matches = await file_system.get_file_matches("large.txt", "Target line", before=2, after=2)
    assert len(matches) == 1
    assert len(matches[0].before.lines()) == 2
    assert len(matches[0].after.lines()) == 2


@pytest.mark.asyncio
async def test_find_files(file_system: FileSystem):
    # Test finding all Python files
    files = await file_system.find_files("*.py")
    assert len(files) == 3  # code.py, deep.py, very_deep.py
    assert all(f.name.endswith(".py") for f in files)

    # Test finding files in nested directory
    files = await file_system.find_files("*.py", directory_path="nested")
    assert len(files) == 2
    assert files[0].name == "deep.py"
    assert files[1].name == "very_deep.py"

    # Test finding files with includes/excludes
    files = await file_system.find_files("*.py", includes=["code.py"])
    assert len(files) == 1
    assert files[0].name == "code.py"

    # Test finding files with skip_hidden
    files = await file_system.find_files("*", skip_hidden=True)
    assert not any(f.name.startswith(".") for f in files)


@pytest.mark.asyncio
async def test_find_dirs(file_system: FileSystem):
    # Test finding all directories
    dirs = await file_system.find_dirs("*")
    assert len(dirs) == 2  # nested, deeper
    assert {d.name for d in dirs} == {"nested", "deeper"}

    # Test finding directories with includes/excludes
    dirs = await file_system.find_dirs("*", includes=["nested"])
    assert len(dirs) == 1
    assert dirs[0].name == "nested"

    # Test finding directories with skip_hidden
    dirs = await file_system.find_dirs("*", skip_hidden=True)
    assert not any(d.name.startswith(".") for d in dirs)


@pytest.mark.asyncio
async def test_file_type_detection(file_system: FileSystem):
    # Test files with extensions
    files = await file_system.get_files(["code.py", "data.json", "readme.md"])
    assert files[0].is_code
    assert files[1].is_data
    assert files[2].is_text

    # Test files without extensions
    files = await file_system.get_files(["no_extension_code", "no_extension_data", "no_extension_text"])
    assert files[0].is_code
    assert files[1].is_data
    assert files[2].is_text


@pytest.mark.asyncio
async def test_special_characters(file_system: FileSystem):
    # Test files with spaces, dashes, and underscores
    files = await file_system.get_files(["file with spaces.txt", "file-with-dashes.txt", "file_with_underscores.txt"])
    assert len(files) == 3
    assert all(f.is_text for f in files)
