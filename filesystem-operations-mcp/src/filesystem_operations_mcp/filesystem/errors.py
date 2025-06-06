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


class CodeSummaryError(FilesystemServerError):
    pass


class LanguageNotSupportedError(CodeSummaryError):
    def __init__(self, language: str):
        super().__init__(f"Language {language} not supported")
