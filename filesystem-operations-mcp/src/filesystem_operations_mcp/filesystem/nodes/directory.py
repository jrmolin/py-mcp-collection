from itertools import chain
from pathlib import Path

from aiofiles.os import scandir

from filesystem_operations_mcp.filesystem.nodes.base import BaseNode
from filesystem_operations_mcp.filesystem.nodes.file import FileEntry


class DirectoryEntry(BaseNode):
    """A directory entry in the filesystem."""

    @property
    def directory_path(self) -> str:
        """The path of the directory."""
        return str(self.relative_path)

    @property
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
            DirectoryEntry(absolute_path=Path(entry.path), relative_to=self.relative_to)
            if entry.is_dir()
            else FileEntry(absolute_path=Path(entry.path), relative_to=self.relative_to)
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

        entries = [FileEntry(absolute_path=p, relative_to=self.relative_to) for p in self.absolute_path.glob(glob) if p.is_file()]

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

        entries = [DirectoryEntry(absolute_path=p, relative_to=self.relative_to) for p in self.absolute_path.glob(glob) if p.is_dir()]

        return [entry for entry in entries if entry.passes_filters(includes=includes, excludes=excludes, skip_hidden=skip_hidden)]
