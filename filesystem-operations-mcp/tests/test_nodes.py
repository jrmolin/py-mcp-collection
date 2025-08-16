import tempfile
from pathlib import Path

import pytest

from filesystem_operations_mcp.filesystem.file_system import FileSystem
from filesystem_operations_mcp.filesystem.nodes import (
    BaseNode,
    DirectoryEntry,
    FileEntry,
    FileEntryTypeEnum,
    FileEntryWithMatches,
)
from tests.conftest import create_test_structure


@pytest.fixture
async def temp_dir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        root = Path(tmpdirname)
        await create_test_structure(root)
        yield root


@pytest.fixture
async def filesystem(temp_dir: Path):
    return FileSystem(path=temp_dir)


@pytest.fixture
async def root_directory(filesystem: FileSystem):
    return DirectoryEntry(path=filesystem.path, filesystem=filesystem)


def test_base_node_properties(temp_dir: Path):
    node = BaseNode(path=temp_dir)

    assert node.name == temp_dir.name
    assert node.is_dir
    assert not node.is_file


def test_file_node_properties(root_directory: DirectoryEntry):
    node = root_directory.get_file("test_with_hello_world.txt")
    assert node.name == "test_with_hello_world.txt"
    assert node.stem == "test_with_hello_world"
    assert node.extension == ".txt"
    assert node.path == root_directory.path / "test_with_hello_world.txt"

    assert node.relative_path == Path("test_with_hello_world.txt")
    assert node.relative_path_str == "test_with_hello_world.txt"

    assert node.is_file
    assert not node.is_dir
    assert node.size == 13
    assert node.type == FileEntryTypeEnum.TEXT


class TestFileEntry:
    def test_node_properties(self, root_directory: DirectoryEntry):
        node = root_directory.get_file("test_with_hello_world.txt")
        assert node.name == "test_with_hello_world.txt"
        assert node.stem == "test_with_hello_world"
        assert node.extension == ".txt"
        assert node.path == root_directory.path / "test_with_hello_world.txt"

    def test_file_size(self, root_directory: DirectoryEntry):
        node = root_directory.get_file("test_with_hello_world.txt")
        assert node.size == 13

    def test_file_type(self, root_directory: DirectoryEntry):
        node = root_directory.get_file("test_with_hello_world.txt")
        assert node.type == FileEntryTypeEnum.TEXT

    def test_file_extension(self, root_directory: DirectoryEntry):
        node = root_directory.get_file("test_with_hello_world.txt")
        assert node.extension == ".txt"

    def test_file_stem(self, root_directory: DirectoryEntry):
        node = root_directory.get_file("test_with_hello_world.txt")
        assert node.stem == "test_with_hello_world"

    def test_file_relative_path(self, root_directory: DirectoryEntry):
        node = root_directory.get_file("test_with_hello_world.txt")
        assert node.relative_path == Path("test_with_hello_world.txt")
        assert node.relative_path_str == "test_with_hello_world.txt"

    def test_file_relative_path_str(self, root_directory: DirectoryEntry):
        node = root_directory.get_file("test_with_hello_world.txt")
        assert node.relative_path_str == "test_with_hello_world.txt"

    def test_file_is_file(self, root_directory: DirectoryEntry):
        node = root_directory.get_file("test_with_hello_world.txt")
        assert node.is_file
        assert not node.is_dir

    async def test_file_atext(self, root_directory: DirectoryEntry):
        node = root_directory.get_file("test_with_hello_world.txt")
        assert await node.atext() == "Hello, World!"

    async def test_file_alines(self, root_directory: DirectoryEntry):
        node = root_directory.get_file("test_with_hello_world.txt")
        assert await node.alines() == ["Hello, World!"]

        multi_line_node = root_directory.get_file(path="./subdir/script_with_hello.sh")

        file_lines = await multi_line_node.afile_lines()
        assert file_lines.root == {1: "#!/bin/bash", 2: "echo 'Hello'"}

    async def test_file_alines_skip(self, root_directory: DirectoryEntry):
        multi_line_node = root_directory.get_file(path="./subdir/script_with_hello.sh")

        file_lines = await multi_line_node.afile_lines(count=1, start=2)
        assert file_lines.root == {2: "echo 'Hello'"}

    async def test_create_file(self, root_directory: DirectoryEntry, temp_dir: Path):
        await FileEntry.create_file(path=temp_dir / "test_with_hello_world_new.txt", lines=["Hello, World!"])
        node = root_directory.get_file("test_with_hello_world_new.txt")
        assert await node.atext() == "Hello, World!"
        assert node.size == 13


class TestDirectoryEntry:
    def test_node_properties(self, root_directory: DirectoryEntry):
        node = root_directory.get_directory("subdir")

        assert node.name == "subdir"
        assert node.is_dir
        assert not node.is_file
        assert node.relative_path == Path("subdir")
        assert node.relative_path_str == "subdir"

    def test_get_file(self, root_directory: DirectoryEntry):
        node = root_directory.get_file("subdir/nested.txt")
        assert node.name == "nested.txt"
        assert node.relative_path == Path("subdir/nested.txt")
        assert node.relative_path_str == "subdir/nested.txt"

    async def test_get_files(self, root_directory: DirectoryEntry):
        files = [file async for file in root_directory.aget_files(["subdir/nested.txt", "subdir/script_with_hello.sh"])]
        assert len(files) == 2
        assert {f.name for f in files} == {"nested.txt", "script_with_hello.sh"}

    def test_get_directory(self, root_directory: DirectoryEntry):
        node = root_directory.get_directory("subdir")
        assert node.name == "subdir"
        assert node.relative_path == Path("subdir")
        assert node.relative_path_str == "subdir"

    class TestFindFiles:
        async def test(self, root_directory: DirectoryEntry):
            descendants: list[FileEntry] = [file async for file in root_directory.afind_files()]
            assert len(descendants) == 5
            descendant_names = sorted([d.name for d in descendants])
            assert descendant_names == sorted(
                [
                    "code_with_hello_world.py",
                    "nested.txt",
                    "script_with_hello.sh",
                    "test_with_hello_world.txt",
                    "CaSeSenSiTiVe.txt",
                ]
            )

        async def test_depth_one(self, root_directory: DirectoryEntry):
            descendants: list[FileEntry] = [file async for file in root_directory.afind_files(max_depth=1)]
            assert len(descendants) == 3
            descendant_names = sorted([d.name for d in descendants])
            assert descendant_names == sorted(
                [
                    "code_with_hello_world.py",
                    "test_with_hello_world.txt",
                    "CaSeSenSiTiVe.txt",
                ]
            )

        async def test_depth_one_with_excludes(self, root_directory: DirectoryEntry):
            descendants: list[FileEntry] = [file async for file in root_directory.afind_files(max_depth=1, excluded_globs=["*.txt"])]
            assert len(descendants) == 1
            descendant_names = sorted([d.name for d in descendants])
            assert descendant_names == [
                "code_with_hello_world.py",
            ]

        async def test_excludes_includes(self, root_directory: DirectoryEntry):
            descendants: list[FileEntry] = [
                file async for file in root_directory.afind_files(excluded_globs=["*.txt"], included_globs=["*.py"])
            ]
            assert len(descendants) == 1
            descendant_names = sorted([d.name for d in descendants])
            assert descendant_names == [
                "code_with_hello_world.py",
            ]

        async def test_includes_subdir(self, root_directory: DirectoryEntry):
            descendants: list[FileEntry] = [file async for file in root_directory.afind_files(included_globs=["subdir/*"])]
            assert len(descendants) == 3
            descendant_names = sorted([d.name for d in descendants])
            assert descendant_names == [
                "nested.txt",
                "script_with_hello.sh",
                "should_be_ignored.env",  # The user has specifically included it
            ]

        async def test_excludes_subdir(self, root_directory: DirectoryEntry):
            descendants: list[FileEntry] = [file async for file in root_directory.afind_files(excluded_globs=["subdir"])]
            assert len(descendants) == 3
            descendant_names = sorted([d.name for d in descendants])
            assert descendant_names == sorted(
                [
                    "code_with_hello_world.py",
                    "test_with_hello_world.txt",
                    "CaSeSenSiTiVe.txt",
                ]
            )

        async def test_subdir(self, root_directory: DirectoryEntry):
            descendants: list[FileEntry] = [file async for file in root_directory.get_directory("subdir").afind_files()]
            assert len(descendants) == 2
            descendant_names = sorted([d.name for d in descendants])
            assert descendant_names == [
                "nested.txt",
                "script_with_hello.sh",
            ]

        async def test_case_insensitive(self, root_directory: DirectoryEntry):
            descendants: list[FileEntry] = [file async for file in root_directory.afind_files(included_globs=["**.txt"])]
            assert len(descendants) == 3
            descendant_names = sorted([d.name for d in descendants])
            assert descendant_names == sorted(
                [
                    "CaSeSenSiTiVe.txt",
                    "nested.txt",
                    "test_with_hello_world.txt",
                ]
            )

    class TestSearchFiles:
        async def test(self, root_directory: DirectoryEntry):
            descendants: list[FileEntry] = [file async for file in root_directory.asearch_files(["print"])]
            assert len(descendants) == 1
            descendant_names = sorted([d.name for d in descendants])
            assert descendant_names == [
                "code_with_hello_world.py",
            ]

        async def test_two(self, root_directory: DirectoryEntry):
            descendants: list[FileEntryWithMatches] = [file async for file in root_directory.asearch_files(["hello"])]
            descendants.sort(key=lambda x: x.name)
            assert len(descendants) == 3
            descendant_names = [d.name for d in descendants]
            assert descendant_names == [
                "code_with_hello_world.py",
                "script_with_hello.sh",
                "test_with_hello_world.txt",
            ]

            first_file = descendants[0]
            assert first_file.name == "code_with_hello_world.py"
            first_match_lines = first_file.matches.lines()
            assert len(first_match_lines) == 2
            assert first_match_lines[0] == "def hello():"
            assert first_match_lines[1] == "    print('Hello, World!')"

        async def test_case_insensitive(self, root_directory: DirectoryEntry):
            descendants: list[FileEntryWithMatches] = [file async for file in root_directory.asearch_files(["hello"], case_sensitive=False)]
            assert len(descendants) == 3
            descendant_names = sorted([d.name for d in descendants])
            assert descendant_names == [
                "code_with_hello_world.py",
                "script_with_hello.sh",
                "test_with_hello_world.txt",
            ]
