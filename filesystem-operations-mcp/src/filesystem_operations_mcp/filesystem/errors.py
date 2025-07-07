from pathlib import Path


class FilesystemServerError(Exception):
    """A base exception for the FilesystemServer."""

    msg: str

    def __init__(self, msg: str):
        self.msg = msg
        super().__init__(msg)

    def __str__(self) -> str:
        return self.msg


class FilesystemServerOutsideRootError(FilesystemServerError):
    """An exception for when a path is outside the permitted root."""

    def __init__(self, path: Path, root: Path):
        super().__init__(f"Path {path} is outside the permitted root {root}")


class FilesystemServerResponseTooLargeError(FilesystemServerError):
    """An exception for when a response is too large to return."""

    def __init__(self, response_size: int, max_size: int):
        super().__init__(f"Response size {response_size} is too large to return. Max size is {max_size} bytes.")


class FilesystemServerTooBigToSummarizeError(FilesystemServerError):
    """An exception for when a result set is too large to summarize."""

    def __init__(self, result_set_size: int, max_size: int):
        super().__init__(f"Result set size {result_set_size} is too large to summarize. Max size is {max_size} files.")


class DirectoryNotFoundError(FilesystemServerError):
    """An exception for when a directory does not exist."""

    def __init__(self, path: Path):
        super().__init__(f"Directory {path} does not exist.")


class DirectoryNotEmptyError(FilesystemServerError):
    """An exception for when a directory is not empty."""

    def __init__(self, path: Path):
        super().__init__(f"Directory {path} is not empty.")


class DirectoryAlreadyExistsError(FilesystemServerError):
    """An exception for when a directory already exists."""

    def __init__(self, path: Path):
        super().__init__(f"Directory {path} already exists.")


class FileAlreadyExistsError(FilesystemServerError):
    """An exception for when a file already exists."""

    def __init__(self, path: Path):
        super().__init__(f"File {path} already exists.")


class FileIsNotTextError(FilesystemServerError):
    """An exception for when a file is not text."""

    def __init__(self, path: Path):
        super().__init__(f"File {path} is not text.")


class FilePatchDoesNotMatchError(FilesystemServerError):
    """An exception for when a file patch does not match the current file."""

    def __init__(self, starting_line_number: int, current_lines: list[str], file_lines: list[str]):
        super().__init__(
            f"Patch starting at line {starting_line_number}. Patch lines {current_lines} do not match the file lines {file_lines}"
        )


class FilePatchIndexError(FilesystemServerError):
    """An exception for when a file patch index is out of bounds."""

    def __init__(self, index: int, max_index: int):
        super().__init__(f"File patch line target {index} is out of bounds. File is only {max_index} lines long.")


class CodeSummaryError(FilesystemServerError):
    pass


class LanguageNotSupportedError(CodeSummaryError):
    def __init__(self, language: str):
        super().__init__(f"Language {language} not supported")
