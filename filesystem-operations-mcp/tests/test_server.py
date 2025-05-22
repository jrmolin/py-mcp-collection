import os
import shutil
from pathlib import Path

import pytest
from syrupy import SnapshotAssertion
from syrupy.extensions.json import JSONSnapshotExtension

from filesystem_operations_mcp.filesystem.models import (
    FileEntry,
    FileEntryChunk,
    FileEntryContent,
    FileEntryPreview,
    FlatDirectoryResult,
    SummaryDirectoryEntry,
)
from filesystem_operations_mcp.filesystem.server import FilesystemServer, FilesystemServerOutsideRootError


@pytest.fixture
def configured_snapshot(snapshot: SnapshotAssertion):
    return snapshot(extension_class=JSONSnapshotExtension)


@pytest.fixture
async def test_dir():
    root = Path(__file__).parent / "temp_dir"
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True, exist_ok=True)
    os.chdir(root)
    try:
        yield root
    finally:
        shutil.rmtree(root)


@pytest.fixture
async def setup_test_dir(test_dir: Path):
    root = Path(test_dir)
    (root / "a.txt").write_text("hello world")
    (root / "b.md").write_text("markdown content")
    (root / "large.txt").write_text("a" * 10000)
    (root / "empty_dir").mkdir()
    (root / "file_with_many_lines.txt").write_text("one\ntwo\nthree\nfour\nfive\nsix\nseven\neight\nnine\nten\n")
    sub = root / "subdir"
    sub.mkdir()
    (sub / "c.py").write_text("print('hi')")
    return root


def test_security(setup_test_dir: Path):
    fs = FilesystemServer(setup_test_dir)

    outside_root = Path("/etc")

    with pytest.raises(FilesystemServerOutsideRootError):
        fs.flat_dir(FileEntry, [outside_root])

    # cwd is a level higher than the root
    cwd_file = Path("../a.txt")

    with pytest.raises(FilesystemServerOutsideRootError):
        fs.read_file(cwd_file)


def test_security_non_intrusive(setup_test_dir: Path):
    fs = FilesystemServer(setup_test_dir)

    os.chdir(setup_test_dir)

    inside_root = Path("a.txt")

    result = fs.read_file(inside_root)

    assert "hello world" in result


def test_flat_walk(configured_snapshot: SnapshotAssertion, setup_test_dir: Path):
    fs = FilesystemServer(setup_test_dir)

    relative_root = Path()

    result = fs.flat_dir(FileEntry, recurse=True)

    assert isinstance(result, FlatDirectoryResult)

    assert str(relative_root) in result.root
    assert "./subdir" in result.root

    for entries in result.root.values():
        for entry in entries.values():
            assert isinstance(entry, FileEntry | SummaryDirectoryEntry)

    assert result.model_dump() == configured_snapshot


def test_flat_list(configured_snapshot: SnapshotAssertion, setup_test_dir: Path):
    fs = FilesystemServer(setup_test_dir)

    relative_root = Path()

    result = fs.flat_dir(FileEntry, recurse=False)

    assert isinstance(result, FlatDirectoryResult)

    assert str(relative_root) in result.root

    for entries in result.root.values():
        for entry in entries.values():
            assert isinstance(entry, FileEntry | SummaryDirectoryEntry)

    assert result.model_dump() == configured_snapshot


def test_flat_walk_preview(configured_snapshot: SnapshotAssertion, setup_test_dir: Path):
    fs = FilesystemServer(setup_test_dir)

    relative_root = Path()

    result = fs.flat_dir(FileEntryPreview, recurse=True)

    assert isinstance(result, FlatDirectoryResult)

    assert str(relative_root) in result.root
    assert "./subdir" in result.root

    for entries in result.root.values():
        for entry in entries.values():
            assert isinstance(entry, FileEntryPreview | SummaryDirectoryEntry)

    assert result.model_dump(exclude_none=True) == configured_snapshot


def test_flat_walk_content(configured_snapshot: SnapshotAssertion, setup_test_dir: Path):
    fs = FilesystemServer(setup_test_dir)

    relative_root = Path()

    result = fs.flat_dir(FileEntryContent, recurse=True)

    assert isinstance(result, FlatDirectoryResult)

    assert str(relative_root) in result.root
    assert "./subdir" in result.root

    for entries in result.root.values():
        for entry in entries.values():
            assert isinstance(entry, FileEntryContent | SummaryDirectoryEntry)

    assert result.model_dump() == configured_snapshot


def test_file_exists(setup_test_dir: Path):
    fs = FilesystemServer(setup_test_dir)
    file_path = setup_test_dir / "a.txt"
    assert fs.file_exists(file_path)
    assert not fs.file_exists(setup_test_dir / "does_not_exist.txt")


def test_delete_file(setup_test_dir: Path):
    fs = FilesystemServer(setup_test_dir)
    file_path = setup_test_dir / "a.txt"
    assert file_path.exists()
    fs.delete_file(file_path)
    assert not file_path.exists()


def test_create_and_read_file(setup_test_dir: Path):
    fs = FilesystemServer(setup_test_dir)
    file_path = setup_test_dir / "new.txt"
    content = "new file content"
    fs.create_file(file_path, content)
    assert file_path.exists()
    read_content = fs.read_file(file_path)
    assert read_content == content


def test_append_file(setup_test_dir: Path):
    fs = FilesystemServer(setup_test_dir)
    file_path = setup_test_dir / "append.txt"
    fs.create_file(file_path, "first line\n")
    fs.append_file(file_path, "second line\n")
    read_content = fs.read_file(file_path)
    assert read_content == "first line\nsecond line\n"


def test_dir_exists(setup_test_dir: Path):
    fs = FilesystemServer(setup_test_dir)
    dir_path = setup_test_dir / "subdir"
    assert fs.dir_exists(dir_path)
    assert not fs.dir_exists(setup_test_dir / "does_not_exist_dir")


def test_preview_file(setup_test_dir: Path):
    fs = FilesystemServer(setup_test_dir)
    file_path = setup_test_dir / "large.txt"
    preview = fs.preview_file(file_path)
    assert isinstance(preview, str)
    assert len(preview) > 0
    assert preview == file_path.read_text()[:400] + "..."


def test_get_dir(setup_test_dir: Path):
    fs = FilesystemServer(setup_test_dir)

    dir_path = setup_test_dir / "."

    dir_result = fs.get_dir(dir_path)

    assert isinstance(dir_result, FlatDirectoryResult)
    # Should contain the root directory
    assert "." in dir_result.root
    # Should contain FileEntry objects for files in root
    for entry in dir_result.root["."].values():
        assert isinstance(entry, FileEntry | SummaryDirectoryEntry)


def test_find_in_file_plain(setup_test_dir: Path):
    fs = FilesystemServer(setup_test_dir)
    file_path = setup_test_dir / "file_with_many_lines.txt"
    file_entry = FileEntry(absolute_path=file_path, root=setup_test_dir)

    result = fs._find_in_file(file_entry, "four")
    assert result is not None
    assert len(result.chunks) == 1
    assert result.chunks[0].match.strip() == "four"
    assert result.chunks[0].match_line_number == 4
    assert result.chunks[0].before == ["one", "two", "three"]
    assert result.chunks[0].after == ["five", "six", "seven"]

    result = fs._find_in_file(file_entry, "four", before=0, after=0)
    assert result is not None
    assert len(result.chunks) == 1
    assert result.chunks[0].match.strip() == "four"
    assert result.chunks[0].match_line_number == 4
    assert result.chunks[0].before == []
    assert result.chunks[0].after == []

    # no results plain
    result_none = fs._find_in_file(file_entry, "notfound")
    assert result_none is None


def test_find_in_file_regex(setup_test_dir: Path):
    fs = FilesystemServer(setup_test_dir)
    file_path = setup_test_dir / "file_with_many_lines.txt"
    file_entry = FileEntry(absolute_path=file_path, root=setup_test_dir)

    result_regex = fs._find_in_file(file_entry, r"se.en", search_is_regex=True)
    assert result_regex is not None
    assert len(result_regex.chunks) == 1
    assert result_regex.chunks[0].match.strip() == "seven"
    assert result_regex.chunks[0].match_line_number == 7
    assert result_regex.chunks[0].before == ["four", "five", "six"]
    assert result_regex.chunks[0].after == ["eight", "nine", "ten"]

    # no results regex
    result_none = fs._find_in_file(file_entry, r"notfound", search_is_regex=True)
    assert result_none is None


def test_search_dir_include_exclude(setup_test_dir: Path):
    fs = FilesystemServer(setup_test_dir)

    os.chdir(setup_test_dir)
    # Only include .md files (should find 'markdown content')
    results = fs.search_content([Path()], recurse=True, search="markdown", include=["*.md"])
    for directory in results.root.values():
        for file in directory.values():
            if isinstance(file, SummaryDirectoryEntry):
                continue

            chunks: list[FileEntryChunk] = file.chunks
            assert any("markdown content" in chunk.match for chunk in chunks)
    # Exclude .md files (should not find 'markdown content')

    results_exclude = fs.search_content([Path()], recurse=True, search="markdown", exclude=["*.md"])
    for directory in results_exclude.root.values():
        for file in directory.values():
            if isinstance(file, SummaryDirectoryEntry):
                continue

            chunks: list[FileEntryChunk] = file.chunks
            assert not any("markdown content" in chunk.match for chunk in chunks)
