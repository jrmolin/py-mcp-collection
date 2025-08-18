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


@pytest.fixture
async def temp_dir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield Path(tmpdirname)


@pytest.fixture
async def file_system(temp_dir: Path):
    return FileSystem(path=temp_dir)


@pytest.mark.parametrize(
    ("patch", "expected_lines"),
    [
        # Test inserting at the beginning
        (
            FileInsertPatch(
                start_line_number=1, current_line="Line 1", before_or_after="before", insert_lines=["New Line 1", "New Line 2"]
            ),
            ["New Line 1", "New Line 2", *SAMPLE_LINES],
        ),
        # Test inserting in the middle
        (
            FileInsertPatch(start_line_number=3, current_line="Line 3", before_or_after="before", insert_lines=["New Line 3"]),
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
            FileReplacePatch(start_line_number=1, current_lines=["Line 1"], new_lines=["New Line 1"]),
            ["New Line 1", "Line 2", "Line 3", "Line 4", "Line 5"],
        ),
        (
            FileReplacePatch(start_line_number=2, current_lines=["Line 2", "Line 3"], new_lines=["New Line 2"]),
            ["Line 1", "New Line 2", "Line 4", "Line 5"],
        ),
        (
            FileReplacePatch(start_line_number=3, current_lines=["Line 3"], new_lines=["New Line 3", "Extra Line"]),
            ["Line 1", "Line 2", "New Line 3", "Extra Line", "Line 4", "Line 5"],
        ),
    ],
    ids=["replace_single_line", "replace_multiple_lines", "replace_with_more_lines"],
)
def test_replace_patch(patch: FileReplacePatch, expected_lines: list[str]):
    result = patch.apply(SAMPLE_LINES)
    assert result == expected_lines


# NEW TESTS FOR EDGE CASES AND ERROR SCENARIOS


def test_insert_patch_after_line():
    """Test inserting lines after a specific line."""
    patch = FileInsertPatch(start_line_number=2, current_line="Line 2", before_or_after="after", insert_lines=["Inserted Line"])
    result = patch.apply(SAMPLE_LINES)
    expected = ["Line 1", "Line 2", "Inserted Line", "Line 3", "Line 4", "Line 5"]
    assert result == expected


def test_insert_patch_at_end():
    """Test inserting lines at the end of the file."""
    patch = FileInsertPatch(start_line_number=5, current_line="Line 5", before_or_after="after", insert_lines=["End Line 1", "End Line 2"])
    result = patch.apply(SAMPLE_LINES)
    expected = ["Line 1", "Line 2", "Line 3", "Line 4", "Line 5", "End Line 1", "End Line 2"]
    assert result == expected


def test_delete_patch_all_lines():
    """Test deleting all lines from a file."""
    patch = FileDeletePatch(line_numbers=[1, 2, 3, 4, 5])
    result = patch.apply(SAMPLE_LINES)
    assert result == []


def test_delete_patch_empty_file():
    """Test deleting lines from an empty file."""
    patch = FileDeletePatch(line_numbers=[1])
    with pytest.raises(FilePatchIndexError):
        patch.apply([])


def test_replace_patch_all_lines():
    """Test replacing all lines in a file."""
    patch = FileReplacePatch(
        start_line_number=1, current_lines=["Line 1", "Line 2", "Line 3", "Line 4", "Line 5"], new_lines=["New Content"]
    )
    result = patch.apply(SAMPLE_LINES)
    assert result == ["New Content"]


def test_replace_patch_empty_replacement():
    """Test replacing lines with empty content."""
    patch = FileReplacePatch(start_line_number=2, current_lines=["Line 2", "Line 3"], new_lines=[])
    result = patch.apply(SAMPLE_LINES)
    assert result == ["Line 1", "Line 4", "Line 5"]


def test_patch_validation_line_numbers():
    """Test validation of line numbers."""
    # Test line number too low
    patch = FileDeletePatch(line_numbers=[0])
    with pytest.raises(FilePatchIndexError):
        patch.apply(SAMPLE_LINES)

    # Test line number too high
    patch = FileDeletePatch(line_numbers=[6])
    with pytest.raises(FilePatchIndexError):
        patch.apply(SAMPLE_LINES)


def test_patch_validation_content_mismatch():
    """Test validation of content matching."""
    # Test replace patch with wrong current content
    patch = FileReplacePatch(start_line_number=2, current_lines=["Wrong Line"], new_lines=["New Line"])
    with pytest.raises(FilePatchDoesNotMatchError):
        patch.apply(SAMPLE_LINES)

    # Test insert patch with wrong current line
    patch = FileInsertPatch(start_line_number=2, current_line="Wrong Line", before_or_after="before", insert_lines=["New Line"])
    with pytest.raises(FilePatchDoesNotMatchError):
        patch.apply(SAMPLE_LINES)


def test_patch_validation_insert_position():
    """Test validation of insert position."""
    # Test inserting at line 1
    patch = FileInsertPatch(start_line_number=1, current_line="Line 1", before_or_after="before", insert_lines=["New Line"])
    result = patch.apply(SAMPLE_LINES)
    expected = ["New Line", "Line 1", "Line 2", "Line 3", "Line 4", "Line 5"]
    assert result == expected


def test_patch_validation_replace_boundaries():
    """Test validation of replace boundaries."""
    # Test replacing at the end of the file
    patch = FileReplacePatch(start_line_number=4, current_lines=["Line 4", "Line 5"], new_lines=["New End"])
    result = patch.apply(SAMPLE_LINES)
    expected = ["Line 1", "Line 2", "Line 3", "New End"]
    assert result == expected


def test_patch_error_recovery():
    """Test that file content remains unchanged after patch errors."""
    original_lines = SAMPLE_LINES.copy()

    # Try to apply an invalid patch
    patch = FileReplacePatch(start_line_number=2, current_lines=["Wrong Content"], new_lines=["New Content"])

    with pytest.raises(FilePatchDoesNotMatchError):
        patch.apply(original_lines)

    # Verify original content is unchanged
    assert original_lines == SAMPLE_LINES


def test_patch_error_with_line_number_validation():
    """Test that line number validation errors don't modify content."""
    original_lines = SAMPLE_LINES.copy()

    # Try to apply a patch with invalid line numbers
    patch = FileDeletePatch(line_numbers=[10])

    with pytest.raises(FilePatchIndexError):
        patch.apply(original_lines)

    # Verify original content is unchanged
    assert original_lines == SAMPLE_LINES


# NEW TESTS FOR EDGE CASES


def test_patch_with_single_line_file():
    """Test patches on a file with only one line."""
    single_line = ["Single Line"]

    # Test insert before
    patch = FileInsertPatch(start_line_number=1, current_line="Single Line", before_or_after="before", insert_lines=["Before"])
    result = patch.apply(single_line)
    assert result == ["Before", "Single Line"]

    # Test insert after
    patch = FileInsertPatch(start_line_number=1, current_line="Single Line", before_or_after="after", insert_lines=["After"])
    result = patch.apply(single_line)
    assert result == ["Single Line", "After"]

    # Test replace
    patch = FileReplacePatch(start_line_number=1, current_lines=["Single Line"], new_lines=["Replaced"])
    result = patch.apply(single_line)
    assert result == ["Replaced"]


def test_patch_with_unicode_content():
    """Test patches with unicode content."""
    unicode_lines = ["Line with émojis 🚀", "Line with 中文", "Line with русский", "Line with العربية"]

    # Test insert with unicode
    patch = FileInsertPatch(start_line_number=2, current_line="Line with 中文", before_or_after="before", insert_lines=["Unicode line 🌟"])
    result = patch.apply(unicode_lines)
    expected = ["Line with émojis 🚀", "Unicode line 🌟", "Line with 中文", "Line with русский", "Line with العربية"]
    assert result == expected

    # Test replace with unicode
    patch = FileReplacePatch(start_line_number=3, current_lines=["Line with русский"], new_lines=["Replaced with 🎉", "Another line ✨"])
    result = patch.apply(unicode_lines)
    expected = ["Line with émojis 🚀", "Line with 中文", "Replaced with 🎉", "Another line ✨", "Line with العربية"]
    assert result == expected


def test_patch_with_empty_lines():
    """Test patches with empty lines."""
    lines_with_empty = [
        "Line 1",
        "",
        "Line 3",
        "   ",  # Line with only spaces
        "Line 5",
    ]

    # Test insert with empty lines
    patch = FileInsertPatch(start_line_number=2, current_line="", before_or_after="after", insert_lines=["Inserted after empty"])
    result = patch.apply(lines_with_empty)
    expected = ["Line 1", "", "Inserted after empty", "Line 3", "   ", "Line 5"]
    assert result == expected

    # Test replace empty lines
    patch = FileReplacePatch(start_line_number=2, current_lines=[""], new_lines=["Replaced empty"])
    result = patch.apply(lines_with_empty)
    expected = ["Line 1", "Replaced empty", "Line 3", "   ", "Line 5"]
    assert result == expected


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
            FileInsertPatch(start_line_number=1, current_line="Line 1", before_or_after="before", insert_lines=["New Line 1"]),
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
                FileInsertPatch(start_line_number=1, current_line="Line 1", before_or_after="before", insert_lines=["Added Line 1"]),
                FileInsertPatch(start_line_number=2, current_line="Line 2", before_or_after="before", insert_lines=["Added Line 2"]),
                FileInsertPatch(start_line_number=3, current_line="Line 3", before_or_after="before", insert_lines=["Added Line 3"]),
            ],
            ["Added Line 1", "Line 1", "Added Line 2", "Line 2", "Added Line 3", "Line 3", "Line 4", "Line 5"],
        ),
        (
            [
                FileInsertPatch(
                    start_line_number=1,
                    current_line="Line 1",
                    before_or_after="before",
                    insert_lines=["Added Line 1", "Added Line 2", "Added Line 3"],
                ),
                FileInsertPatch(
                    start_line_number=3,
                    current_line="Line 3",
                    before_or_after="before",
                    insert_lines=["Added Line 4", "Added Line 5", "Added Line 6"],
                ),
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
                FileInsertPatch(
                    start_line_number=10, current_line="Something that doesn't match", before_or_after="before", insert_lines=["Invalid"]
                ),
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


# NEW TESTS FOR BULK OPERATIONS WITH ERROR HANDLING


@pytest.mark.asyncio
async def test_bulk_patches_with_partial_failures(file_system: FileSystem, temp_file: Path):
    """Test that bulk patches handle partial failures correctly."""
    file_entry = FileEntry(path=temp_file, filesystem=file_system)

    # Create patches where some will succeed and some will fail
    patches = [
        FileInsertPatch(start_line_number=1, current_line="Line 1", before_or_after="before", insert_lines=["Header"]),
        FileReplacePatch(start_line_number=2, current_lines=["Wrong Line"], new_lines=["This will fail"]),
        FileInsertPatch(start_line_number=3, current_line="Line 3", before_or_after="before", insert_lines=["Middle"]),
    ]

    # The second patch should fail, but the first should succeed
    # We expect the operation to fail and the file to remain unchanged
    with pytest.raises(FilePatchDoesNotMatchError):
        await file_entry.apply_patches(patches)

    # Verify file content is unchanged
    async with aopen(temp_file) as f:
        content = await f.read()
        lines = content.splitlines()
    assert lines == SAMPLE_LINES


@pytest.mark.asyncio
async def test_bulk_patches_with_line_number_errors(file_system: FileSystem, temp_file: Path):
    """Test that bulk patches handle line number errors correctly."""
    file_entry = FileEntry(path=temp_file, filesystem=file_system)

    # Create patches where some have invalid line numbers
    patches = [
        FileInsertPatch(start_line_number=1, current_line="Line 1", before_or_after="before", insert_lines=["Header"]),
        FileInsertPatch(start_line_number=10, current_line="Line 3", before_or_after="before", insert_lines=["Middle"]),
    ]

    # The second patch should fail due to invalid line number
    with pytest.raises(FilePatchIndexError):
        await file_entry.apply_patches(patches)

    # Verify file content is unchanged
    async with aopen(temp_file) as f:
        content = await f.read()
        lines = content.splitlines()
    assert lines == SAMPLE_LINES


@pytest.mark.asyncio
async def test_multiple_insert_patches(file_system: FileSystem, temp_file: Path):
    """Test applying multiple insert patches in sequence."""
    file_entry = FileEntry(path=temp_file, filesystem=file_system)

    patches = [
        FileInsertPatch(start_line_number=1, current_line="Line 1", before_or_after="before", insert_lines=["Header"]),
        FileInsertPatch(start_line_number=3, current_line="Line 3", before_or_after="before", insert_lines=["Middle"]),
        FileInsertPatch(start_line_number=5, current_line="Line 5", before_or_after="after", insert_lines=["Footer"]),
    ]

    await file_entry.apply_patches(patches=patches)

    async with aopen(temp_file) as f:
        lines = await f.readlines()
        lines = [line.rstrip() for line in lines]

    assert lines == ["Header", "Line 1", "Line 2", "Middle", "Line 3", "Line 4", "Line 5", "Footer"]


@pytest.mark.asyncio
async def test_multiple_replace_patches(file_system: FileSystem, temp_file: Path):
    """Test applying multiple replace patches in sequence."""
    file_entry = FileEntry(path=temp_file, filesystem=file_system)

    patches = [
        FileReplacePatch(start_line_number=1, current_lines=["Line 1"], new_lines=["New Line 1"]),
        FileReplacePatch(start_line_number=3, current_lines=["Line 3"], new_lines=["New Line 3"]),
        FileReplacePatch(start_line_number=5, current_lines=["Line 5"], new_lines=["New Line 5"]),
    ]

    await file_entry.apply_patches(patches=patches)

    async with aopen(temp_file) as f:
        lines = await f.readlines()
        lines = [line.rstrip() for line in lines]

    assert lines == ["New Line 1", "Line 2", "New Line 3", "Line 4", "New Line 5"]
