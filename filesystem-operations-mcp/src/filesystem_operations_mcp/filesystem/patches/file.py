from abc import ABC, abstractmethod
from typing import ClassVar, Literal, override

from pydantic import BaseModel, ConfigDict, Field

from filesystem_operations_mcp.filesystem.errors import FilePatchDoesNotMatchError, FilePatchIndexError


class BaseFilePatch(BaseModel, ABC):  # pyright: ignore[reportUnsafeMultipleInheritance]
    """A base class for file patches."""

    # patch_type: Literal["insert", "replace", "delete", "append"] = Field(...)
    # """The type of patch."""

    model_config: ClassVar[ConfigDict] = ConfigDict(use_attribute_docstrings=True)

    @abstractmethod
    def apply(self, lines: list[str]) -> list[str]:
        """Applies the patch to the file."""

    @classmethod
    def validate_line_numbers(cls, line_numbers: list[int], lines: list[str]) -> None:
        """Checks if the index 1-based line numbers are valid to the index 0-based line numbers array."""
        line_count = len(lines)

        for line_number in line_numbers:
            if line_number < 1 or line_number > line_count:
                raise FilePatchIndexError(line_number, line_count)


class FileInsertPatch(BaseFilePatch):
    """A patch for inserting lines into a file."""

    patch_type: Literal["insert"] = Field(default="insert", exclude=True)
    """The type of patch."""

    line_number: int = Field(..., examples=[1])
    """The line number to apply the patch to. `lines` will be inserted immediately before the line at `line_number`.
    Line numbers are indexed from 1 and available via the read_file_lines tool.
    """

    current_line: str = Field(..., examples=["the current line of text at the line number"])
    """To validate the patch, provide the current line of text at `line_number`."""

    lines: list[str] = Field(..., examples=["Line 1 to insert before the current line", "Line 2 to insert after the current line"])
    """The lines to insert immediately before `line_number`, i.e. immediately before `current_line`."""

    @override
    def apply(self, lines: list[str]) -> list[str]:
        """Applies the patch to the file."""
        self.validate_line_numbers([self.line_number], lines)

        file_line_number = self.line_number - 1
        file_line = lines[file_line_number]

        if self.current_line != file_line:
            raise FilePatchDoesNotMatchError(self.line_number, [self.current_line], [file_line])

        return lines[:file_line_number] + self.lines + lines[file_line_number:]


class FileAppendPatch(BaseFilePatch):
    """A patch for appending lines to a file."""

    patch_type: Literal["append"] = Field(default="append", exclude=True)
    """The type of patch."""

    lines: list[str] = Field(...)
    """The lines to append to the end of thefile."""

    @override
    def apply(self, lines: list[str]) -> list[str]:
        """Applies the patch to the file."""
        return lines + self.lines


class FileDeletePatch(BaseFilePatch):
    """A patch to delete lines from a file."""

    patch_type: Literal["delete"] = Field(default="delete", exclude=True)
    """The type of patch."""

    line_numbers: list[int] = Field(...)
    """The exact line numbers to delete from the file."""

    @override
    def apply(self, lines: list[str]) -> list[str]:
        """Applies the patch to the file."""
        self.validate_line_numbers(self.line_numbers, lines)

        file_line_numbers = [line_number - 1 for line_number in self.line_numbers]

        return [line for i, line in enumerate(lines) if i not in file_line_numbers]


class FileReplacePatch(BaseFilePatch):
    """A patch to replace lines in a file."""

    patch_type: Literal["replace"] = Field(default="replace", exclude=True)
    """The type of patch."""

    start_line_number: int = Field(...)
    """The line number to start replacing at. The line at this number and the lines referenced in `current_lines` will be replaced.

    Line numbers are indexed from 1 and available via the read_file_lines tool.
    """

    current_lines: list[str] = Field(...)
    """To validate the patch, provide the lines as they exist now.

    Must match the lines at `start_line_number` to `start_line_number + len(current_lines) - 1` exactly.
    """

    new_lines: list[str] = Field(...)
    """The lines to replace the existing lines with.

    Does not have to match the length of `current_lines`.
    """

    @override
    def apply(self, lines: list[str]) -> list[str]:
        """Applies the patch to the file."""
        self.validate_line_numbers([self.start_line_number, self.start_line_number + len(self.current_lines) - 1], lines)

        file_start_line_number = self.start_line_number - 1
        file_end_line_number = self.start_line_number + len(self.current_lines) - 1

        current_file_lines = lines[file_start_line_number:file_end_line_number]

        if current_file_lines != self.current_lines:
            raise FilePatchDoesNotMatchError(self.start_line_number, self.current_lines, current_file_lines)

        prepend_lines = lines[:file_start_line_number]
        append_lines = lines[file_end_line_number:]

        return prepend_lines + self.new_lines + append_lines


FilePatchTypes = FileInsertPatch | FileReplacePatch | FileDeletePatch | FileAppendPatch
FileMultiplePatchTypes = list[FileInsertPatch] | list[FileReplacePatch]
