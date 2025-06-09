from itertools import chain
from pathlib import Path

from aiofiles.os import mkdir as amkdir
from aiofiles.os import rmdir as armdir
from aiofiles.os import scandir

from filesystem_operations_mcp.filesystem.errors import (
    DirectoryAlreadyExistsError,
    DirectoryNotEmptyError,
    DirectoryNotFoundError,
)
from filesystem_operations_mcp.filesystem.nodes.base import BaseNode
from filesystem_operations_mcp.filesystem.nodes.file import FileEntry


class DirectoryEntry(BaseNode):
    """A directory entry in the filesystem."""

    async def is_empty(self) -> bool:
        """Whether the directory is empty."""
        return not any(await self.children())

    @property
    def directory_path(self) -> str:
        """The path of the directory."""
        return str(self.relative_path)

    async def children(self) -> list["DirectoryEntry | FileEntry"]:
        """The children of the directory."""
        return await self._children(depth=0)

    async def _children(
        self, depth: int = 0, includes: list[str] | None = None, excludes: list[str] | None = None, skip_hidden: bool = True
    ) -> list["DirectoryEntry | FileEntry"]:
        """Returns a flat list of children of the directory.

        Args:
            depth: The depth of the children to return.
            includes: A list of globs to include in the search.
            excludes: A list of globs to exclude from the search.
        """
        dir_iterator = await scandir(self.absolute_path)

        children = [
            DirectoryEntry(absolute_path=Path(entry.path), root=self.root)
            if entry.is_dir()
            else FileEntry(absolute_path=Path(entry.path), root=self.root)
            for entry in dir_iterator
        ]

        children = [p for p in children if p.passes_filters(includes=includes, excludes=excludes, skip_hidden=skip_hidden)]

        if depth > 0:
            return list(
                chain(
                    *[
                        children,
                        *[
                            await p._children(depth=depth - 1, includes=includes, excludes=excludes)
                            for p in children
                            if isinstance(p, DirectoryEntry)
                        ],
                    ]
                )
            )

        return children

    @classmethod
    async def create_directory(cls, directory_path: Path) -> None:
        """Creates a directory.

        Returns:
            None if the directory was created successfully, otherwise an error message.
        """
        if directory_path.exists():
            raise DirectoryAlreadyExistsError(directory_path=str(directory_path))

        await amkdir(directory_path)

    async def delete_directory(self, directory_path: str) -> None:
        """Deletes a directory.

        Returns:
            None if the directory was deleted successfully, otherwise an error message.
        """
        new_path: Path = self.absolute_path / Path(directory_path)

        if not new_path.exists():
            raise DirectoryNotFoundError(directory_path=str(new_path))

        # Make sure the directory is empty
        children = await self._children(depth=0)

        if children:
            raise DirectoryNotEmptyError(directory_path=str(new_path))

        await armdir(new_path)

    async def search_files(
        self,
        glob: str,
        pattern: str,
        pattern_is_regex: bool = False,
        includes: list[str] | None = None,
        excludes: list[str] | None = None,
        skip_hidden: bool = True,
    ) -> list[FileEntry]:
        """Searches the text files in the directory for the given pattern.

        Returns:
            A list of files that match the pattern.
        """

        files = await self.find_files(glob, includes, excludes, skip_hidden)

        files = [file for file in files if not file.is_binary]

        return [file for file in files if await file.contents_match(pattern, pattern_is_regex)]

    async def find_files(
        self, glob: str, includes: list[str] | None = None, excludes: list[str] | None = None, skip_hidden: bool = True
    ) -> list[FileEntry]:
        """Finds files in the directory that match the glob.

        Args:
            glob: The glob to search for.
            includes: A list of globs to limit the search to.
            excludes: A list of globs to exclude from the search.

        Returns:
            A list of files that match the glob.
        """

        entries = [FileEntry(absolute_path=p, root=self.root) for p in self.absolute_path.rglob(glob) if p.is_file()]

        return [entry for entry in entries if entry.passes_filters(includes=includes, excludes=excludes, skip_hidden=skip_hidden)]

    async def find_dirs(
        self, glob: str, includes: list[str] | None = None, excludes: list[str] | None = None, skip_hidden: bool = True
    ) -> list["DirectoryEntry"]:
        """Finds directories in the directory that match the glob.

        Args:
            glob: The glob to search for.
            includes: A list of globs to include in the search.
            excludes: A list of globs to exclude from the search.

        Returns:
            A list of directories that match the glob.
        """

        entries = [DirectoryEntry(absolute_path=p, root=self.root) for p in self.absolute_path.rglob(glob) if p.is_dir()]

        return [entry for entry in entries if entry.passes_filters(includes=includes, excludes=excludes, skip_hidden=skip_hidden)]
