from datetime import UTC, datetime
from fnmatch import fnmatch
from os import stat_result
from pathlib import Path
from typing import Any

from aiofiles.os import stat
from pydantic import BaseModel, Field

from filesystem_operations_mcp.filesystem.errors import FilesystemServerOutsideRootError


class BaseNode(BaseModel):
    absolute_path: Path = Field(exclude=True)
    """The absolute path of the node."""

    root: Path = Field(exclude=True)
    """The path of the node relative to the root."""

    def model_post_init(self, __context: Any):
        self.absolute_path = self.absolute_path.resolve()
        self.root = self.root.resolve()

    @property
    def name(self) -> str:
        return self.absolute_path.name

    async def created_at(self) -> datetime:
        stat_result = await self._stat()
        return datetime.fromtimestamp(stat_result.st_ctime, tz=UTC)

    async def modified_at(self) -> datetime:
        stat_result = await self._stat()
        return datetime.fromtimestamp(stat_result.st_mtime, tz=UTC)

    async def owner(self) -> int:
        stat_result = await self._stat()
        return stat_result.st_uid

    async def group(self) -> int:
        stat_result = await self._stat()
        return stat_result.st_gid

    async def _stat(self) -> stat_result:
        """The stat result of the file.

        This is cached very a very short period of time to avoid repeated stat calls.

        A stat_result contains:
        - st_mode: protection bits,
        - st_ino: inode number,
        - st_dev: device,
        - st_nlink: number of hard links,
        - st_uid: user id of owner,
        - st_gid: group id of owner,
        - st_size: size of file, in bytes,
        - st_atime: time of most recent access,
        - st_mtime: time of most recent content modification,
        - st_ctime: time of most recent metadata change on Unix, or the time of creation on Windows
        - st_atime_ns: time of most recent access, in nanoseconds
        - st_mtime_ns: time of most recent content modification in nanoseconds
        - st_ctime_ns: time of most recent metadata change on Unix, or the time of creation on Windows in nanoseconds
        - st_blocks: number of blocks allocated for file
        - st_blksize: filesystem blocksize
        - st_rdev: type of device if an inode device
        - st_gen: file generation number
        - st_birthtime: time of file creation in seconds
        - st_birthtime_ns: time of file creation in nanoseconds
        """
        return await stat(self.absolute_path)

    @property
    def relative_path(self) -> Path:
        return self.absolute_path.relative_to(self.root)

    def validate_in_root(self, root: Path) -> None:
        if not self.is_relative_to(root):
            raise FilesystemServerOutsideRootError(self.absolute_path, root)

    def is_relative_to(self, other: Path) -> bool:
        return self.absolute_path.is_relative_to(other)

    @property
    def is_file(self) -> bool:
        return self.absolute_path.is_file()

    @property
    def is_dir(self) -> bool:
        return self.absolute_path.is_dir()

    def passes_filters(self, includes: list[str] | None = None, excludes: list[str] | None = None, skip_hidden: bool = True) -> bool:
        """Checks if the node passes the include and exclude filters.

        Args:
            includes: A list of globs to include in the search.
            excludes: A list of globs to exclude from the search.

        Returns:
            True if the node passes the filters, False otherwise.
        """
        if skip_hidden:
            if excludes is None:
                excludes = []

            # What does .?* do? It's not Regex! It's a glob!
            # It matches any file or directory that starts with a dot (.) and is followed by 1 or more characters.
            # So .?* does not match . but does match .folder and does match .file

            excludes.append(".?*")  # any hidden files or directories in the root directory
            excludes.append(".?*/")  # any hidden directories in the root directory
            excludes.append("**/.?*")  # any hidden files or directories in any subdirectory

        if includes is None and excludes is None:
            return True

        relative_path_str = str(self.relative_path)

        if includes is not None and not any(fnmatch(relative_path_str, include) for include in includes):
            return False

        if excludes is not None and any(fnmatch(relative_path_str, exclude) for exclude in excludes):  # noqa: SIM103
            return False

        return True
