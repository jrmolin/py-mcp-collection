from pathlib import Path


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


class FilesystemServerResponseTooLargeError(FilesystemServerError):
    """An exception for when a response is too large to return."""

    def __init__(self, response_size: int, max_size: int):
        super().__init__(f"Response size {response_size} is too large to return. Max size is {max_size} bytes.")


class FilesystemServerTooBigToSummarizeError(FilesystemServerError):
    """An exception for when a result set is too large to summarize."""

    def __init__(self, result_set_size: int, max_size: int):
        super().__init__(f"Result set size {result_set_size} is too large to summarize. Max size is {max_size} files.")


class CodeSummaryError(FilesystemServerError):
    pass


class LanguageNotSupportedError(CodeSummaryError):
    def __init__(self, language: str):
        super().__init__(f"Language {language} not supported")
