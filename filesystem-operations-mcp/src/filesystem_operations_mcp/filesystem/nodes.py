import mimetypes
from collections.abc import AsyncIterator, Generator, Iterator
from contextlib import asynccontextmanager, contextmanager
from datetime import UTC, datetime
from enum import StrEnum
from fnmatch import fnmatch
from functools import cached_property
from io import TextIOWrapper
from os import stat_result
from pathlib import Path
from typing import Annotated, Any, ClassVar, Literal, Self, get_args

from aiofiles import open as aopen
from aiofiles.os import mkdir as amkdir
from aiofiles.os import remove as aremove
from aiofiles.os import rmdir as armdir
from aiofiles.threadpool.text import AsyncTextIOWrapper
from aioshutil import rmtree
from magika.types import ContentTypeInfo, Status
from magika.types.content_type_label import ContentTypeLabel
from pydantic import BaseModel, Field, RootModel
from pydantic.config import ConfigDict
from pydantic.fields import computed_field
from rpygrep import (
    RipGrepFind,
    RipGrepSearch,
)
from rpygrep.types import RIPGREP_TYPE_LIST, RipGrepContext, RipGrepSearchResult

from filesystem_operations_mcp.filesystem.detection.file_type import init_magika
from filesystem_operations_mcp.filesystem.errors import (
    DirectoryAlreadyExistsError,
    FileAlreadyExistsError,
    FileIsNotTextError,
    FilesystemServerOutsideRootError,
)
from filesystem_operations_mcp.filesystem.mappings.magika_to_tree_sitter import (
    TreeSitterLanguage,
    code_mappings,
    data_mappings,
    script_mappings,
    text_mappings,
)
from filesystem_operations_mcp.filesystem.patches.file import FileMultiplePatchTypes, FilePatchTypes
from filesystem_operations_mcp.logging import BASE_LOGGER

logger = BASE_LOGGER.getChild(__name__)

EXCLUDE_BINARY_TYPES: list[RIPGREP_TYPE_LIST] = [
    "avro",
    "brotli",
    "bzip2",
    "cbor",
    "flatbuffers",
    "gzip",
    "lz4",
    "lzma",
    "pdf",
    "protobuf",
    "thrift",
    "xz",
    "zstd",
]

EXCLUDE_EXTRA_TYPES: list[RIPGREP_TYPE_LIST] = [
    "lock",
    "minified",
    "jupyter",
    "log",
    "postscript",
    "svg",
    "usd",
]
EXCLUDE_DATA_TYPES: list[RIPGREP_TYPE_LIST] = ["csv", "jsonl", "json", "xml", "yaml", "toml"]

DEFAULT_EXCLUDED_TYPES: list[str] = sorted(EXCLUDE_BINARY_TYPES + EXCLUDE_EXTRA_TYPES + EXCLUDE_DATA_TYPES)


magika = init_magika()

PATTERNS_PARAM = Annotated[list[str], Field(description="A list of patterns to search for in the contents of the files.")]

BEFORE_CONTEXT_PARAM = Annotated[int, Field(description="The number of lines of context to include before the match.")]
AFTER_CONTEXT_PARAM = Annotated[int, Field(description="The number of lines of context to include after the match.")]

INCLUDE_FILES_GLOBS = Annotated[list[str] | str | None, Field(description="A list of globs to include in the search.")]
EXCLUDE_FILES_GLOBS = Annotated[list[str] | str | None, Field(description="A list of globs to exclude from the search.")]

DEPTH_PARAM = Annotated[int, Field(description="The depth of the search.")]
MATCHES_PER_FILE_PARAM = Annotated[int, Field(description="The maximum number of matches to return per file.")]

CASE_SENSITIVE_PARAM = Annotated[bool, Field(description="Whether the search should be case sensitive.")]


class BaseNode(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(arbitrary_types_allowed=True, frozen=True, use_attribute_docstrings=True)

    path: Path = Field(exclude=True)
    """The absolute path of the node."""

    def __init__(self, path: Path, **kwargs: Any) -> None:  # pyright: ignore[reportAny]
        if not path.is_absolute():
            path = path.resolve()
        super().__init__(path=path, **kwargs)

    @computed_field
    @property
    def name(self) -> str:
        return self.path.name

    @property
    def parent(self) -> "BaseNode":
        return BaseNode(path=self.path.parent)

    @property
    def parent_path(self) -> Path:
        return self.path.parent

    @cached_property
    def _stat(self) -> stat_result:
        return self.path.stat()

    @computed_field
    @property
    def created_at(self) -> str:
        return datetime.fromtimestamp(self._stat.st_ctime, tz=UTC).isoformat()

    @computed_field
    @property
    def modified_at(self) -> str:
        return datetime.fromtimestamp(self._stat.st_mtime, tz=UTC).isoformat()

    def relative_to(self, node: "BaseNode") -> Path:
        """The relative path of the node from the given path or node."""

        try:
            return self.path.relative_to(node.path)
        except ValueError as ve:
            raise FilesystemServerOutsideRootError(self.path, node.path) from ve

    def is_descendant_of(self, ancestor: "BaseNode") -> bool:
        """Whether the node is a descendant of the given path or node."""

        return self.path.is_relative_to(ancestor.path)

    @computed_field
    @property
    def owner(self) -> int:
        return self._stat.st_uid

    @computed_field
    @property
    def group(self) -> int:
        return self._stat.st_gid

    @property
    def is_file(self) -> bool:
        return self.path.is_file()

    @property
    def is_dir(self) -> bool:
        return self.path.is_dir()


class FileSystemEntry(BaseNode):
    filesystem: "BaseNode" = Field(exclude=True)

    def __init__(self, path: Path, filesystem: "BaseNode", **kwargs: Any) -> None:  # pyright: ignore[reportAny]
        if not path.is_absolute():
            path = (filesystem.path / path).resolve()

        super().__init__(path=path, filesystem=filesystem, **kwargs)

    @computed_field
    @property
    def relative_path(self) -> Path:
        return self.relative_to(self.filesystem)

    @computed_field
    @property
    def relative_path_str(self) -> str:
        return str(self.relative_path)

    def passes_filters(
        self,
        includes: list[str] | None = None,
        excludes: list[str] | None = None,
    ) -> bool:
        """Checks if the node passes the include and exclude filters.

        Args:
            includes: A list of globs to include in the search.
            excludes: A list of globs to exclude from the search.

        Returns:
            True if the node passes the filters, False otherwise.
        """
        if includes is None and excludes is None:
            return True

        relative_path_str = str(self.relative_path)

        if includes is not None and not any(fnmatch(relative_path_str, include) for include in includes):
            return False

        if excludes is not None and any(fnmatch(relative_path_str, exclude) for exclude in excludes):  # noqa: SIM103
            return False

        return True


class FileLines(RootModel[dict[int, str]]):
    root: dict[int, str] = Field(
        default_factory=dict,
        description="A set of key-value pairs where the key is the line number and the value is the line of text at that line number.",
    )

    def lines(self) -> list[str]:
        return list(self.root.values())

    def line_numbers(self) -> list[int]:
        return list(self.root.keys())

    def first(self, count: int) -> "FileLines":
        return FileLines(root={k: v for k, v in self.root.items() if k < count})


class FileEntryMatch(BaseModel):
    before: FileLines = Field(default_factory=FileLines, description="The lines of text before the line")
    match: FileLines = Field(default_factory=FileLines, description="The line of text that matches the pattern")
    after: FileLines = Field(default_factory=FileLines, description="The lines of text after the line")


class FileEntryTypeEnum(StrEnum):
    CODE = "code"
    TEXT = "text"
    DATA = "data"
    BINARY = "binary"
    UNKNOWN = "unknown"


class FileEntry(FileSystemEntry):
    """A file entry in the virtual filesystem."""

    @computed_field
    @property
    def stem(self) -> str:
        """The stem of the file."""
        return self.path.stem

    # @property
    # def path(self) -> str:
    #     """The path of the file."""
    #     return str(self.path)

    @computed_field
    @property
    def extension(self) -> str:
        """The extension of the file."""
        return self.path.suffix

    @computed_field
    @property
    def size(self) -> int:
        """The size of the file in bytes."""
        return self._stat.st_size

    @computed_field
    @cached_property
    def type(self) -> FileEntryTypeEnum:  # noqa: PLR0911
        # Hardcoded rules for data files
        if self.extension in {".yml", ".yaml", ".json", ".log", ".csv", ".tsv", ".jsonl"}:
            return FileEntryTypeEnum.DATA
        if self.extension in {".md", ".markdown", ".asciidoc", ".txt"}:
            return FileEntryTypeEnum.TEXT

        # detect binary via mimetype
        if is_binary_mime_type(self.mime_type):
            return FileEntryTypeEnum.BINARY

        # Allow magika to detect the type
        if self.magika_content_type_label in code_mappings or self.magika_content_type_label in script_mappings:
            return FileEntryTypeEnum.CODE
        if self.magika_content_type_label in text_mappings:
            return FileEntryTypeEnum.TEXT
        if self.magika_content_type_label in data_mappings:
            return FileEntryTypeEnum.DATA

        return FileEntryTypeEnum.UNKNOWN

    @cached_property
    def magika_content_type(self) -> ContentTypeInfo | None:
        result = magika.identify_path(self.path)  # pyright: ignore[reportUnknownMemberType]
        if result.status != Status.OK:
            return None
        return result.output

    @cached_property
    def tree_sitter_language(self) -> TreeSitterLanguage | None:
        if self.magika_content_type_label and self.magika_content_type_label in code_mappings:
            return code_mappings[self.magika_content_type_label]

        return None

    @property
    def magika_content_type_label(self) -> ContentTypeLabel | None:
        if self.magika_content_type:
            return self.magika_content_type.label
        return None

    @computed_field
    @cached_property
    def mime_type(self) -> str:
        return mimetypes.guess_type(self.path)[0] or "unknown"

    @asynccontextmanager
    async def _aopen(self, mode: Literal["r", "w", "a"]) -> AsyncIterator[AsyncTextIOWrapper]:
        if self.type == FileEntryTypeEnum.BINARY:
            raise FileIsNotTextError(path=self.path)

        async with aopen(self.path, mode=mode, encoding="utf-8") as f:
            yield f

    @contextmanager
    def _open(self, mode: Literal["r", "w", "a"]) -> Iterator[TextIOWrapper]:
        if self.type == FileEntryTypeEnum.BINARY:
            raise FileIsNotTextError(path=self.path)

        with self.path.open(mode=mode) as f:
            yield f

    def text(self, size: int | None = None) -> str:
        """The contents of the file as text."""
        with self._open(mode="r") as f:
            return f.read(size)

    def lines_iter(self) -> Iterator[str]:
        """The lines of the file as a list of strings."""
        with self._open(mode="r") as f:
            while line := f.readline():
                yield line.rstrip()

    def lines(self, count: int | None = None) -> list[str]:
        """The lines of the file as a list of strings."""
        lines_iter = self.lines_iter()

        lines: list[str] = []

        for line in lines_iter:
            lines.append(line)
            if count is not None and len(lines) >= count:
                break

        return lines

    def file_lines(self, count: int | None = None) -> FileLines:
        """The lines of the file as a list of strings."""
        lines_iter = self.lines_iter()

        lines: dict[int, str] = {}

        for line in lines_iter:
            lines[len(lines) + 1] = line
            if count is not None and len(lines) >= count:
                break

        return FileLines(root=lines)

    async def atext(self, size: int | None = None) -> str:
        """The contents of the file as text."""
        async with self._aopen(mode="r") as f:
            return await f.read(size)

    async def alines_iter(self) -> AsyncIterator[str]:
        """The lines of the file as a list of strings."""
        async with self._aopen(mode="r") as f:
            while line := await f.readline():
                yield line.rstrip()

    async def alines(self, count: int | None = None) -> list[str]:
        """The lines of the file as a list of strings."""
        alines_iter = self.alines_iter()

        lines: list[str] = []

        async for line in alines_iter:
            lines.append(line)
            if count is not None and len(lines) >= count:
                break

        return lines

    async def afile_lines(self, count: int | None = None, start: int = 1) -> FileLines:
        """The lines of the file as a list of strings.

        Args:
            start: The index-1 line number to start reading from.
            count: The number of lines to read.
        """
        afile_lines_iter = self.alines_iter()

        lines: dict[int, str] = {}
        current_line_number: int = 1

        async for line in afile_lines_iter:
            if current_line_number >= start:
                lines[current_line_number] = line

            if count is not None and len(lines) >= count:
                break

            current_line_number += 1

        return FileLines(root=lines)

    async def delete(self) -> None:
        """Deletes the file."""
        await aremove(self.path)

    async def apply_patch(self, patch: FilePatchTypes) -> None:
        """Applies the patch to the file."""
        file_lines = await self.afile_lines()
        lines = patch.apply(file_lines.lines())
        await self.save(lines)

    async def apply_patches(self, patches: FileMultiplePatchTypes) -> None:
        """Applies the patches to the file."""
        lines = await self.alines()

        # Reverse the patches if they are a list so that they are applied in the correct order.
        patches_to_apply: list[FilePatchTypes] = list(reversed(patches))

        for patch in patches_to_apply:
            lines = patch.apply(lines)

        await self.save(lines)

    async def save(self, lines: list[str]) -> None:
        """Saves the file with the given lines."""
        async with aopen(self.path, mode="w", encoding="utf-8") as f:
            _ = await f.write("\n".join(lines))

    @classmethod
    async def create_file(cls, path: Path, content: str) -> None:
        """Creates a file."""
        if path.exists():
            raise FileAlreadyExistsError(path=path)

        async with aopen(path, mode="w", encoding="utf-8") as f:
            _ = await f.write(content)


class FileEntryWithMatches(FileEntry):
    """A file entry with matches."""

    matches: FileLines = Field(default_factory=FileLines, description="The matches of the file.")

    matches_limit_reached: bool = Field(default=False, description="Whether the matches limit was reached.")

    @classmethod
    def from_file_entry(cls, file_entry: FileEntry, matches: FileLines) -> "FileEntryWithMatches":
        return cls(path=file_entry.path, filesystem=file_entry.filesystem, matches=matches)


# class FileEntryWithMatches(FileEntry):
#     matches: list[FileEntryMatch] = Field(default_factory=list, description="The matches of the file.")

#     @classmethod
#     def from_file_entry(cls, file_entry: FileEntry, matches: list[FileEntryMatch]) -> "FileEntryWithMatches":
#         return cls(path=file_entry.path, filesystem=file_entry.filesystem, matches=matches)


class DirectoryEntry(FileSystemEntry):
    """A directory entry in the virtual filesystem."""

    async def aget_files(self, paths: list[str | Path]) -> AsyncIterator[FileEntry]:
        """Get a list of specific file entries by path."""
        for path in paths:
            yield self.get_file(path)

    def get_file(self, path: str | Path) -> FileEntry:
        """Get a specific file entry by path."""

        return FileEntry(path=self.path / path, filesystem=self)

    def get_directory(self, path: str | Path) -> "DirectoryEntry":
        """Get a specific directory entry by path."""

        return DirectoryEntry(path=self.path / path, filesystem=self)

    def get_descendent_directories(self, root: "DirectoryEntry", depth: int) -> Generator["DirectoryEntry"]:
        """Get a list of child directory entries by path."""
        if depth == 0:
            return

        # Recurse
        for path in self.path.iterdir():
            if path.is_dir() and not path.name.startswith("."):
                directory_entry = DirectoryEntry(path=path, filesystem=root)
                yield directory_entry
                if depth > 1:
                    yield from directory_entry.get_descendent_directories(root=root, depth=depth - 1)

    @property
    def _ripgrep_find(self) -> RipGrepFind:
        return RipGrepFind(working_directory=self.path).one_file_system().max_depth(10)

    @property
    def _ripgrep_search(self) -> RipGrepSearch:
        return RipGrepSearch(working_directory=self.path).auto_hybrid_regex().one_file_system().max_depth(10)

    async def afind_files(
        self,
        *,
        included_globs: INCLUDE_FILES_GLOBS = None,
        excluded_globs: EXCLUDE_FILES_GLOBS = None,
        included_types: Annotated[
            list[str] | None,
            Field(description="The types (not extensions!) of files to search for."),
        ] = None,
        excluded_types: Annotated[
            list[str] | None,
            Field(
                description="""The types (not extensions!) of files to exclude from the search.
                Many common types are excluded by default, be sure to overwrite the default if you want to include them.
                """
            ),
        ] = DEFAULT_EXCLUDED_TYPES,
        max_depth: DEPTH_PARAM = 6,
    ) -> AsyncIterator[FileEntry]:
        """Find files in the directory using a mix of Globs and types, with the ability to limit the depth of the search.

        Honors gitignore files. If no globs are provided, all non-ignored files are in scope."""
        included_globs_list, excluded_globs_list, included_type_list, excluded_type_list = prepare_ripgrep_arguments(
            included_globs, excluded_globs, included_types, excluded_types
        )

        ripgrep = (
            self._ripgrep_find.include_types(included_type_list)
            .exclude_types(excluded_type_list)
            .include_globs(included_globs_list)
            .exclude_globs(excluded_globs_list)
            .max_depth(max_depth)  # Don't fold
        )

        async for matched_path in ripgrep.arun():
            file_entry = FileEntry(path=self.path / matched_path, filesystem=self.filesystem)
            yield file_entry

    async def asearch_files(
        self,
        patterns: PATTERNS_PARAM,
        *,
        included_globs: INCLUDE_FILES_GLOBS = None,
        excluded_globs: EXCLUDE_FILES_GLOBS = None,
        included_types: Annotated[
            list[str] | None,
            Field(description="The types (not extensions!) of files to search for."),
        ] = None,
        excluded_types: Annotated[
            list[str] | None,
            Field(
                description="""The types (not extensions!) of files to exclude from the search.
                Many common types are excluded by default, be sure to overwrite the default if you want to include them.
                """
            ),
        ] = DEFAULT_EXCLUDED_TYPES,
        before_context: BEFORE_CONTEXT_PARAM = 1,
        after_context: AFTER_CONTEXT_PARAM = 1,
        max_depth: DEPTH_PARAM = 6,
        matches_per_file: MATCHES_PER_FILE_PARAM = 3,
        case_sensitive: CASE_SENSITIVE_PARAM = False,
    ) -> AsyncIterator[FileEntryWithMatches]:
        """Search the contents of files in the filesystem using a mix of Globs and types, with the ability to limit the depth
        of the search.

        Honors gitignore files. If no patterns are provided, no files are returned.

        This operation is functionally similar to a `grep` command.
        """
        included_globs_list, excluded_globs_list, included_type_list, excluded_type_list = prepare_ripgrep_arguments(
            included_globs, excluded_globs, included_types, excluded_types
        )

        ripgrep = (
            self._ripgrep_search.add_safe_defaults()
            .include_types(included_type_list)
            .exclude_types(excluded_type_list)
            .include_globs(included_globs_list)
            .exclude_globs(excluded_globs_list)
            .before_context(before_context)
            .after_context(after_context)
            .add_patterns(patterns)
            .max_depth(max_depth)
            .max_count(matches_per_file)
            .case_sensitive(case_sensitive)
        )

        result: AsyncIterator[RipGrepSearchResult] = ripgrep.arun()

        async for file_match in result:
            yield FileEntryWithMatches(
                path=file_match.path,
                filesystem=self.filesystem,
                matches=search_result_to_file_lines(file_match),
                matches_limit_reached=len(file_match.matches) >= matches_per_file,
            )

    async def create_directory(
        self,
        path: Annotated[Path, Field(description="The relative path of the directory to create.")],
    ) -> None:
        """Creates a directory

        Returns:
            None if the directory was created successfully, otherwise an error message.
        """
        path = self.path / path

        if path.exists():
            raise DirectoryAlreadyExistsError(path=path)

        if not path.is_relative_to(self.filesystem.path):
            raise FilesystemServerOutsideRootError(path, self.filesystem.path)

        await amkdir(path)

    async def delete_directory(
        self,
        path: Annotated[Path, Field(description="The relative path of the directory to delete.")],
        recursive: Annotated[bool, Field(description="Also delete the contents of the directory, and do it recursively.")] = False,
    ) -> None:
        """Deletes a directory."""

        path = self.path / path

        if not path.is_relative_to(self.filesystem.path):
            raise FilesystemServerOutsideRootError(path, self.filesystem.path)

        if recursive:
            await rmtree(path)
            return

        await armdir(path)


def is_binary_mime_type(mime_type: str) -> bool:
    if mime_type.startswith(("image/", "video/", "audio/")):
        return True

    if mime_type.startswith("application/") and not (mime_type.endswith(("json", "xml"))):  # noqa: SIM103
        return True

    return False


def search_result_to_file_lines(search_result: RipGrepSearchResult) -> FileLines:
    return FileLines(
        root={
            line.data.line_number: line.data.lines.text.rstrip()[:100]  # Limit to 100 characters to avoid bloating the response
            for line in [*search_result.matches, *search_result.context]
            if line.data.lines.text and line.data.lines.text.rstrip()
        }
    )


def search_result_to_file_entry_matches(
    search_result: RipGrepSearchResult, before_context: int, after_context: int
) -> list[FileEntryMatch]:
    line_context_by_line_number: dict[int, RipGrepContext] = {context.data.line_number: context for context in search_result.context}

    file_entry_matches: list[FileEntryMatch] = []

    for line_match in search_result.matches:
        if not line_match.data.lines.text:
            continue

        before_context_lines: FileLines = FileLines(root={})
        after_context_lines: FileLines = FileLines(root={})

        # Find the before context lines
        for line_number in range(line_match.data.line_number - before_context, line_match.data.line_number):
            if line := line_context_by_line_number.pop(line_number, None):  # noqa: SIM102
                if text := line.data.lines.text:  # noqa: SIM102
                    if stripped_line := text.rstrip():
                        before_context_lines.root[line_number] = stripped_line

        # Find the after context lines
        for line_number in range(line_match.data.line_number + 1, line_match.data.line_number + after_context + 1):
            if line := line_context_by_line_number.pop(line_number, None):  # noqa: SIM102
                if text := line.data.lines.text:  # noqa: SIM102
                    if stripped_line := text.rstrip():
                        after_context_lines.root[line_number] = stripped_line

        file_entry_matches.append(
            FileEntryMatch(
                before=before_context_lines,
                match=FileLines(root={line_match.data.line_number: line_match.data.lines.text.rstrip()}),
                after=after_context_lines,
            )
        )

    return file_entry_matches


def prepare_ripgrep_arguments(
    included_globs: INCLUDE_FILES_GLOBS,
    excluded_globs: EXCLUDE_FILES_GLOBS,
    included_types: list[str] | str | None,
    excluded_types: list[str] | str | None,
) -> tuple[list[str], list[str], list[RIPGREP_TYPE_LIST], list[RIPGREP_TYPE_LIST]]:
    if included_globs is None:
        included_globs = []

    if excluded_globs is None:
        excluded_globs = []

    if isinstance(included_globs, str):
        included_globs = [included_globs]

    if isinstance(excluded_globs, str):
        excluded_globs = [excluded_globs]

    included_type_list: list[RIPGREP_TYPE_LIST] = []
    excluded_type_list: list[RIPGREP_TYPE_LIST] = []

    if included_types:
        included_type_list = [t for t in included_types if t in get_args(RIPGREP_TYPE_LIST)]  # pyright: ignore[reportAssignmentType]

    if excluded_types:
        excluded_type_list = [t for t in excluded_types if t in get_args(RIPGREP_TYPE_LIST)]  # pyright: ignore[reportAssignmentType]

    return included_globs, excluded_globs, included_type_list, excluded_type_list
