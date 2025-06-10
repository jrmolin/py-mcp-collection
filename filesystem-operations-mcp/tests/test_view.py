from pathlib import Path

import pytest
from aiofiles import open as aopen
from aiofiles import tempfile
from test_file_system import create_test_structure

from filesystem_operations_mcp.filesystem.nodes.file import FileEntry
from filesystem_operations_mcp.filesystem.view import FileExportableField


# Helper function to create test files
async def create_test_file(path: Path, content: str) -> None:
    async with aopen(path, "w") as f:
        await f.write(content)


@pytest.fixture
async def temp_dir():
    async with tempfile.TemporaryDirectory() as tmpdirname:
        root = Path(tmpdirname)
        await create_test_structure(root)
        yield root


def get_file_entry(temp_dir, filename):
    return FileEntry(absolute_path=temp_dir / filename, root=temp_dir)


@pytest.mark.asyncio
async def test_file_exportable_field_default_fields(temp_dir):
    node = get_file_entry(temp_dir, "readme.md")
    file_fields = FileExportableField()
    result = await file_fields.apply(node)
    # Default fields: file_path, file_type, size
    assert "file_path" in result
    assert result["file_path"] == "readme.md"
    assert "file_type" in result
    assert isinstance(result["file_type"], str) or result["file_type"] is None
    assert "size" in result
    assert isinstance(result["size"], int)
    # Non-default fields should not be present
    assert "basename" not in result
    assert "extension" not in result
    assert "read_text" not in result


@pytest.mark.asyncio
async def test_file_exportable_field_toggle_fields(temp_dir):
    node = get_file_entry(temp_dir, "code.py")
    file_fields = FileExportableField(basename=True, extension=True, read_text=True)
    result = await file_fields.apply(node)
    assert result["basename"] == "code.py"
    assert result["extension"] == ".py"
    assert "read_text" in result
    assert "def hello()" in result["read_text"]


@pytest.mark.asyncio
async def test_file_exportable_field_binary_file(temp_dir):
    # Create a binary file
    binary_path = temp_dir / "binary.bin"
    binary_path.write_bytes(b"\x00\x01\x02\x03")
    node = FileEntry(absolute_path=binary_path, root=temp_dir)
    file_fields = FileExportableField(is_binary=True, read_binary_base64=True)
    result = await file_fields.apply(node)
    assert result["is_binary"] is True
    assert "read_binary_base64" in result
    assert isinstance(result["read_binary_base64"], str)


@pytest.mark.asyncio
async def test_file_exportable_field_preview_and_lines(temp_dir):
    node = get_file_entry(temp_dir, "notes.txt")
    file_fields = FileExportableField(preview=True, read=True, limit_preview=10)
    result = await file_fields.apply(node)
    assert "preview" in result
    assert result["preview"] == "Important "
    assert len(result["preview"]) <= 10
    assert "read" in result
    assert isinstance(result["read"], dict)
    lines = result["read"]
    assert len(lines) == 3
    assert lines[0] == "Important notes:"
    assert lines[1] == "1. First point"
    assert lines[2] == "2. Second point"
