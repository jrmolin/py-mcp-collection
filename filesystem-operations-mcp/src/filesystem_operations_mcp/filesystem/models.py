from pathlib import Path
import re
from typing import TypeVar

from pydantic import BaseModel, Field, RootModel, computed_field

PREVIEW_SIZE = 400


class BaseFileEntry(BaseModel):
    absolute_path: Path = Field(exclude=True)
    root: Path = Field(exclude=True)

    def size(self) -> int:
        return self.absolute_path.stat().st_size

    def read(self) -> str:
        with self.absolute_path.open("r") as f:
            return f.read()

    def preview(self, head: int) -> str:
        with self.absolute_path.open("r") as f:
            return f.read(head)

    def contents_match(self, pattern: str) -> list[int]:
        """Searches for a pattern in the file and returns the line numbers of the matches."""
        return [i for i, line in enumerate(self.read_lines()) if pattern in line]

    def contents_match_regex(self, pattern: str) -> list[int]:
        """Searches for a regex pattern in the file and returns the line numbers of the matches."""
        return [i for i, line in enumerate(self.read_lines()) if re.search(pattern, line)]

    def read_lines(self) -> list[str]:
        with self.absolute_path.open("r") as f:
            return f.readlines()


type FileEntryTypes = FileEntry | FileEntryPreview | FileEntryContent |  FileEntryWithSize | FileEntryWithNameAndContent

T = TypeVar("T", bound=FileEntryTypes)


class FileEntry(BaseFileEntry):
    pass


class FileEntryWithSize(BaseFileEntry):
    @computed_field
    def size(self) -> int:
        return self.absolute_path.stat().st_size


class FileEntryPreview(FileEntryWithSize):

    @computed_field
    def content(self) -> str | None:
        if self.size() <= PREVIEW_SIZE:
            return self.read()

        return None

    @computed_field
    def preview(self) -> str | None:
        if self.size() > PREVIEW_SIZE:
            return self.read(PREVIEW_SIZE) + "..."

        return None


class FileEntryNotFound(BaseFileEntry):

    @computed_field
    def error(self) -> str:
        return f"File {self.absolute_path} does not exist"


class FileEntryWithNameAndContent(BaseFileEntry):

    @computed_field
    def path(self) -> Path:
        return self.absolute_path.relative_to(self.root)

    @computed_field
    def content(self) -> str:
        return self.read()


class FileEntryContent(FileEntryWithSize):

    @computed_field
    def content(self) -> str:
        return self.read()


class FileEntryChunk(BaseModel):
    before: list[str] = Field(description="The lines before the match.")
    match: str = Field(description="The line with the match..")
    after: list[str] = Field(description="The lines after the match.")
    match_line_number: int = Field(description="The line number of the match in the file.")


class FileEntryChunkedContent(BaseFileEntry):
    chunks: list[FileEntryChunk]


class SummaryDirectoryEntry(BaseModel):
    absolute_path: Path = Field(exclude=True)
    root: Path = Field(exclude=True)
    children: int


class FlatDirectoryResult[T: FileEntryTypes](RootModel[dict[str, dict[str, SummaryDirectoryEntry | T]]]):
    pass
