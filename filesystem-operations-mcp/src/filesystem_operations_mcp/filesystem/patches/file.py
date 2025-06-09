from abc import ABC, abstractmethod
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from filesystem_operations_mcp.filesystem.errors import FilePatchDoesNotMatchError, FilePatchIndexError


class BaseFilePatch(BaseModel, ABC):
    """A base class for file patches."""

    patch_type: Literal["insert", "replace", "delete", "append"] = Field(...)
    """The type of patch."""

    model_config = ConfigDict(use_attribute_docstrings=True)

    @abstractmethod
    def apply(self, lines: list[str]) -> list[str]:
        """Applies the patch to the file."""

    @classmethod
    def validate_line_numbers(cls, line_numbers: list[int], lines: list[str]) -> None:
        """Checks if the line numbers are valid."""
        line_count = len(lines)

        for line_number in line_numbers:
            if line_number < 0 or line_number >= line_count:
                raise FilePatchIndexError(line_number, line_count)


class FileInsertPatch(BaseFilePatch):
    """A patch for inserting lines into a file."""

    patch_type: Literal["insert"] = "insert"
    """The type of patch."""

    line_number: int = Field(...)
    """The line number to insert the lines at."""

    current_line: str = Field(...)
    """The current line of text at `line_number`, new lines will be inserted immediately before this line."""

    lines: list[str] = Field(...)
    """The lines to insert into the file."""

    def apply(self, lines: list[str]) -> list[str]:
        """Applies the patch to the file."""
        self.validate_line_numbers([self.line_number], lines)

        file_line = lines[self.line_number]

        if self.current_line != file_line:
            raise FilePatchDoesNotMatchError(self.line_number, [self.current_line], [file_line])

        return lines[: self.line_number] + self.lines + lines[self.line_number :]


class FileAppendPatch(BaseFilePatch):
    """A patch for appending lines to a file."""

    patch_type: Literal["append"] = "append"
    """The type of patch."""

    lines: list[str] = Field(...)
    """The lines to append to the end of thefile."""

    def apply(self, lines: list[str]) -> list[str]:
        """Applies the patch to the file."""
        return lines + self.lines


class FileDeletePatch(BaseFilePatch):
    """A patch to delete lines from a file."""

    patch_type: Literal["delete"] = "delete"
    """The type of patch."""

    line_numbers: list[int] = Field(...)
    """The exact line numbers to delete from the file."""

    def apply(self, lines: list[str]) -> list[str]:
        """Applies the patch to the file."""
        self.validate_line_numbers(self.line_numbers, lines)

        return [line for i, line in enumerate(lines) if i not in self.line_numbers]


class FileReplacePatch(BaseFilePatch):
    """A patch to replace lines in a file."""

    patch_type: Literal["replace"] = "replace"
    """The type of patch."""

    start_line_number: int = Field(...)
    """The line number to start replacing at. The line at this number and the lines referenced in `current_lines` will be replaced."""

    current_lines: list[str] = Field(...)
    """The lines to replace. Must match the lines at `start_line_number` to `start_line_number + len(current_lines) - 1` exactly."""

    new_lines: list[str] = Field(...)
    """The lines to replace the existing lines with. Does not have to match the length of `current_lines`."""

    def apply(self, lines: list[str]) -> list[str]:
        """Applies the patch to the file."""
        self.validate_line_numbers([self.start_line_number, self.start_line_number + len(self.current_lines) - 1], lines)

        end_line_number = self.start_line_number + len(self.current_lines)

        file_lines = lines[self.start_line_number : end_line_number]

        if file_lines != self.current_lines:
            raise FilePatchDoesNotMatchError(self.start_line_number, self.current_lines, file_lines)

        prepend_lines = lines[: self.start_line_number]
        append_lines = lines[end_line_number:]

        return prepend_lines + self.new_lines + append_lines


FilePatchTypes = FileInsertPatch | FileReplacePatch | FileDeletePatch | FileAppendPatch
FileMultiplePatchTypes = list[FileInsertPatch] | list[FileReplacePatch]
