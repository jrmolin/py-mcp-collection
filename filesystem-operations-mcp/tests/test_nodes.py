import tempfile
from pathlib import Path

import pytest
from aiofiles import open as aopen

from filesystem_operations_mcp.filesystem.errors import FilesystemServerOutsideRootError
from filesystem_operations_mcp.filesystem.nodes.base import BaseNode
from filesystem_operations_mcp.filesystem.nodes.directory import DirectoryEntry
from filesystem_operations_mcp.filesystem.nodes.file import FileEntry


# Helper function to create test files
async def create_test_file(path: Path, content: str) -> None:
    async with aopen(path, "w") as f:
        await f.write(content)


# Helper function to create test directory structure
async def create_test_structure(root: Path) -> None:
    # Create some text files
    await create_test_file(root / "test.txt", "Hello, World!")
    await create_test_file(root / "code.py", "def hello():\n    print('Hello, World!')")
    await create_test_file(root / "data.json", '{"key": "value"}')

    # Create a subdirectory with files
    subdir = root / "subdir"
    subdir.mkdir()
    await create_test_file(subdir / "nested.txt", "Nested content")
    await create_test_file(subdir / "script.sh", "#!/bin/bash\necho 'Hello'")

    # Create a hidden file
    await create_test_file(root / ".hidden", "Hidden content")


@pytest.fixture
async def temp_dir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        root = Path(tmpdirname)
        await create_test_structure(root)
        yield root


@pytest.mark.asyncio
async def test_base_node_properties(temp_dir: Path):
    node = BaseNode(absolute_path=temp_dir, root=temp_dir)

    assert node.name == temp_dir.name
    assert node.relative_path == Path()
    assert node.is_dir
    assert not node.is_file

    # Test filters
    assert node.passes_filters()
    assert node.passes_filters(skip_hidden=True)
    assert node.passes_filters(includes=["*"])  # Include everything
    assert not node.passes_filters(excludes=["*"])  # Exclude everything


@pytest.mark.asyncio
async def test_file_entry_properties(temp_dir: Path):
    file_path = temp_dir / "test.txt"
    node = FileEntry(absolute_path=file_path, root=temp_dir)

    assert node.name == "test.txt"
    assert node.stem == "test"
    assert node.extension == ".txt"
    assert node.file_path == "test.txt"
    assert node.is_text
    assert not node.is_binary
    assert not node.is_code
    assert not node.is_data

    # Test file reading
    content = await node.read_text()
    assert content == "Hello, World!"

    # Test binary reading
    binary = await node.read_binary_base64()
    assert isinstance(binary, str)  # Should be base64 encoded

    # Test line reading
    lines = await node.read_lines()
    assert len(lines.lines()) == 1
    assert lines.lines()[0] == "Hello, World!"

    # Test line numbers
    line_numbers = await node.read_lines()
    assert len(line_numbers.lines()) == 1
    assert line_numbers.line_numbers()[0] == 0
    assert line_numbers.lines()[0] == "Hello, World!"


@pytest.mark.asyncio
async def test_directory_entry_properties(temp_dir: Path):
    node = DirectoryEntry(absolute_path=temp_dir, root=temp_dir)

    assert node.name == temp_dir.name
    assert node.directory_path == "."

    # Test children
    children = await node.children()
    assert len(children) == 4  # test.txt, code.py, data.json, subdir

    # Test finding files
    txt_files = await node.find_files("*.txt")
    assert len(txt_files) == 2
    assert txt_files[0].name == "test.txt"
    assert txt_files[1].name == "nested.txt"

    # Test finding directories
    dirs = await node.find_dirs("*")
    assert len(dirs) == 1
    assert dirs[0].name == "subdir"

    # Test recursive children
    all_children = await node._children(depth=1)
    assert len(all_children) == 6  # 4 in root + 2 in subdir


@pytest.mark.asyncio
async def test_file_content_matching(temp_dir: Path):
    file_path = temp_dir / "code.py"
    node = FileEntry(absolute_path=file_path, root=temp_dir)

    # Test simple content matching
    matches = await node.contents_match("print")
    assert len(matches) == 1
    assert "print" in matches[0].match.lines()[0]

    # Test simple content matching
    matches = await node.contents_match("print", before=1)
    assert len(matches) == 1
    assert "print" in matches[0].match.lines()[0]
    assert "hello" in matches[0].before.lines()[0]

    # Test regex matching
    matches = await node.contents_match_regex(r"def \w+")
    assert len(matches) == 1
    assert "def hello" in matches[0].match.lines()[0]

    # Test context lines
    matches = await node.contents_match("print", before=1, after=0)
    assert len(matches) == 1
    assert len(matches[0].before.lines()) == 1
    assert "def hello" in matches[0].before.lines()[0]


@pytest.mark.asyncio
async def test_file_type_detection(temp_dir):
    # Test text file
    txt_node = FileEntry(absolute_path=temp_dir / "test.txt", root=temp_dir)
    assert txt_node.is_text
    assert not txt_node.is_binary
    assert not txt_node.is_code

    # Test code file
    py_node = FileEntry(absolute_path=temp_dir / "code.py", root=temp_dir)
    assert py_node.is_code
    assert not py_node.is_binary

    # Test data file
    json_node = FileEntry(absolute_path=temp_dir / "data.json", root=temp_dir)
    assert json_node.is_data
    assert not json_node.is_binary


@pytest.mark.asyncio
async def test_path_validation(temp_dir: Path):
    # Test valid path
    node = FileEntry(absolute_path=temp_dir / "test.txt", root=temp_dir)
    node.validate_in_root(temp_dir)

    # Test invalid path
    outside_path = Path("/tmp/outside")  # noqa: S108 # Insecure temporary directory

    node = FileEntry(absolute_path=outside_path, root=temp_dir)

    with pytest.raises(FilesystemServerOutsideRootError):
        node.validate_in_root(temp_dir)


@pytest.mark.asyncio
async def test_hidden_files(temp_dir: Path):
    # Test hidden file
    hidden_node = FileEntry(absolute_path=temp_dir / ".hidden", root=temp_dir)
    assert not hidden_node.passes_filters(skip_hidden=True)
    assert hidden_node.passes_filters(skip_hidden=False)

    # Test hidden directory
    hidden_dir = temp_dir / ".hidden_dir"
    hidden_dir.mkdir()
    dir_node = DirectoryEntry(absolute_path=hidden_dir, root=temp_dir)
    assert not dir_node.passes_filters(skip_hidden=True)
    assert dir_node.passes_filters(skip_hidden=False)
