from pathlib import Path
from textwrap import dedent

import pytest
from aiofiles import tempfile

from filesystem_operations_mcp.filesystem.file_system import FileSystem
from filesystem_operations_mcp.filesystem.nodes import FileEntry
from filesystem_operations_mcp.filesystem.view import FileExportableField
from tests.conftest import create_test_structure


@pytest.fixture
async def temp_dir():
    async with tempfile.TemporaryDirectory() as tmpdirname:
        root = Path(tmpdirname)
        await create_test_structure(root)
        yield root


@pytest.fixture
def file_system(temp_dir: Path):
    return FileSystem(path=temp_dir)


@pytest.mark.asyncio
async def test_file_field_selection_default_fields(file_system: FileSystem):
    node = file_system.get_file("test_with_hello_world.txt")
    file_fields = FileExportableField()
    result, _ = file_fields.apply(node)
    # Default fields: file_path, file_type, size
    assert "relative_path_str" in result
    assert result.get("relative_path_str") == "test_with_hello_world.txt"
    assert "type" in result
    assert isinstance(result["type"], str) or result["type"] is None
    assert "size" in result
    assert isinstance(result["size"], int)
    # Non-default fields should not be present
    assert "basename" not in result
    assert "extension" not in result
    assert "read_text" not in result


@pytest.mark.asyncio
async def test_file_field_selection_toggle_fields(file_system: FileSystem):
    node = file_system.get_file("code_with_hello_world.py")
    file_fields = FileExportableField(
        basename=True, extension=True, created_at=True, modified_at=True, owner=True, group=True, mime_type=True
    )
    result, _ = file_fields.apply(node)
    assert result["stem"] == "code_with_hello_world"
    assert result["extension"] == ".py"
    assert "created_at" in result
    assert "modified_at" in result
    assert "owner" in result
    assert "group" in result
    assert "mime_type" in result


@pytest.mark.asyncio
async def test_file_field_selection_preview(file_system: FileSystem):
    node = file_system.get_file("test_with_hello_world.txt")
    file_fields = FileExportableField(preview="long")
    # result, _ = file_fields.apply(node)
    expensive_fields = await file_fields.aapply(node)
    assert "preview" in expensive_fields
    assert expensive_fields["preview"][1] == "Hello, World!"


@pytest.mark.asyncio
async def test_file_field_selection_summarize(file_system: FileSystem):
    _ = await file_system.create_file(
        file_system.path / "test_notes.md",
        ["# Important notes: The first important note is about the first point. The second important note is about the second point."],
    )
    node = file_system.get_file("test_notes.md")
    file_fields = FileExportableField(summarize=True)
    result = await file_fields.aapply(node)
    assert "summary" in result
    assert (
        result["summary"]
        == "Important notes: The first important note is about the first point. The second important note is about the second point."
    )


@pytest.mark.asyncio
async def test_file_field_selection_binary_file(file_system: FileSystem, temp_dir: Path):
    """Test handling of binary files in the materializer."""
    # Create a binary file
    binary_path = temp_dir / "binary.bin"
    binary_path.write_bytes(b"\x00\x01\x02\x03")

    node = FileEntry(path=binary_path, filesystem=file_system)
    file_fields = FileExportableField(basename=True, extension=True, type=True, size=True, mime_type=True)

    result, _ = file_fields.apply(node)

    # Verify binary file properties
    assert result["stem"] == "binary"
    assert result["extension"] == ".bin"
    assert result["type"] == "binary"
    assert result["size"] == 4
    assert result["mime_type"].startswith("application/") or result["mime_type"] == "unknown"


@pytest.mark.asyncio
async def test_file_field_selection_code_file(file_system: FileSystem):
    """Test handling of code files with summarization."""
    # Create a Python code file
    code_content = dedent(
        text='''
        """A test code file."""

        def hello_world():
            """A simple hello world function."""

            print('Hello, World!')

        class TestClass:
            """A test class for demonstration."""
            def __init__(self):
                self.value = 42
            def get_value(self):
                return self.value
        '''
    ).strip()

    await file_system.create_file(file_system.path / "test_code.py", code_content.splitlines())

    node = file_system.get_file("test_code.py")
    file_fields = FileExportableField(summarize=True, preview="long", type=True, extension=True)

    result = file_fields.apply(node)[0]
    async_result = await file_fields.aapply(node)

    # Verify code file properties
    assert result["type"] == "code"
    assert result["extension"] == ".py"
    assert "preview" in async_result
    assert "summary" in async_result

    # Verify preview content
    preview = async_result["preview"]
    assert preview[3] == "def hello_world():"
    assert preview[4] == '    """A simple hello world function."""'
    assert preview[6] == "    print('Hello, World!')"

    assert async_result["summary"] == {
        "class_definition": [{"function_definition": ["__init__", "get_value"], "identifier": "TestClass"}],
        "function_definition": ["hello_world"],
        "identifier": "module",
    }


@pytest.mark.asyncio
async def test_file_field_selection_json_file(file_system: FileSystem):
    """Test that we correctly identify the type and mime type of a JSON file"""
    node = file_system.get_file("data.json")

    file_fields = FileExportableField(type=True, extension=True, size=True, mime_type=True)

    result, _ = file_fields.apply(node)

    assert result["type"] == "data"
    assert result["extension"] == ".json"
    assert result["mime_type"] == "application/json"


@pytest.mark.asyncio
async def test_file_field_selection_preview_limits(file_system: FileSystem):
    """Test that `short` and `long` preview limits are respected."""
    # Create a file with 100 lines
    many_lines = [f"Line {i}" for i in range(1, 101)]

    await file_system.create_file(file_system.path / "many_lines.txt", many_lines)

    node = file_system.get_file("many_lines.txt")

    # Test short preview (should be 5 lines)
    file_fields_short = FileExportableField(preview="short")
    result_short = await file_fields_short.aapply(node)

    assert "preview" in result_short
    preview_short = result_short["preview"]
    assert isinstance(preview_short, dict)
    assert len(preview_short.keys()) == 5
    assert preview_short[1] == "Line 1"
    assert preview_short[5] == "Line 5"

    # Test long preview (should be 50 lines)
    file_fields_long = FileExportableField(preview="long")
    result_long = await file_fields_long.aapply(node)

    assert "preview" in result_long
    preview_long = result_long["preview"]
    assert len(preview_long.keys()) == 50
    assert preview_long[1] == "Line 1"
    assert preview_long[50] == "Line 50"


@pytest.mark.asyncio
async def test_file_field_selection_summary_limits(file_system: FileSystem):
    """Test that summaries respect the configured byte limits."""
    # Create a very long text file
    long_content = [
        "This is a very long line that contains a lot of text. " * 50,  # ~3000 characters
        "Another very long line with lots of content. " * 50,  # ~3000 characters
        "Yet another long line to test summary limits. " * 50,  # ~3000 characters
    ]

    await file_system.create_file(file_system.path / "very_long.txt", long_content)

    node = file_system.get_file("very_long.txt")
    file_fields = FileExportableField(summarize=True)

    result = await file_fields.aapply(node)

    assert "summary" in result
    summary = result["summary"]

    # The summary should be truncated to MAX_SUMMARY_BYTES (1000 bytes)
    assert len(summary.encode("utf-8")) <= 1000


@pytest.mark.asyncio
async def test_file_field_selection_markdown_summarization(file_system: FileSystem):
    """Test markdown-specific summarization."""
    markdown_content = [
        "# Main Title",
        "",
        "This is a paragraph with some **bold text** and *italic text*.",
        "",
        "## Subsection",
        "",
        "Here's a list:",
        "- Item 1",
        "- Item 2",
        "- Item 3",
        "",
        "And a [link](https://example.com) to test.",
    ]

    await file_system.create_file(file_system.path / "test_markdown.md", markdown_content)

    node = file_system.get_file("test_markdown.md")
    file_fields = FileExportableField(summarize=True)

    result = await file_fields.aapply(node)

    # Verify markdown summarization
    assert "summary" in result
    summary = result["summary"]

    # The summary should process the markdown content
    assert len(summary) > 0


@pytest.mark.asyncio
async def test_file_field_selection_asciidoc_summarization(file_system: FileSystem):
    """Test asciidoc-specific summarization."""
    asciidoc_content = [
        "= Document Title",
        "",
        "This is an asciidoc document with some content.",
        "",
        "== Section",
        "",
        "Here's some text that should be summarized.",
        "",
        "http://example.com should be excluded from summary",
        "",
        "More meaningful content here.",
    ]

    await file_system.create_file(file_system.path / "test.asciidoc", asciidoc_content)

    node = file_system.get_file("test.asciidoc")
    file_fields = FileExportableField(summarize=True)

    result = await file_fields.aapply(node)

    # Verify asciidoc summarization
    assert "summary" in result
    summary = result["summary"]

    # The summary should process the asciidoc content
    assert len(summary) > 0


@pytest.mark.asyncio
async def test_file_field_selection_error_handling(file_system: FileSystem):
    """Test error handling in the materializer."""
    # Create a file that might cause issues during summarization
    problematic_content = [
        "Normal line 1",
        "Normal line 2",
        # Add some content that might cause issues
        "Line with special chars: \x00\x01\x02",  # Binary-like content
        "Normal line 4",
    ]

    await file_system.create_file(file_system.path / "problematic.txt", problematic_content)

    node = file_system.get_file("problematic.txt")
    file_fields = FileExportableField(summarize=True, preview="long")

    # This should not crash, even with problematic content
    result = file_fields.apply(node)[0]
    async_result = await file_fields.aapply(node)

    # Should still get basic file information
    assert "type" in result
    assert result["type"] == "text"

    # Preview should still work
    assert "preview" in async_result
    assert isinstance(async_result["preview"], dict)
    assert len(async_result["preview"].keys()) > 0


@pytest.mark.asyncio
async def test_file_field_selection_combined_features(file_system: FileSystem):
    """Test combining multiple features together."""
    # Create a comprehensive test file
    comprehensive_content = [
        "# Comprehensive Test",
        "",
        "This file tests multiple features:",
        "",
        "1. **Bold text** for emphasis",
        "2. *Italic text* for variety",
        "3. `Code snippets` for examples",
        "",
        "## Code Section",
        "```python",
        "def test_function():",
        "    return 'Hello, World!'",
        "```",
        "",
        "## Data Section",
        "- Item A",
        "- Item B",
        "- Item C",
    ]

    await file_system.create_file(file_system.path / "comprehensive.md", comprehensive_content)

    node = file_system.get_file("comprehensive.md")
    file_fields = FileExportableField(
        basename=True, extension=True, type=True, size=True, preview="long", summarize=True, created_at=True, modified_at=True
    )

    result = file_fields.apply(node)[0]
    async_result = await file_fields.aapply(node)

    # Verify all requested fields are present
    assert result["stem"] == "comprehensive"
    assert result["extension"] == ".md"
    assert result["type"] == "text"
    assert "size" in result
    assert "preview" in async_result
    assert "summary" in async_result
    assert "created_at" in result
    assert "modified_at" in result

    # Verify preview content
    preview = async_result["preview"]
    assert isinstance(preview, dict)
    assert len(preview.keys()) == 18  # Long preview
    assert preview[1] == "# Comprehensive Test"

    # Verify summary
    assert "summary" in async_result
    assert len(async_result["summary"]) > 0
