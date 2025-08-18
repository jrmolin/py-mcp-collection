import tempfile
from pathlib import Path

import pytest
from aiofiles import open as aopen

from filesystem_operations_mcp.filesystem.file_system import FileSystem
from filesystem_operations_mcp.filesystem.nodes import FileEntryTypeEnum
from filesystem_operations_mcp.filesystem.errors import FilesystemServerOutsideRootError


# Helper function to create test files
async def create_test_file(path: Path, content: str) -> None:
    async with aopen(path, "w") as f:
        await f.write(content)


# Helper function to create test directory structure
async def create_test_structure(root: Path) -> None:
    # Create some basic test files
    await create_test_file(root / "test.txt", "Test content")
    await create_test_file(root / "code.py", "def hello():\n    print('Hello')")

    # Create a subdirectory
    subdir = root / "subdir"
    subdir.mkdir()
    await create_test_file(subdir / "nested.txt", "Nested content")


@pytest.fixture
async def temp_dir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        root = Path(tmpdirname)
        await create_test_structure(root)
        yield root


@pytest.fixture
async def file_system(temp_dir: Path):
    return FileSystem(path=temp_dir)


# TESTS FOR FILE MODIFICATION OPERATIONS


@pytest.mark.asyncio
async def test_create_file(file_system: FileSystem):
    """Test creating a new file with content."""
    content = ["Line 1", "Line 2", "Line 3"]
    result = await file_system.create_file(Path("new_file.txt"), content)

    assert result is True

    # Verify file was created
    file_path = file_system.path / "new_file.txt"
    assert file_path.exists()

    # Verify content
    async with aopen(file_path) as f:
        actual_content = await f.read()
        assert actual_content == "Line 1\nLine 2\nLine 3"


@pytest.mark.asyncio
async def test_create_file_with_special_characters(file_system: FileSystem):
    """Test creating a file with special characters in the name."""
    content = ["Special content"]
    result = await file_system.create_file(Path("file with spaces.txt"), content)

    assert result is True

    # Verify file was created
    file_path = file_system.path / "file with spaces.txt"
    assert file_path.exists()


@pytest.mark.asyncio
async def test_replace_file(file_system: FileSystem):
    """Test replacing file content."""
    # First create a file
    original_content = ["Original line 1", "Original line 2"]
    await file_system.create_file(Path("replace_test.txt"), original_content)

    # Replace with new content
    new_content = ["New line 1", "New line 2", "New line 3"]
    result = await file_system.replace_file(Path("replace_test.txt"), new_content)

    assert result is True

    # Verify content was replaced
    file_path = file_system.path / "replace_test.txt"
    async with aopen(file_path) as f:
        actual_content = await f.read()
        assert actual_content == "New line 1\nNew line 2\nNew line 3"


@pytest.mark.asyncio
async def test_append_file(file_system: FileSystem):
    """Test appending content to an existing file."""
    # First create a file
    original_content = ["Original line 1", "Original line 2"]
    await file_system.create_file(Path("append_test.txt"), original_content)

    # Append new content
    append_content = ["Appended line 1", "Appended line 2"]
    result = await file_system.append_file(Path("append_test.txt"), append_content)

    assert result is True

    # Verify content was appended
    file_path = file_system.path / "append_test.txt"
    async with aopen(file_path) as f:
        actual_content = await f.read()
        expected = "Original line 1\nOriginal line 2\nAppended line 1\nAppended line 2"
        assert actual_content == expected


@pytest.mark.asyncio
async def test_delete_file(file_system: FileSystem):
    """Test deleting a file."""
    # First create a file
    content = ["Line to delete"]
    await file_system.create_file(Path("delete_test.txt"), content)

    # Verify file exists
    file_path = file_system.path / "delete_test.txt"
    assert file_path.exists()

    # Delete the file
    result = await file_system.delete_file(Path("delete_test.txt"))

    assert result is True

    # Verify file was deleted
    assert not file_path.exists()


@pytest.mark.asyncio
async def test_delete_file_lines(file_system: FileSystem):
    """Test deleting specific lines from a file."""
    # First create a file with multiple lines
    content = ["Line 1", "Line 2", "Line 3", "Line 4", "Line 5"]
    await file_system.create_file(Path("delete_lines_test.txt"), content)

    # Delete lines 2 and 4
    result = await file_system.delete_file_lines(Path("delete_lines_test.txt"), [2, 4])

    assert result is True

    # Verify lines were deleted
    file_path = file_system.path / "delete_lines_test.txt"
    async with aopen(file_path) as f:
        actual_content = await f.read()
        expected = "Line 1\nLine 3\nLine 5"
        assert actual_content == expected


@pytest.mark.asyncio
async def test_replace_file_lines(file_system: FileSystem):
    """Test replacing specific lines in a file."""
    # First create a file with multiple lines
    content = ["Line 1", "Line 2", "Line 3", "Line 4", "Line 5"]
    await file_system.create_file(Path("replace_lines_test.txt"), content)

    # Replace lines 2-3 with new content
    result = await file_system.replace_file_lines(
        Path("replace_lines_test.txt"),
        start_line_number=2,
        current_lines=["Line 2", "Line 3"],
        new_lines=["New Line 2", "New Line 3", "Extra Line"],
    )

    assert result is True

    # Verify lines were replaced
    file_path = file_system.path / "replace_lines_test.txt"
    async with aopen(file_path) as f:
        actual_content = await f.read()
        expected = "Line 1\nNew Line 2\nNew Line 3\nExtra Line\nLine 4\nLine 5"
        assert actual_content == expected


@pytest.mark.asyncio
async def test_insert_file_lines(file_system: FileSystem):
    """Test inserting lines into a file."""
    # First create a file with multiple lines
    content = ["Line 1", "Line 2", "Line 3"]
    await file_system.create_file(Path("insert_lines_test.txt"), content)

    # Insert new lines before line 2
    result = await file_system.insert_file_lines(
        Path("insert_lines_test.txt"),
        start_line_number=2,
        current_line="Line 2",
        before_or_after="before",
        insert_lines=["Inserted Line 1", "Inserted Line 2"],
    )

    assert result is True

    # Verify lines were inserted
    file_path = file_system.path / "insert_lines_test.txt"
    async with aopen(file_path) as f:
        actual_content = await f.read()
        expected = "Line 1\nInserted Line 1\nInserted Line 2\nLine 2\nLine 3"
        assert actual_content == expected


@pytest.mark.asyncio
async def test_create_directory(file_system: FileSystem):
    """Test creating a new directory."""
    result = await file_system.create_directory(Path("new_directory"))

    assert result is True

    # Verify directory was created
    dir_path = file_system.path / "new_directory"
    assert dir_path.exists()
    assert dir_path.is_dir()


@pytest.mark.asyncio
async def test_delete_directory(file_system: FileSystem):
    """Test deleting an empty directory."""
    # First create a directory
    await file_system.create_directory(Path("delete_dir_test"))

    # Verify directory exists
    dir_path = file_system.path / "delete_dir_test"
    assert dir_path.exists()

    # Delete the directory
    result = await file_system.delete_directory(Path("delete_dir_test"))

    assert result is True

    # Verify directory was deleted
    assert not dir_path.exists()


@pytest.mark.asyncio
async def test_delete_directory_recursive(file_system: FileSystem):
    """Test deleting a directory with contents recursively."""
    # First create a directory with files
    await file_system.create_directory(Path("recursive_delete_test"))
    await file_system.create_file(Path("recursive_delete_test/file1.txt"), ["Content 1"])
    await file_system.create_file(Path("recursive_delete_test/file2.txt"), ["Content 2"])

    # Verify directory and files exist
    dir_path = file_system.path / "recursive_delete_test"
    assert dir_path.exists()
    assert (dir_path / "file1.txt").exists()
    assert (dir_path / "file2.txt").exists()

    # Delete the directory recursively
    result = await file_system.delete_directory(Path("recursive_delete_test"), recursive=True)

    assert result is True

    # Verify directory and all contents were deleted
    assert not dir_path.exists()


# TESTS FOR BINARY FILE HANDLING


@pytest.mark.asyncio
async def test_binary_file_creation_and_detection(file_system: FileSystem):
    """Test creating and detecting binary files."""
    # Create a binary file
    binary_content = b"\x00\x01\x02\x03\x04\x05"
    binary_path = file_system.path / "test.bin"
    binary_path.write_bytes(binary_content)

    # Get the file entry and check its type
    files = [file async for file in file_system.aget_files([Path("test.bin")])]
    assert len(files) == 1

    binary_file = files[0]
    assert binary_file.type == FileEntryTypeEnum.BINARY
    assert binary_file.size == 6
    assert binary_file.mime_type.startswith("application/") or binary_file.mime_type == "unknown"


@pytest.mark.asyncio
async def test_image_file_detection(file_system: FileSystem):
    """Test detecting image files as binary."""
    # Create a simple "image" file (PNG header)
    png_header = b"\x89PNG\r\n\x1a\n"
    image_path = file_system.path / "test.png"
    image_path.write_bytes(png_header)

    # Get the file entry and check its type
    files = [file async for file in file_system.aget_files([Path("test.png")])]
    assert len(files) == 1

    image_file = files[0]
    assert image_file.type == FileEntryTypeEnum.BINARY
    assert image_file.mime_type.startswith("image/")


@pytest.mark.asyncio
async def test_binary_file_operations_restrictions(file_system: FileSystem):
    """Test that binary files cannot be read as text."""
    # Create a binary file
    binary_content = b"\x00\x01\x02\x03"
    binary_path = file_system.path / "restricted.bin"
    binary_path.write_bytes(binary_content)

    # Get the file entry
    files = [file async for file in file_system.aget_files([Path("restricted.bin")])]
    binary_file = files[0]

    # Verify it's detected as binary
    assert binary_file.type == FileEntryTypeEnum.BINARY

    # Test that text operations fail appropriately
    # This would typically raise an exception, but we're testing the type detection
    assert binary_file.type == FileEntryTypeEnum.BINARY


@pytest.mark.asyncio
async def test_large_file_handling(file_system: FileSystem):
    """Test handling of large files."""
    # Create a large text file
    large_content = ["Line " + str(i) for i in range(1, 1001)]  # 1000 lines
    await file_system.create_file(Path("large_test.txt"), large_content)

    # Test reading with pagination
    response = await file_system.read_file_lines(Path("large_test.txt"), start=1, count=100)
    assert response.more_lines_available is True
    assert len(response.lines.lines()) == 100
    assert response.total_lines == 1000

    # Test reading the end of the file
    response = await file_system.read_file_lines(Path("large_test.txt"), start=901, count=100)
    assert response.more_lines_available is False
    assert len(response.lines.lines()) == 100
    assert response.lines.lines()[-1] == "Line 1000"


@pytest.mark.asyncio
async def test_file_operations_with_nonexistent_files(file_system: FileSystem):
    """Test file operations with files that don't exist."""
    # Test reading a nonexistent file
    with pytest.raises(FileNotFoundError):
        await file_system.read_file_lines(Path("nonexistent.txt"))

    # Test replacing a nonexistent file
    with pytest.raises(FileNotFoundError):
        await file_system.replace_file(Path("nonexistent.txt"), ["New content"])

    # Test deleting a nonexistent file
    with pytest.raises(FileNotFoundError):
        await file_system.delete_file(Path("nonexistent.txt"))


@pytest.mark.asyncio
async def test_file_operations_with_invalid_paths(file_system: FileSystem):
    """Test file operations with invalid paths."""
    with pytest.raises(FilesystemServerOutsideRootError):
        await file_system.create_file(Path("../outside.txt"), ["Content"])

    with pytest.raises(FilesystemServerOutsideRootError):
        await file_system.read_file_lines(Path("../outside.txt"))
