from collections.abc import AsyncIterator
from pathlib import Path
from typing import Annotated, Any

from pydantic import Field, model_serializer
from pydantic.fields import computed_field
from pydantic.main import BaseModel

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
        description="The content to append to the end of the file.",
        examples=[FileAppendPatch(lines=["This content will be appended to end ofthe file!"])],
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
        description="A set of patches to apply to the file.",
        examples=[
            FileReplacePatch(start_line_number=1, current_lines=["Line 1"], new_lines=["New Line 1"]),
            FileReplacePatch(start_line_number=2, current_lines=["Line 2", "Line 3"], new_lines=["New Line 2", "New Line 3"]),
        ],
    ),
]
FileInsertPatches = Annotated[
    list[FileInsertPatch],
    Field(
        description="A set of patches to apply to the file.",
        examples=[FileInsertPatch(line_number=1, current_line="Line 1", lines=["New Line 1"])],
    ),
]

Depth = Annotated[int, Field(description="The depth of the filesystem to get.", examples=[1, 2, 3])]

FileReadStart = Annotated[int, Field(description="The index-1 line number to start reading from.", examples=[1])]
FileReadCount = Annotated[int, Field(description="The number of lines to read.", examples=[100])]


class ReadFileLinesResponse(BaseModel):
    path: str = Field(description="The path of the file.")
    lines: FileLines = Field(description="The lines of text in the file.")
    max_lines: int = Field(description="The maximum number of lines to read.", exclude=True)
    total_lines: int = Field(description="The total number of lines in the file.")

    @computed_field
    @property
    def max_lines_reached(self) -> bool:
        """Whether the maximum number of lines has been reached."""
        return len(self.lines.lines()) >= self.max_lines


class FileSystemStructureResponse(BaseModel):
    max_results: int = Field(description="The maximum number of results to return.", exclude=True)
    directories: list[str] = Field(description="The results of the filesystem structure.")

    @computed_field
    @property
    def max_results_reached(self) -> bool:
        return len(self.directories) >= self.max_results

    @model_serializer
    def serialize(self) -> dict[str, Any]:
        kv: dict[str, Any] = {
            "directories": self.directories,
        }

        if self.max_results_reached:
            kv["max_results_reached"] = True
            kv["max_results"] = self.max_results

        return kv


class FileSystem(DirectoryEntry):
    """A virtual filesystem rooted in a specific directory on disk."""

    def __init__(self, path: Path):
        root_node = BaseNode(path=path)
        super().__init__(path=path, filesystem=root_node)

    async def aget_root(self) -> AsyncIterator[FileEntry]:
        """Gets the items in the root of the filesystem."""
        async for file in self.afind_files(max_depth=1):
            yield file

    def get_structure(self, depth: Depth = 2, max_results: int = 200) -> FileSystemStructureResponse:
        """Gets the structure of the filesystem up to the given depth. Structure includes directories only
        and does not include files. Structure is gathered depth-first, up to the given depth. This means that
        any descendants deeper than the given depth will not be included in the results.

        Once the max results limit is reached, the response will include a flag indicating that the limit was reached.
        """

        accumulated_results: list[str] = []

        for descendent in self.get_descendent_directories(root=self, depth=depth):
            accumulated_results.append(descendent.relative_path_str)

            if len(accumulated_results) >= max_results:
                break

        return FileSystemStructureResponse(
            max_results=max_results,
            directories=accumulated_results,
        )

    async def create_file(self, path: FilePath, content: FileContent) -> None:
        """Creates a file.

        Returns:
            None if the file was created successfully, otherwise an error message.
        """
        path = self.path / Path(path)

        if not path.is_relative_to(self.path):
            raise FilesystemServerOutsideRootError(path, self.path)

        await FileEntry.create_file(path=path, content=content)

    async def delete_file(self, path: FilePath) -> None:
        """Deletes a file.

        Returns:
            None if the file was deleted successfully, otherwise an error message.
        """
        path = self.path / Path(path)

        if not path.is_relative_to(self.path):
            raise FilesystemServerOutsideRootError(path, self.path)

        file_entry = FileEntry(path=path, filesystem=self)

        await file_entry.delete()

    async def append_file(self, path: FilePath, content: FileAppendContent) -> None:
        """Appends content to a file.

        Returns:
            None if the file was appended to successfully, otherwise an error message.
        """
        path = self.path / Path(path)

        if not path.is_relative_to(self.path):
            raise FilesystemServerOutsideRootError(path, self.path)

        file_entry = FileEntry(path=path, filesystem=self)
        await file_entry.apply_patch(patch=FileAppendPatch(lines=[content]))

    async def delete_file_lines(self, path: FilePath, line_numbers: FileDeleteLineNumbers) -> None:
        """Deletes lines from a file. It is recommended to read the file again after applying patches
        to ensure the changes were applied correctly and that you have the updated content for the file.

        Returns:
            None if the lines were deleted successfully, otherwise an error message.
        """
        path = self.path / Path(path)

        if not path.is_relative_to(self.path):
            raise FilesystemServerOutsideRootError(path, self.path)

        file_entry = FileEntry(path=path, filesystem=self)
        await file_entry.apply_patch(patch=FileDeletePatch(line_numbers=line_numbers))

    async def replace_file_lines_bulk(self, path: FilePath, patches: FileReplacePatches) -> None:
        """Replaces lines in a file using find/replace style patch. It is recommended to read the file after applying
        patches to ensure the changes were applied correctly and that you have the updated content for the file.

        Returns:
            None if the lines were replaced successfully, otherwise an error message.
        """
        path = self.path / Path(path)

        if not path.is_relative_to(self.path):
            raise FilesystemServerOutsideRootError(path, self.path)

        file_entry = FileEntry(path=path, filesystem=self)
        await file_entry.apply_patches(patches=patches)

    async def replace_file_lines(
        self,
        path: FilePath,
        start_line_number: Annotated[int, FileReplacePatch.model_fields["start_line_number"]],
        current_lines: Annotated[list[str], FileReplacePatch.model_fields["current_lines"]],
        new_lines: Annotated[list[str], FileReplacePatch.model_fields["new_lines"]],
    ) -> None:
        """Replaces lines in a file using find/replace style patch. It is recommended to read the file after applying
        patches to ensure the changes were applied correctly and that you have the updated content for the file.
        """
        file_entry = FileEntry(path=self.path / Path(path), filesystem=self)
        await file_entry.apply_patch(
            patch=FileReplacePatch(start_line_number=start_line_number, current_lines=current_lines, new_lines=new_lines)
        )

    async def insert_file_lines_bulk(self, path: FilePath, patches: FileInsertPatches) -> None:
        """Inserts lines into a file. It is recommended to read the file after applying patches to ensure the changes
        were applied correctly and that you have the updated content for the file.

        Returns:
            None if the lines were inserted successfully, otherwise an error message.
        """
        file_entry = FileEntry(path=self.path / Path(path), filesystem=self)
        await file_entry.apply_patches(patches=patches)

    async def insert_file_lines(
        self,
        path: FilePath,
        line_number: Annotated[
            int,
            FileInsertPatch.model_fields["line_number"],
        ],
        current_line: Annotated[
            str,
            FileInsertPatch.model_fields["current_line"],
        ],
        lines: Annotated[
            list[str],
            FileInsertPatch.model_fields["lines"],
        ],
    ) -> None:
        """Inserts lines into a file. It is recommended to read the file after applying patches to ensure the changes
        were applied correctly and that you have the updated content for the file.

        Returns:
            None if the lines were inserted successfully, otherwise an error message.
        """
        file_entry = FileEntry(path=self.path / Path(path), filesystem=self)
        await file_entry.apply_patch(patch=FileInsertPatch(line_number=line_number, current_line=current_line, lines=lines))

    async def read_file_lines(self, path: FilePath, start: FileReadStart = 1, count: FileReadCount = 250) -> ReadFileLinesResponse:
        """Reads the content of a file. It will read up to `count` lines starting from `start`. So if you want
        to read the first 100 lines, you would just pass `count=100`. If you want the following 100 lines, you
        would pass `start=101` and `count=100`.

        If the response includes `max_lines_reached=False`, that means that the file has additional lines that
        have not been read yet.

        Returns:
            The content of the file.
        """
        file_entry = FileEntry(path=self.path / Path(path), filesystem=self)
        lines = await file_entry.afile_lines(start=start, count=count)

        return ReadFileLinesResponse(
            path=file_entry.relative_path_str,
            lines=lines,
            max_lines=count,
            total_lines=await file_entry.aget_total_lines(),
        )

    async def read_file_lines_bulk(
        self, paths: FilePaths, start: FileReadStart = 1, count: FileReadCount = 250
    ) -> list[ReadFileLinesResponse]:
        """Reads the content of a list of files. It will read up to `count` lines starting from `start`. So if you want
        to read the first 100 lines, you would just pass `count=100`. If you want the following 100 lines, you
        would pass `start=101` and `count=100`.

        If the response includes `max_lines_reached=False`, that means that the file has additional lines that
        have not been read yet.

        You can provide a maximum of 10 files at a time. If more than 10 files are provided, only the first 10
        files will be read.

        Returns:
            The content of the files.
        """

        paths = paths[:10]

        return [await self.read_file_lines(path=path, start=start, count=count) for path in paths]
