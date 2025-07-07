import tempfile
from pathlib import Path

import pytest
from aiofiles import open as aopen

from filesystem_operations_mcp.filesystem.errors import FilePatchDoesNotMatchError, FilePatchIndexError
from filesystem_operations_mcp.filesystem.file_system import FileSystem
from filesystem_operations_mcp.filesystem.nodes import FileEntry
from filesystem_operations_mcp.filesystem.patches.file import (
    FileAppendPatch,
    FileDeletePatch,
    FileInsertPatch,
    FileMultiplePatchTypes,
    FilePatchTypes,
    FileReplacePatch,
)

# Test data
SAMPLE_LINES = [
    "Line 1",
    "Line 2",
    "Line 3",
    "Line 4",
    "Line 5",
]


@pytest.mark.parametrize(
    ("patch", "expected_lines"),
    [
        # Test inserting at the beginning
        (
            FileInsertPatch(line_number=1, current_line="Line 1", lines=["New Line 1", "New Line 2"]),
            ["New Line 1", "New Line 2", *SAMPLE_LINES],
        ),
        # Test inserting in the middle
        (
            FileInsertPatch(line_number=3, current_line="Line 3", lines=["New Line 3"]),
            ["Line 1", "Line 2", "New Line 3", "Line 3", "Line 4", "Line 5"],
        ),
    ],
    ids=["insert_at_beginning", "insert_in_middle"],
)
def test_insert_patch(patch: FileInsertPatch, expected_lines: list[str]):
    result = patch.apply(SAMPLE_LINES)
    assert result == expected_lines


@pytest.mark.parametrize(
    ("patch", "expected_lines"),
    [
        # Test appending single line
        (
            FileAppendPatch(lines=["New Line 1"]),
            [*SAMPLE_LINES, "New Line 1"],
        ),
        # Test appending multiple lines
        (
            FileAppendPatch(lines=["New Line 1", "New Line 2"]),
            [*SAMPLE_LINES, "New Line 1", "New Line 2"],
        ),
    ],
    ids=["append_single_line", "append_multiple_lines"],
)
def test_append_patch(patch: FileAppendPatch, expected_lines: list[str]):
    result = patch.apply(SAMPLE_LINES)
    assert result == expected_lines


def test_file_append_patch_empty_file():
    result = FileAppendPatch(lines=["New Line 1"]).apply([])
    assert result == ["New Line 1"]


@pytest.mark.parametrize(
    ("patch", "expected_lines"),
    [
        (
            FileDeletePatch(line_numbers=[1]),
            ["Line 2", "Line 3", "Line 4", "Line 5"],
        ),
        (
            FileDeletePatch(line_numbers=[2, 4]),
            ["Line 1", "Line 3", "Line 5"],
        ),
        (
            FileDeletePatch(line_numbers=[1, 3, 5]),
            ["Line 2", "Line 4"],
        ),
    ],
    ids=["delete_single_line", "delete_multiple_lines", "delete_non_consecutive_lines"],
)
def test_delete_patch(patch: FileDeletePatch, expected_lines: list[str]):
    result = patch.apply(SAMPLE_LINES)
    assert result == expected_lines


@pytest.mark.parametrize(
    ("patch", "expected_lines"),
    [
        (
            FileReplacePatch(
                start_line_number=1,
                current_lines=["Line 1"],
                new_lines=["New Line 1"],
            ),
            ["New Line 1", "Line 2", "Line 3", "Line 4", "Line 5"],
        ),
        (
            FileReplacePatch(
                start_line_number=2,
                current_lines=["Line 2", "Line 3"],
                new_lines=["New Line 2", "New Line 3"],
            ),
            ["Line 1", "New Line 2", "New Line 3", "Line 4", "Line 5"],
        ),
        (
            FileReplacePatch(
                start_line_number=3,
                current_lines=["Line 3"],
                new_lines=["New Line 3", "New Line 4"],
            ),
            ["Line 1", "Line 2", "New Line 3", "New Line 4", "Line 4", "Line 5"],
        ),
        (
            FileReplacePatch(
                start_line_number=3,
                current_lines=["Line 3", "Line 4"],
                new_lines=["New Line 3", "New Line 4"],
            ),
            ["Line 1", "Line 2", "New Line 3", "New Line 4", "Line 5"],
        ),
    ],
    ids=[
        "replace_single_line",
        "replace_multiple_lines_same_number",
        "replace_lines_different_number",
        "replace_multiple_lines_different_number",
    ],
)
def test_replace_patch(patch: FileReplacePatch, expected_lines: list[str]):
    result = patch.apply(SAMPLE_LINES)
    assert result == expected_lines


def test_file_replace_patch_mismatch():
    patch = FileReplacePatch(
        start_line_number=1,
        current_lines=["Wrong Line"],
        new_lines=["New Line"],
    )
    with pytest.raises(FilePatchDoesNotMatchError):
        _ = patch.apply(SAMPLE_LINES)


def test_edge_cases():
    # Test empty file
    empty_lines: list[str] = []

    # Append to empty file
    append_patch = FileAppendPatch(lines=["New Line"])
    assert append_patch.apply(empty_lines) == ["New Line"]


def test_invalid_operations():
    # Test inserting at invalid line number
    with pytest.raises(FilePatchIndexError):
        _ = FileInsertPatch(line_number=10, current_line="Something that doesn't match", lines=["New Line"]).apply(SAMPLE_LINES)

    # Test deleting invalid line number
    with pytest.raises(FilePatchIndexError):
        _ = FileDeletePatch(line_numbers=[10]).apply(SAMPLE_LINES)

    # Test replacing with invalid line number
    with pytest.raises(FilePatchIndexError):
        _ = FileReplacePatch(
            start_line_number=10,
            current_lines=["Line"],
            new_lines=["New Line"],
        ).apply(SAMPLE_LINES)


@pytest.fixture
async def temp_dir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield Path(tmpdirname)


@pytest.fixture
async def file_system(temp_dir: Path):
    return FileSystem(path=temp_dir)


@pytest.fixture
async def temp_file(temp_dir: Path):
    file_path = temp_dir / "test_file.txt"
    async with aopen(file_path, "w") as f:
        _ = await f.write("\n".join(SAMPLE_LINES))
    return file_path


@pytest.mark.parametrize(
    ("patch", "expected_lines"),
    [
        (
            FileDeletePatch(line_numbers=[3, 5]),
            ["Line 1", "Line 2", "Line 4"],
        ),
        (
            FileInsertPatch(line_number=1, current_line="Line 1", lines=["New Line 1"]),
            ["New Line 1", *SAMPLE_LINES],
        ),
        (
            FileReplacePatch(start_line_number=2, current_lines=["Line 2"], new_lines=["New Line 2"]),
            ["Line 1", "New Line 2", "Line 3", "Line 4", "Line 5"],
        ),
        (
            FileAppendPatch(lines=["New Line 1"]),
            [*SAMPLE_LINES, "New Line 1"],
        ),
    ],
    ids=["single_delete_patch", "single_insert_patch", "single_replace_patch", "single_append_patch"],
)
async def test_file_entry_apply_single_patches(file_system: FileSystem, temp_file: Path, patch: FilePatchTypes, expected_lines: list[str]):
    file_entry = FileEntry(path=temp_file, filesystem=file_system)

    await file_entry.apply_patch(patch=patch)

    # Read the file and verify changes
    async with aopen(temp_file) as f:
        lines = await f.readlines()
        lines = [line.rstrip() for line in lines]

    assert lines == expected_lines


@pytest.mark.parametrize(
    ("patches", "expected_lines"),
    [
        (
            [
                FileInsertPatch(line_number=1, current_line="Line 1", lines=["Added Line 1"]),
                FileInsertPatch(line_number=2, current_line="Line 2", lines=["Added Line 2"]),
                FileInsertPatch(line_number=3, current_line="Line 3", lines=["Added Line 3"]),
            ],
            ["Added Line 1", "Line 1", "Added Line 2", "Line 2", "Added Line 3", "Line 3", "Line 4", "Line 5"],
        ),
        (
            [
                FileInsertPatch(line_number=1, current_line="Line 1", lines=["Added Line 1", "Added Line 2", "Added Line 3"]),
                FileInsertPatch(line_number=3, current_line="Line 3", lines=["Added Line 4", "Added Line 5", "Added Line 6"]),
            ],
            [
                "Added Line 1",
                "Added Line 2",
                "Added Line 3",
                "Line 1",
                "Line 2",
                "Added Line 4",
                "Added Line 5",
                "Added Line 6",
                "Line 3",
                "Line 4",
                "Line 5",
            ],
        ),
        (
            [
                FileReplacePatch(start_line_number=3, current_lines=["Line 3"], new_lines=["Replaced Line 3"]),
                FileReplacePatch(start_line_number=4, current_lines=["Line 4"], new_lines=["Replaced Line 4"]),
            ],
            ["Line 1", "Line 2", "Replaced Line 3", "Replaced Line 4", "Line 5"],
        ),
        (
            [
                FileReplacePatch(start_line_number=3, current_lines=["Line 3", "Line 4"], new_lines=["Replaced Line 3", "Replaced Line 4"]),
                FileReplacePatch(start_line_number=5, current_lines=["Line 5"], new_lines=["Replaced Line 5"]),
            ],
            ["Line 1", "Line 2", "Replaced Line 3", "Replaced Line 4", "Replaced Line 5"],
        ),
    ],
    ids=["multiple_insert_patch", "multiple_insert_multiline_patch", "multiple_replace_patch", "multiple_replace_multiline_patch"],
)
async def test_file_entry_apply_multiple_patches(
    file_system: FileSystem, temp_file: Path, patches: FileMultiplePatchTypes, expected_lines: list[str]
):
    file_entry = FileEntry(path=temp_file, filesystem=file_system)

    await file_entry.apply_patches(patches=patches)

    # Read the file and verify changes
    async with aopen(temp_file) as f:
        lines = await f.readlines()
        lines = [line.rstrip() for line in lines]

    assert lines == expected_lines


@pytest.mark.asyncio
async def test_file_entry_apply_patches_empty_file(file_system: FileSystem):
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        pass

    file_entry = FileEntry(path=Path(f.name), filesystem=file_system)

    # Test applying patches to empty file
    patch = FileAppendPatch(lines=["Last Line"])

    await file_entry.apply_patch(patch=patch)

    # Read the file and verify changes
    async with aopen(f.name) as f:
        content = await f.read()
        lines = content.splitlines()

    assert lines == ["Last Line"]


@pytest.mark.asyncio
async def test_file_entry_apply_patches_error_handling(file_system: FileSystem, temp_file: Path):
    file_entry = FileEntry(path=temp_file, filesystem=file_system)

    # Test invalid line number
    with pytest.raises(FilePatchIndexError):
        await file_entry.apply_patches(
            [
                FileInsertPatch(line_number=10, current_line="Something that doesn't match", lines=["Invalid"]),
            ]
        )

    # Test replace patch mismatch
    with pytest.raises(FilePatchDoesNotMatchError):
        await file_entry.apply_patches(
            [
                FileReplacePatch(
                    start_line_number=1,
                    current_lines=["Wrong Line"],
                    new_lines=["New Line"],
                ),
            ]
        )

    # Verify file content is unchanged after errors
    async with aopen(temp_file) as f:
        content = await f.read()
        lines = content.splitlines()
    assert lines == SAMPLE_LINES
