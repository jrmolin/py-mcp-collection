from pathlib import Path
from typing import Annotated

from pydantic import Field

from filesystem_operations_mcp.filesystem.nodes.directory import DirectoryEntry
from filesystem_operations_mcp.filesystem.nodes.file import FileEntry, FileEntryMatch
from filesystem_operations_mcp.logging import BASE_LOGGER

logger = BASE_LOGGER.getChild("file_system")

FilePaths = Annotated[list[str], Field(description="A list of root-relative file paths to get.")]
FilePath = Annotated[str, Field(description="The root-relative path to the file to get.")]

DirectoryPaths = Annotated[list[str], Field(description="A list of root-relative directory paths to get.")]
DirectoryPath = Annotated[str, Field(description="The root-relative path to the directory to search in.")]

FileGlob = Annotated[str, Field(description="The root-relative glob to search for.")]
DirectoryGlob = Annotated[str, Field(description="The root-relative glob to search for.")]

Depth = Annotated[int, Field(description="The depth of the search.")]
Includes = Annotated[list[str], Field(description="The root-relative globs to include in the search.")]
Excludes = Annotated[list[str], Field(description="The root-relative globs to exclude from the search.")]

SkipHidden = Annotated[bool, Field(description="Whether to skip hidden files and directories.")]

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
        self.root_directory = DirectoryEntry(absolute_path=self.root, relative_to=self.root)

    async def get_root(self) -> DirectoryEntry:
        """Gets the root directory."""
        return self.root_directory

    async def get_structure(
        self,
        depth: Depth = 2,
        includes: Includes | None = None,
        excludes: Excludes | None = None,
        skip_hidden: SkipHidden = True,
    ) -> list[DirectoryEntry]:
        """Gets the structure of the filesystem.

        Returns:
            A list of DirectoryEntry and FileEntry objects.

        Example:
            >>> await get_structure(depth=2)
            [
                {"directory_path": ".", "children_count": 2},
                {"directory_path": "directory_1", "children_count": 1},
                {"directory_path": "directory_1/directory_a", "children_count": 0},
            ]
        """

        children = await self.root_directory._children(
            depth=depth,
            includes=includes,
            excludes=excludes,
            skip_hidden=skip_hidden,
        )

        child_dirs: list[DirectoryEntry] = [child for child in children if child.is_dir()]  # type: ignore

        return [self.root_directory, *child_dirs]

    async def get_files(self, file_paths: list[str]) -> list[FileEntry]:
        """Gets the files in the filesystem.

        Args:
            file_paths: A list of file paths to get.

        Returns:
            A list of file paths. Relative to the root of the File Server.
        """
        return [FileEntry(absolute_path=Path(this_path).resolve(), relative_to=self.root) for this_path in file_paths]

    async def get_text_files(self, file_paths: list[str]) -> list[FileEntry]:
        """Gets the text files in the filesystem."""
        return [file for file in await self.get_files(file_paths) if not file.is_binary]

    async def get_directories(self, directory_paths: list[str]) -> list[DirectoryEntry]:
        """Gets the directories in the filesystem.

        Args:
            directory_paths: A list of directory paths to get.

        Returns:
            A list of directory paths. Relative to the root of the File Server.
        """
        return [DirectoryEntry(absolute_path=Path(this_path).resolve(), relative_to=self.root) for this_path in directory_paths]

    # @mcp_tool(name="read_file_contents")
    # async def get_file_contents(self, file_path: str) -> str:
    #     """Gets the contents of the file."""
    #     return await FileEntry(absolute_path=Path(file_path).resolve(), relative_to=self.root).contents

    # @mcp_tool(name="read_file_lines")
    # async def get_file_lines(self, file_path: str) -> list[str]:
    #     """Gets the lines of the file."""
    #     return await FileEntry(absolute_path=Path(file_path).resolve(), relative_to=self.root).lines

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
            return await FileEntry(absolute_path=Path(file_path).resolve(), relative_to=self.root).contents_match_regex(
                pattern, before, after
            )
        return await FileEntry(absolute_path=Path(file_path).resolve(), relative_to=self.root).contents_match(pattern, before, after)

    async def find_files(
        self,
        glob: FileGlob,
        directory_path: DirectoryPath = ".",
        includes: Includes | None = None,
        excludes: Excludes | None = None,
        skip_hidden: SkipHidden = True,
    ) -> list[FileEntry]:
        """Finds the files in the directory."""
        return await DirectoryEntry(absolute_path=Path(directory_path).resolve(), relative_to=self.root).find_files(
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
        return await DirectoryEntry(absolute_path=Path(directory_path).resolve(), relative_to=self.root).find_dirs(
            glob, includes, excludes, skip_hidden
        )
