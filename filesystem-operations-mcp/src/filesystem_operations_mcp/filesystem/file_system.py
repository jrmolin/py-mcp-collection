from collections.abc import AsyncIterator
from pathlib import Path
from typing import Annotated

from pydantic import Field

from filesystem_operations_mcp.filesystem.errors import FilesystemServerOutsideRootError
from filesystem_operations_mcp.filesystem.nodes import BaseNode, DirectoryEntry, FileEntry, FileLines
from filesystem_operations_mcp.filesystem.patches.file import FileAppendPatch, FileDeletePatch, FileInsertPatch, FileReplacePatch
from filesystem_operations_mcp.logging import BASE_LOGGER

logger = BASE_LOGGER.getChild("file_system")

FilePaths = Annotated[list[Path], Field(description="A list of root-relative file paths.")]
FilePath = Annotated[Path, Field(description="The root-relative path of the file.")]

FileContent = Annotated[str, Field(description="The content of the file.")]

FileAppendContent = Annotated[
    str,
    Field(
        description="The content to append to the file.",
        examples=[FileAppendPatch(lines=["This content will be appended to the file!"])],
    ),
]
FileDeleteLineNumbers = Annotated[
    list[int],
    Field(
        description="The line numbers to delete from the file. Line numbers start at 1.",
        examples=[FileDeletePatch(line_numbers=[1, 2, 3])],
    ),
]
FileReplacePatches = Annotated[
    list[FileReplacePatch],
    Field(
        description="The patches to apply to the file.",
        examples=[
            FileReplacePatch(start_line_number=1, current_lines=["Line 1"], new_lines=["New Line 1"]),
            FileReplacePatch(start_line_number=2, current_lines=["Line 2", "Line 3"], new_lines=["New Line 2", "New Line 3"]),
        ],
    ),
]
FileInsertPatches = Annotated[
    list[FileInsertPatch],
    Field(
        description="The patches to apply to the file.",
        examples=[FileInsertPatch(line_number=1, current_line="Line 1", lines=["New Line 1"])],
    ),
]

Depth = Annotated[int, Field(description="The depth of the filesystem to get.", examples=[1, 2, 3])]

FileReadStart = Annotated[int, Field(description="The index-1 line number to start reading from.", examples=[1])]
FileReadCount = Annotated[int, Field(description="The number of lines to read.", examples=[100])]


class FileSystem(DirectoryEntry):
    """A virtual filesystem rooted in a specific directory on disk."""

    def __init__(self, path: Path):
        root_node = BaseNode(path=path)
        super().__init__(path=path, filesystem=root_node)

    async def get_root(self) -> AsyncIterator[FileEntry]:
        """Gets the items in the root of the filesystem."""
        async for file in self.afind_files(max_depth=1):
            yield file

    async def get_structure(self, depth: Depth = 2) -> AsyncIterator[FileEntry]:
        """Gets the structure of the filesystem up to the given depth."""
        async for file in self.afind_files(max_depth=depth):
            yield file

    async def create_file(self, path: FilePath, content: FileContent):
        """Creates a file.

        Returns:
            None if the file was created successfully, otherwise an error message.
        """
        path = self.path / Path(path)

        if not path.is_relative_to(self.path):
            raise FilesystemServerOutsideRootError(path, self.path)

        await FileEntry.create_file(path=path, content=content)

    async def delete_file(self, path: FilePath):
        """Deletes a file.

        Returns:
            None if the file was deleted successfully, otherwise an error message.
        """
        path = self.path / Path(path)

        if not path.is_relative_to(self.path):
            raise FilesystemServerOutsideRootError(path, self.path)

        file_entry = FileEntry(path=path, filesystem=self)

        await file_entry.delete()

    async def append_file(self, path: FilePath, content: FileAppendContent):
        """Appends content to a file.

        Returns:
            None if the file was appended to successfully, otherwise an error message.
        """
        path = self.path / Path(path)

        if not path.is_relative_to(self.path):
            raise FilesystemServerOutsideRootError(path, self.path)

        file_entry = FileEntry(path=path, filesystem=self)
        await file_entry.apply_patch(patch=FileAppendPatch(lines=[content]))

    async def delete_file_lines(self, path: FilePath, line_numbers: FileDeleteLineNumbers):
        """Deletes lines from a file.

        Returns:
            None if the lines were deleted successfully, otherwise an error message.
        """
        path = self.path / Path(path)

        if not path.is_relative_to(self.path):
            raise FilesystemServerOutsideRootError(path, self.path)

        file_entry = FileEntry(path=path, filesystem=self)
        await file_entry.apply_patch(patch=FileDeletePatch(line_numbers=line_numbers))

    async def replace_file_lines(self, path: FilePath, patches: FileReplacePatches):
        """Replaces lines in a file using find/replace style patch.

        Returns:
            None if the lines were replaced successfully, otherwise an error message.
        """
        path = self.path / Path(path)

        if not path.is_relative_to(self.path):
            raise FilesystemServerOutsideRootError(path, self.path)

        file_entry = FileEntry(path=path, filesystem=self)
        await file_entry.apply_patches(patches=patches)

    async def insert_file_lines(self, path: FilePath, patches: FileInsertPatches):
        """Inserts lines into a file.

        Returns:
            None if the lines were inserted successfully, otherwise an error message.
        """
        file_entry = FileEntry(path=self.path / Path(path), filesystem=self)
        await file_entry.apply_patches(patches=patches)

    async def read_file_lines(self, path: FilePath, start: FileReadStart = 1, count: FileReadCount = 100) -> FileLines:
        """Reads the content of a file.

        Returns:
            The content of the file.
        """
        file_entry = FileEntry(path=self.path / Path(path), filesystem=self)
        return await file_entry.afile_lines(start=start, count=count)
