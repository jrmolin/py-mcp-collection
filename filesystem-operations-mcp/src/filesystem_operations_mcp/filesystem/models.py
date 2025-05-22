from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel, Field, RootModel, computed_field

PREVIEW_SIZE = 400


class BaseFileEntry(BaseModel):
    absolute_path: Path = Field(exclude=True)
    root: Path = Field(exclude=True)

    def size(self) -> int:
        return self.absolute_path.stat().st_size

    def read(self, head: int | None = None) -> str:
        with self.absolute_path.open("r") as f:
            return f.read(head)

    def read_lines(self) -> list[str]:
        with self.absolute_path.open("r") as f:
            return f.readlines()


type FileEntryTypes = FileEntry | FileEntryPreview | FileEntryContent | FileEntryChunkedContent | FileEntryWithSize

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
        if self.size <= PREVIEW_SIZE:
            return self.read()

        return None

    @computed_field
    def preview(self) -> str | None:
        if self.size > PREVIEW_SIZE:
            return self.read(PREVIEW_SIZE) + "..."

        return None


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
