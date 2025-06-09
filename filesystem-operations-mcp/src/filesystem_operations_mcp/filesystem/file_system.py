from pathlib import Path
from typing import Annotated

from pydantic import Field

from filesystem_operations_mcp.filesystem.nodes.directory import DirectoryEntry
from filesystem_operations_mcp.filesystem.nodes.file import FileEntry, FileEntryMatch
from filesystem_operations_mcp.filesystem.patches.file import FileAppendPatch, FileDeletePatch, FileInsertPatch, FileReplacePatch
from filesystem_operations_mcp.logging import BASE_LOGGER

logger = BASE_LOGGER.getChild("file_system")

FilePaths = Annotated[list[str], Field(description="A list of root-relative file paths to get.")]
FilePath = Annotated[str, Field(description="The root-relative path to the f    ile to get.")]

FileContent = Annotated[str, Field(description="The content of the file.")]

FileAppendContent = Annotated[str, Field(description="The content to append to the file.")]
FileDeleteLineNumbers = Annotated[list[int], Field(description="The line numbers to delete from the file.")]

DirectoryPaths = Annotated[list[str], Field(description="A list of root-relative directory paths to get.")]
DirectoryPath = Annotated[str, Field(description="The root-relative path to the directory to search in.")]

FileGlob = Annotated[str, Field(description="The root-relative glob to search for.")]
DirectoryGlob = Annotated[str, Field(description="The root-relative glob to search for.")]

Depth = Annotated[int, Field(description="The depth of the search. 0 means immediate children only.")]
Includes = Annotated[list[str], Field(description="The root-relative globs to include in the search.")]
Excludes = Annotated[list[str], Field(description="The root-relative globs to exclude from the search.")]

SkipHidden = Annotated[bool, Field(description="Whether to skip hidden files and directories.")]
SkipEmpty = Annotated[bool, Field(description="Whether to skip empty directories.")]

ContentSearchPattern = Annotated[str, Field(description="The pattern to search for in the contents of the file.")]
ContentSearchPatternIsRegex = Annotated[bool, Field(description="Whether the pattern is a regex.")]
LinesBeforeMatch = Annotated[int, Field(description="The number of lines before the match to include.")]
LinesAfterMatch = Annotated[int, Field(description="The number of lines after the match to include.")]


class FileSystem:
    """A simple filesystem implementation."""

    root: Path
    root_directory: DirectoryEntry

    def __init__(self, root: Path):
        self.root = root
        self.root_directory = DirectoryEntry(absolute_path=self.root, root=self.root)

    async def get_root(self) -> DirectoryEntry:
        """Gets the root directory of the filesystem mounted by this server."""
        return self.root_directory

    async def get_structure(
        self,
        depth: Depth = 2,
        includes: Includes | None = None,
        excludes: Excludes | None = None,
        skip_hidden: SkipHidden = True,
        skip_empty: SkipEmpty = True,
    ) -> list[DirectoryEntry]:
        """Gets the directory structure of the filesystem.

        Returns:
            A list of DirectoryEntry objects.

        Example:
            >>> await get_structure(depth=1)
            [
                {"directory_path": ".", "children_count": 2},
                {"directory_path": "directory_1", "children_count": 1},  # Depth 0
                {"directory_path": "directory_1/directory_a", "children_count": 0},  # Depth 1
            ]
        """

        children = await self.root_directory._children(
            depth=depth,
            includes=includes,
            excludes=excludes,
            skip_hidden=skip_hidden,
        )

        child_dirs: list[DirectoryEntry] = [child for child in children if child.is_dir]  # type: ignore

        if skip_empty:
            child_dirs = [child for child in child_dirs if not await child.is_empty()]

        return [self.root_directory, *child_dirs]

    async def create_directory(self, directory_path: DirectoryPath):
        """Creates a directory.

        Returns:
            None if the directory was created successfully, otherwise an error message.
        """
        await DirectoryEntry.create_directory(directory_path=self.root / Path(directory_path))

    async def delete_directory(self, directory_path: DirectoryPath):
        """Deletes a directory.

        Returns:
            None if the directory was deleted successfully, otherwise an error message.
        """
        await self.root_directory.delete_directory(directory_path)

    async def create_file(self, file_path: FilePath, content: FileContent):
        """Creates a file.

        Returns:
            None if the file was created successfully, otherwise an error message.
        """
        await FileEntry.create_file(file_path=self.root / Path(file_path), content=content)

    async def delete_file(self, file_path: FilePath):
        """Deletes a file.

        Returns:
            None if the file was deleted successfully, otherwise an error message.
        """
        file_entry = FileEntry(absolute_path=self.root / Path(file_path), root=self.root)

        await file_entry.delete()

    async def append_file(self, file_path: FilePath, content: FileAppendContent):
        """Appends content to a file.

        Returns:
            None if the file was appended to successfully, otherwise an error message.
        """
        file_entry = FileEntry(absolute_path=self.root / Path(file_path), root=self.root)
        await file_entry.apply_patch(patch=FileAppendPatch(lines=[content]))

    async def delete_file_lines(self, file_path: FilePath, line_numbers: FileDeleteLineNumbers):
        """Deletes lines from a file.

        Returns:
            None if the lines were deleted successfully, otherwise an error message.
        """
        file_entry = FileEntry(absolute_path=self.root / Path(file_path), root=self.root)
        await file_entry.apply_patch(patch=FileDeletePatch(line_numbers=line_numbers))

    async def replace_file_lines(self, file_path: FilePath, patches: list[FileReplacePatch]):
        """Replaces lines in a file using find/replace style patch.

        Returns:
            None if the lines were replaced successfully, otherwise an error message.
        """
        file_entry = FileEntry(absolute_path=self.root / Path(file_path), root=self.root)
        await file_entry.apply_patches(patches=patches)

    async def insert_file_lines(self, file_path: FilePath, patches: list[FileInsertPatch]):
        """Inserts lines into a file.

        Returns:
            None if the lines were inserted successfully, otherwise an error message.
        """
        file_entry = FileEntry(absolute_path=self.root / Path(file_path), root=self.root)
        await file_entry.apply_patches(patches=patches)

    async def get_files(self, file_paths: FilePaths) -> list[FileEntry]:
        """Gets the files in the filesystem.

        Args:
            file_paths: A list of file paths to get.

        Returns:
            A list of file paths. Relative to the root of the File Server.
        """
        return [FileEntry(absolute_path=self.root / Path(this_path), root=self.root) for this_path in file_paths]

    async def get_text_files(self, file_paths: FilePaths) -> list[FileEntry]:
        """Gets the text files in the filesystem."""
        return [file for file in await self.get_files(file_paths) if not file.is_binary]

    async def get_directories(self, directory_paths: DirectoryPaths) -> list[DirectoryEntry]:
        """Gets the directories in the filesystem.

        Args:
            directory_paths: A list of directory paths to get.

        Returns:
            A list of directory paths. Relative to the root of the File Server.
        """
        return [DirectoryEntry(absolute_path=self.root / Path(this_path), root=self.root) for this_path in directory_paths]

    async def get_file_matches(
        self,
        file_path: FilePath,
        pattern: ContentSearchPattern,
        pattern_is_regex: ContentSearchPatternIsRegex = False,
        before: LinesBeforeMatch = 0,
        after: LinesAfterMatch = 0,
    ) -> list[FileEntryMatch]:
        """Gets the matches of the file."""
        if pattern_is_regex:
            return await FileEntry(absolute_path=self.root / Path(file_path), root=self.root).contents_match_regex(pattern, before, after)
        return await FileEntry(absolute_path=self.root / Path(file_path), root=self.root).contents_match(pattern, before, after)

    async def search_files(
        self,
        glob: FileGlob,
        pattern: ContentSearchPattern,
        pattern_is_regex: ContentSearchPatternIsRegex = False,
        directory_path: DirectoryPath = ".",
        includes: Includes | None = None,
        excludes: Excludes | None = None,
        skip_hidden: SkipHidden = True,
    ) -> list[FileEntry]:
        """Searches the files in the directory for the given pattern. Returns the file entries that
        contain the pattern. Does not return matches from the file itself. Read the file to get the matches.

        Returns:
            A list of file paths with matching content. Relative to the root of the File Server.
        """

        return await DirectoryEntry(absolute_path=self.root / Path(directory_path), root=self.root).search_files(
            glob, pattern, pattern_is_regex, includes, excludes, skip_hidden
        )

    async def find_files(
        self,
        glob: FileGlob,
        directory_path: DirectoryPath = ".",
        includes: Includes | None = None,
        excludes: Excludes | None = None,
        skip_hidden: SkipHidden = True,
    ) -> list[FileEntry]:
        """Finds the files in the directory."""
        return await DirectoryEntry(absolute_path=self.root / Path(directory_path), root=self.root).find_files(
            glob, includes, excludes, skip_hidden
        )

    async def find_dirs(
        self,
        glob: DirectoryGlob,
        directory_path: DirectoryPath = ".",
        includes: Includes | None = None,
        excludes: Excludes | None = None,
        skip_hidden: SkipHidden = True,
    ) -> list[DirectoryEntry]:
        """Finds the directories in the directory."""
        return await DirectoryEntry(absolute_path=self.root / Path(directory_path), root=self.root).find_dirs(
            glob, includes, excludes, skip_hidden
        )
