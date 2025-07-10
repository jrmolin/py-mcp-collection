import tempfile
from pathlib import Path

import pytest

from local_references_mcp.references import Reference, ReferenceEntry, ReferenceManager


@pytest.fixture
def temp_directory():
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


def test_reference_entry_get_content(temp_directory: Path):
    temp_file = temp_directory / "Dashboard.md"
    temp_file.write_text("This is a test reference.")
    entry = ReferenceEntry(name="Dashboard", path=temp_file)
    content = entry.get_content()
    assert "This is a test reference." in content


def test_reference_entry_get_preview(temp_directory: Path):
    temp_file = temp_directory / "Dashboard.md"
    temp_file.write_text("This is a test reference.\n\nEntry1 content.")
    entry = ReferenceEntry(name="Dashboard", path=temp_file)
    preview = entry.get_preview(preview_size=1000)
    assert "Entry1 content." not in preview  # Should only get up to first double newline


def test_reference_from_reference_string(temp_directory: Path):
    temp_file = temp_directory / "Dashboard.md"
    ref_str = f"TestRef:{temp_file}"
    ref = Reference.from_reference_string(ref_str)
    assert ref.type == "TestRef"
    assert str(ref.path) == str(temp_file)


def test_reference_get_entry_by_name(temp_directory: Path):
    # Create a directory with a README.md file
    temp_file = temp_directory / "README.md"
    temp_file.write_text("This is the description of this reference type.")

    # Create a directory with a How To Make a Sandwich.md file
    how_to_file = temp_directory / "How To Make a Sandwich.md"
    how_to_file.write_text("This is the content of the how-to reference.")

    ref = Reference(type="How To", path=temp_directory)

    # Get the entry by name
    entry = ref.get_entry_by_name("How To Make a Sandwich")
    assert entry.path == how_to_file


def test_reference_get_description(temp_directory: Path):
    # Create a directory with a README.md file
    temp_file = temp_directory / "README.md"
    temp_file.write_text("This is the description of this reference type.")

    ref = Reference(type="How To", path=temp_directory)
    assert ref.description == "This is the description of this reference type."


def test_reference_manager_and_preview(temp_directory: Path):
    temp_file = temp_directory / "README.md"
    temp_file.write_text("This is the description of this reference type.")

    temp_entry = temp_directory / "Dashboard.md"
    temp_entry.write_text("This is a test reference.")

    ref_str = f"Cool Reference Type:{temp_directory}"
    mgr = ReferenceManager.from_reference_strings([ref_str], preview_size=1000)
    preview = mgr.preview_references()
    assert "# Local References" in preview
    assert "description of this reference type" in preview
    assert "Dashboard" in preview
    assert "This is a test reference." in preview


def test_reference_manager_get_reference(temp_directory: Path):
    # Create the readme
    temp_file = temp_directory / "README.md"
    temp_file.write_text("This is the description of this reference type.")

    # Create an entry
    entry_file = temp_directory / "Making a Sandwich.md"
    entry_file.write_text("This is a test reference.")

    ref_str = f"Best Practices:{temp_directory}"
    mgr = ReferenceManager.from_reference_strings([ref_str], preview_size=1000)
    content = mgr.get_reference("Best Practices", "Making a Sandwich")
    assert "This is a test reference." in content


def test_reference_structure_snapshot(tmp_path, snapshot):
    # Create a reference structure with two files

    folder1 = tmp_path / "Best Practices"
    folder1.mkdir(parents=True, exist_ok=True)
    file1 = folder1 / "README.md"
    file1.write_text("This is the best practice reference type.")
    file2 = folder1 / "Making a Sandwich.md"
    file2.write_text("This is the best practice reference.\n\nEntry1 content.")
    folder2 = tmp_path / "How To"
    folder2.mkdir(parents=True, exist_ok=True)
    file3 = folder2 / "README.md"
    file3.write_text("This is the how-to reference type.")
    file4 = folder2 / "How To Make a Sandwich.md"
    file4.write_text("This is the how-to reference.\n\nHowTo entry content.")
    file5 = folder2 / "How To Make a Sandwich.md"
    file5.write_text(
        "Of resolve to gravity thought my prepare chamber so. Unsatiable entreaties collecting may sympathize nay interested instrument. If continue building numerous of at relation in margaret. Lasted engage roused mother an am at. Other early while if by do to. Missed living excuse as be. Cause heard fat above first shall for. My smiling to he removal weather on anxious. "
        * 3
    )

    ref_strs = [f"Best Practices:{folder1}", f"How To:{folder2}"]
    mgr = ReferenceManager.from_reference_strings(ref_strs, preview_size=1000)

    # Snapshot the preview
    assert snapshot == mgr.preview_references()

    # Snapshot the full rendering for one reference
    assert snapshot == mgr.get_reference("Best Practices", "Making a Sandwich")
