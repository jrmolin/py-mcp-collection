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

    @abstractmethod
    def verify(self, lines: list[str]) -> None:
        """Verifies the patch."""

    @classmethod
    def validate_line_numbers(cls, line_numbers: list[int], lines: list[str]) -> None:
        """User provided line numbers are 1-indexed, but the file has 0-indexed line numbers.

        This method converts the 1-indexed line numbers to 0-indexed line numbers and validates them.
        """
        line_count = len(lines)

        for line_number in line_numbers:
            if line_number < 1 or line_number > line_count:
                raise FilePatchIndexError(line_number, line_count)


class FileInsertPatch(BaseFilePatch):
    """A patch for inserting lines into a file.

    Example (Inserting line 1 before line 2):
    1: Line 1
    2: Line 2
    3: Line 3

    FileInsertPatch(start_line_number=2, current_line="Line 2", before_or_after="before", insert_lines=["New Line a", "New Line b"])

    1: Line 1
    2: New Line a
    3: New Line b
    4: line 2
    5: Line 3
    """

    patch_type: Literal["insert"] = Field(default="insert", exclude=True)
    """The type of patch."""

    start_line_number: int = Field(default=..., examples=[1], ge=1)
    """The line number to start inserting lines at."""

    before_or_after: Literal["before", "after"] = Field(default="before", examples=["before", "after"])
    """Whether to insert the lines before or after the `start_line_number`.

    If `before`, the lines will be inserted before the line at `start_line_number`.
    If `after`, the lines will be inserted after the line at `start_line_number`.
    """

    current_line: str = Field(default=..., examples=["the current line of text at the line number"])
    """To validate the patch, provide the current line of text at `start_line_number`."""

    insert_lines: list[str] = Field(
        default=..., examples=["Line 1 to insert before the current line", "Line 2 to insert after the current line"]
    )
    """The lines to insert before or after (depending on `before_or_after`) the `start_line_number`."""

    def _get_insert_file_line_number(self, lines: list[str]) -> int:
        """Gets the file line number for the patch."""
        if self.before_or_after == "before":
            return self.start_line_number - 1

        return self.start_line_number

    @override
    def verify(self, lines: list[str]) -> None:
        """Verifies the patch."""
        self.validate_line_numbers([self.start_line_number], lines)

        file_line = lines[self.start_line_number - 1]

        if self.current_line != file_line:
            raise FilePatchDoesNotMatchError(self.start_line_number, [self.current_line], [file_line])

    @override
    def apply(self, lines: list[str]) -> list[str]:
        """Applies the patch to the file."""
        self.verify(lines)

        file_line_number = self._get_insert_file_line_number(lines)
        return lines[:file_line_number] + self.insert_lines + lines[file_line_number:]


class FileAppendPatch(BaseFilePatch):
    """A patch for appending lines to a file.

    Example (Appending 2 new lines to the end of the file):
    1: Line 1
    2: Line 2
    3: Line 3

    FileAppendPatch(lines=["Line 4", "Line 5"])

    1: Line 1
    2: Line 2
    3: Line 3
    4: Line 4
    5: Line 5
    """

    patch_type: Literal["append"] = Field(default="append", exclude=True)
    """The type of patch."""

    lines: list[str] = Field(default=...)
    """The lines to append to the end of the file."""

    @override
    def verify(self, lines: list[str]) -> None:
        """Verifies the patch."""

    @override
    def apply(self, lines: list[str]) -> list[str]:
        """Applies the patch to the file."""
        return lines + self.lines


class FileDeletePatch(BaseFilePatch):
    """A patch to delete lines from a file.

    Example (Deleting line 1 and line 2):
    1: Line 1
    2: Line 2
    3: Line 3

    FileDeletePatch(line_numbers=[1, 2])

    1: Line 3
    """

    patch_type: Literal["delete"] = Field(default="delete", exclude=True)
    """The type of patch."""

    line_numbers: list[int] = Field(default=...)
    """The exact line numbers to delete from the file."""

    @override
    def verify(self, lines: list[str]) -> None:
        """Verifies the patch."""
        self.validate_line_numbers(self.line_numbers, lines)

    @override
    def apply(self, lines: list[str]) -> list[str]:
        """Applies the patch to the file."""
        self.verify(lines)

        file_line_numbers = [line_number - 1 for line_number in self.line_numbers]

        return [line for i, line in enumerate(lines) if i not in file_line_numbers]


class FileReplacePatch(BaseFilePatch):
    """A patch to replace lines in a file.

    Example (Finding line 1 and 2 and replacing them with just 1 new line):
    1: Line 1
    2: Line 2
    3: Line 3

    FileReplacePatch(start_line_number=1, current_lines=["Line 1", "Line 2"], new_lines=["New Line 1"])

    1: New Line 1
    2: Line 3
    """

    patch_type: Literal["replace"] = Field(default="replace", exclude=True)
    """The type of patch."""

    start_line_number: int = Field(default=..., ge=1)
    """The line number to start replacing at. The line at this number and the lines referenced in `current_lines` will be replaced.

    Line numbers are indexed from 1 and available via the read_file_lines tool.
    """

    current_lines: list[str] = Field(default=...)
    """To validate the patch, provide the lines as they exist now.

    Must match the lines at `start_line_number` to `start_line_number + len(current_lines) - 1` exactly.
    """

    new_lines: list[str] = Field(default=...)
    """The lines to replace the existing lines with.

    Does not have to match the length of `current_lines`.
    """

    def _get_start_end_line_numbers(self, lines: list[str]) -> tuple[int, int]:
        """Gets the start and end line numbers for the patch."""
        file_start_line_number = self.start_line_number - 1
        file_end_line_number = self.start_line_number + len(self.current_lines) - 1
        return file_start_line_number, file_end_line_number

    @override
    def verify(self, lines: list[str]) -> None:
        """Verifies the patch."""
        self.validate_line_numbers([self.start_line_number, self.start_line_number + len(self.current_lines) - 1], lines)

        file_start_line_number, file_end_line_number = self._get_start_end_line_numbers(lines)

        current_file_lines = lines[file_start_line_number:file_end_line_number]

        if current_file_lines != self.current_lines:
            raise FilePatchDoesNotMatchError(self.start_line_number, self.current_lines, current_file_lines)

    @override
    def apply(self, lines: list[str]) -> list[str]:
        """Applies the patch to the file."""
        self.verify(lines)

        file_start_line_number, file_end_line_number = self._get_start_end_line_numbers(lines)

        prepend_lines = lines[:file_start_line_number]
        append_lines = lines[file_end_line_number:]

        return prepend_lines + self.new_lines + append_lines


FilePatchTypes = FileInsertPatch | FileReplacePatch | FileDeletePatch | FileAppendPatch
FileMultiplePatchTypes = list[FileInsertPatch] | list[FileReplacePatch]
