import re
from fnmatch import fnmatch
from pathlib import Path
from typing import TypeVar

from filesystem_operations_mcp.filesystem.models import (
    FileEntry,
    FileEntryChunk,
    FileEntryChunkedContent,
    FileEntryContent,
    FileEntryPreview,
    FlatDirectoryResult,
    SummaryDirectoryEntry,
)

R = TypeVar("R", bound=FileEntry | FileEntryContent | FileEntryPreview)


class FilesystemServerError(Exception):
    """A base exception for the FilesystemServer."""

    msg: str

    def __init__(self, msg: str):
        self.msg = msg

    def __str__(self) -> str:
        return self.msg


class FilesystemServerOutsideRootError(FilesystemServerError):
    """An exception for when a path is outside the permitted root."""

    def __init__(self, path: Path, root: Path):
        super().__init__(f"Path {path} is outside the permitted root {root}")


class FilesystemServerFileNotFoundError(FilesystemServerError):
    """An exception for when a file does not exist."""

    def __init__(self, path: Path):
        super().__init__(f"File {path} does not exist")


class FilesystemServer:
    """The main filesystem server for the FilesystemOperationsMCP."""

    root: Path

    def __init__(self, root: Path):
        self.root = root

    @classmethod
    def _resolve_path(cls, path: Path) -> Path:
        """Resolve a path to an absolute path."""
        if path.is_absolute():
            return path

        return path.resolve()

    def _resolve_and_validate(self, path: Path) -> Path:
        """Resolve a path to an absolute path and check if it is within the root."""
        resolved_path = self._resolve_path(path)

        try:
            resolved_path.relative_to(self.root.resolve())
        except ValueError as e:
            raise FilesystemServerOutsideRootError(resolved_path, self.root) from e

        return resolved_path

    def _resolve_and_validate_list(self, paths: list[Path]) -> list[Path]:
        """Resolve a list of paths to an absolute path and check if they are within the root."""
        return [self._resolve_and_validate(path) for path in paths]

    def _get_relative_path(self, path: Path) -> Path:
        """Get the relative path to the root."""
        return path.relative_to(self.root)

    # File Commands

    def file_exists(self, path: Path) -> bool:
        """Check if a file exists."""
        self._resolve_and_validate(path)

        return path.is_file()

    def delete_file(self, path: Path) -> None:
        """Delete a file."""
        self._resolve_and_validate(path)

        if not self.file_exists(path):
            raise FilesystemServerFileNotFoundError(path)

        path.unlink()

    def search_file(
        self, path: Path, search: str, search_is_regex: bool = False, before: int = 3, after: int = 3
    ) -> FileEntryChunkedContent | None:
        """Search a file for a string or regex pattern."""
        self._resolve_and_validate(path)

        return self._find_in_file(
            file=self._get_file(FileEntry, path), search=search, search_is_regex=search_is_regex, before=before, after=after
        )

    def create_file(self, path: Path, content: str) -> None:
        """Create a file."""
        self._resolve_and_validate(path)

        path.write_text(content)

    def append_file(self, path: Path, content: str) -> None:
        """Append to a file."""
        self._resolve_and_validate(path)

        current_content = path.read_text()
        path.write_text(current_content + content)

    def read_file(self, path: Path) -> str:
        """Read a file."""
        return self._get_file(FileEntryContent, path).content

    def preview_file(self, path: Path) -> str:
        """Preview a file."""
        result = self._get_file(FileEntryPreview, path)

        if result.preview:
            return result.preview

        return result.content

    def _get_file(self, entry_type: type[R], path: Path) -> R:
        """Get a file."""
        self._resolve_and_validate(path)

        return entry_type(absolute_path=path, root=self.root)

    # Directory Commands

    def dir_exists(self, path: Path) -> bool:
        """Check if a directory exists."""
        self._resolve_and_validate(path)

        return path.is_dir()

    def create_dir(self, path: Path) -> None:
        """Create a directory."""
        self._resolve_and_validate(path)

        path.mkdir(parents=True, exist_ok=True)

    def get_dir(self, path: Path) -> FlatDirectoryResult[FileEntry]:
        """Get a directory."""
        self._resolve_and_validate(path)

        return self.flat_dir(FileEntry, [path], recurse=False)

    @classmethod
    def _find_in_file(
        cls, file: FileEntry, search: str, search_is_regex: bool = False, before: int = 3, after: int = 3
    ) -> FileEntryChunkedContent | None:
        """Find a regex in a file."""
        chunks: list[FileEntryChunk] = []

        file_content = file.read_lines()

        for line_number, line in enumerate(file_content, start=1):
            before_lines: list[str] = []
            after_lines: list[str] = []
            chunk: FileEntryChunk | None = None

            if (search_is_regex and re.search(search, line)) or (not search_is_regex and search in line):
                before_lines = file_content[max(0, line_number - before - 1) : max(0, line_number - 1)]
                after_lines = file_content[min(len(file_content), line_number) : min(len(file_content), line_number + after)]

                before_lines = [line.strip() for line in before_lines]
                after_lines = [line.strip() for line in after_lines]

                chunk = FileEntryChunk(before=before_lines, match=line, after=after_lines, match_line_number=line_number)
                chunks.append(chunk)

        return FileEntryChunkedContent(absolute_path=file.absolute_path, root=file.root, chunks=chunks) if chunks else None

    def search_content(
        self,
        path: list[Path],
        search: str,
        recurse: bool,
        search_is_regex: bool = False,
        include: list[str] | None = None,
        exclude: list[str] | None = None,
        before: int = 3,
        after: int = 3,
    ) -> FlatDirectoryResult[FileEntryChunkedContent]:
        """Search the files in a directory for text or a regex pattern. Will not search files larger than 5mb.

        Args:
            path: The path to search.
            recurse: Whether to recurse into subdirectories.
            search: The string to search for.
            search_is_regex: Whether the search is a regex.
            include: A list of patterns to include.
            exclude: A list of patterns to exclude.
            before: The number of lines to include before the match.
            after: The number of lines to include after the match.

        Returns:
            A list of FileEntryChunkedContent objects.

        Example:
            >>> fs = FilesystemServer(Path("/home/user"))
            >>> fs.search_dir([Path("documents")], recurse=True, search="hello", is_regex=False, include=["*.txt"], exclude=["*.md"], before=3, after=3)
            [FileEntryChunkedContent(chunks=[FileEntryChunk(before=["This is a test"], match="hello", after=["This is a test"], match_line_number=1)])]
        """  # noqa: E501 Ignore long line length
        self._resolve_and_validate_list(path)

        flat_directory_result = self.flat_dir(FileEntry, path, recurse=recurse, include=include, exclude=exclude)
        new_flat_directory_result = FlatDirectoryResult[FileEntryChunkedContent]({})
        results: list[FileEntryChunkedContent] = []

        for dir_name, directory in flat_directory_result.root.items():
            for file_name, file in directory.items():
                if isinstance(file, SummaryDirectoryEntry) or file.size() > 5 * 1024 * 1024:
                    continue

                result = self._find_in_file(file=file, search=search, search_is_regex=search_is_regex, before=before, after=after)
                if result:
                    results.append(result)

                    if dir_name not in new_flat_directory_result.root:
                        new_flat_directory_result.root[dir_name] = {}

                    new_flat_directory_result.root[dir_name][file_name] = result

        return new_flat_directory_result

    def flat_dir(
        self,
        entry_type: type[R],
        path: list[Path] | None = None,
        recurse: bool = False,
        include: list[str] | None = None,
        exclude: list[str] | None = None,
    ) -> FlatDirectoryResult[R]:
        """Get an LLM-friendly flat directory result.

        Args:
            entry_type: The type of entry to return.
            path: The path to the directory to get.
            recurse: Whether to recurse into subdirectories.
            include: A list of patterns to include.
            exclude: A list of patterns to exclude.

        Returns:
            A flat directory result.

        Example:
            >>> fs = FilesystemServer(Path("/home/user"))
            >>> fs.flat_dir(FileEntry, [Path("documents")], recurse=True)
            FlatDirectoryResult(
                root={
                    "documents": {
                        "file1.txt": FileEntry(absolute_path=Path("/home/user/documents/file1.txt"), root=Path("/home/user")),
                    }
                }
            )
        """
        if path is None:
            path = [Path()]

        path = self._resolve_and_validate_list(path)

        flat_directory_result = FlatDirectoryResult[entry_type]({})

        walk = self._filtered_walk(path, recurse, include, exclude)

        files: set[Path] = set()
        directories: set[Path] = set()

        for child in walk:
            entry = self.root / child
            if entry.is_file():
                files.add(child)
                directories.add(child.parent)
            elif entry.is_dir():
                directories.add(child)

        # Now we render our flat directory result
        for directory in directories:
            # We want to use the relative path to the root for the keys in the flat directory result
            relative_directory = str(self._get_relative_path(directory))
            if relative_directory != ".":
                relative_directory = "./" + relative_directory

            # now we get all of the files that are in this directory from files
            files_in_dir = [child for child in files if child.parent == directory]

            # now we add the files to the flat directory result

            children = list(directory.glob("*"))

            entry = flat_directory_result.root.setdefault(relative_directory, {})

            entry.update(
                **{".": SummaryDirectoryEntry(absolute_path=directory, root=self.root, children=len(children))},
                **{child.name: entry_type(absolute_path=child, root=self.root) for child in files_in_dir},
            )

        return flat_directory_result

    def _filtered_walk(
        self, path: list[Path], recurse: bool, include: list[str] | None = None, exclude: list[str] | None = None
    ) -> list[Path]:
        """Walk a directory and filter the entries.

        Args:
            path: The path to the directory to walk.
            recurse: Whether to recurse into subdirectories.
            include: A list of patterns to include.
            exclude: A list of patterns to exclude.

        Returns:
            A list of paths.

        Example:
            >>> fs = FilesystemServer(Path("/home/user"))
            >>> fs._filtered_walk([Path("documents")], recurse=True, include=["*.txt"], exclude=["*.md"])
            [Path("/home/user/documents/file1.txt"), Path("/home/user/documents/file2.txt")]

            >>> fs._filtered_walk([Path("documents")], recurse=True, include=["*.txt"], exclude=["*.md"])
            [Path("/home/user/documents/file1.txt"), Path("/home/user/documents/file2.txt")]
        """
        entries = set()

        if not include:
            include = ["*"]

        if not exclude:
            exclude = []

        for p in path:
            joined_path = self.root / p
            self._resolve_and_validate(joined_path)

            glob_function = joined_path.rglob if recurse else joined_path.glob

            for this_include in include:
                entries.update(list(glob_function(this_include)))

        entries = list(entries)

        if exclude:
            entries = [e for e in entries if not any(fnmatch(e, this_exclude) for this_exclude in exclude)]

        return entries
