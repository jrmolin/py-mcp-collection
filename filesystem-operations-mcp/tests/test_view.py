from pathlib import Path

import pytest
from aiofiles import open as aopen
from aiofiles import tempfile

from filesystem_operations_mcp.filesystem.file_system import FileSystem
from filesystem_operations_mcp.filesystem.nodes import FileEntry
from filesystem_operations_mcp.filesystem.view import FileExportableField
from tests.test_file_system import create_test_structure


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


@pytest.fixture
def file_system(temp_dir: Path):
    return FileSystem(path=temp_dir)


def get_file_entry(file_system: FileSystem, filename: str):
    return FileEntry(path=file_system.path / filename, filesystem=file_system)


@pytest.mark.asyncio
async def test_file_exportable_field_default_fields(file_system: FileSystem):
    node = file_system.get_file("readme.md")
    file_fields = FileExportableField()
    result, _ = file_fields.apply(node)
    # Default fields: file_path, file_type, size
    assert "relative_path_str" in result
    assert result.get("relative_path_str") == "readme.md"
    assert "type" in result
    assert isinstance(result["type"], str) or result["type"] is None
    assert "size" in result
    assert isinstance(result["size"], int)
    # Non-default fields should not be present
    assert "basename" not in result
    assert "extension" not in result
    assert "read_text" not in result


@pytest.mark.asyncio
async def test_file_exportable_field_toggle_fields(file_system: FileSystem):
    node = file_system.get_file("code.py")
    file_fields = FileExportableField(
        read=True, basename=True, extension=True, created_at=True, modified_at=True, owner=True, group=True, mime_type=True
    )
    result, _ = file_fields.apply(node)
    expensive_fields = await file_fields.aapply(node)
    assert result["stem"] == "code"
    assert result["extension"] == ".py"
    assert "read" in expensive_fields
    assert "def hello():" in expensive_fields["read"][1]
    assert "created_at" in result
    assert "modified_at" in result
    assert "owner" in result
    assert "group" in result
    assert "mime_type" in result


# @pytest.mark.asyncio
# async def test_file_exportable_field_binary_file(file_system: FileSystem, temp_dir: Path):
#     Create a binary file
#     binary_path = temp_dir / "binary.bin"
#     _ = binary_path.write_bytes(b"\x00\x01\x02\x03")
#     node = FileEntry(path=binary_path, filesystem=file_system)
#     file_fields = FileExportableField(is_binary=True, read_binary_base64=True)
#     result = await file_fields.apply(node)
#     assert result["is_binary"] is True
#     assert "read_binary_base64" in result
#     assert isinstance(result["read_binary_base64"], str)


@pytest.mark.asyncio
async def test_file_exportable_field_preview(file_system: FileSystem):
    node = file_system.get_file("notes.txt")
    file_fields = FileExportableField(preview=True)
    # result, _ = file_fields.apply(node)
    expensive_fields = await file_fields.aapply(node)
    assert "preview" in expensive_fields
    assert expensive_fields["preview"][1] == "Important notes:"
    assert expensive_fields["preview"][2] == "1. First point"
    assert expensive_fields["preview"][3] == "2. Second point"


@pytest.mark.asyncio
async def test_file_exportable_field_summarize(file_system: FileSystem):
    _ = await file_system.create_file(
        file_system.path / "notes.md",
        "# Important notes: The first important note is about the first point. The second important note is about the second point.",
    )
    node = file_system.get_file("notes.md")
    file_fields = FileExportableField(summarize=True)
    result = await file_fields.aapply(node)
    assert "summary" in result
    assert (
        result["summary"]
        == "Important notes: The first important note is about the first point. The second important note is about the second point."
    )
