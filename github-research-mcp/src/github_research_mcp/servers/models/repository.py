from datetime import datetime
from typing import TYPE_CHECKING, Self

from githubkit.exception import GitHubException as GitHubKitGitHubException
from githubkit.versions.v2022_11_28.models import (
    ContentFile as GitHubKitContentFile,
)
from githubkit.versions.v2022_11_28.models import (
    FullRepository as GitHubKitFullRepository,
)
from githubkit.versions.v2022_11_28.models import (
    LicenseSimple as GitHubKitLicenseSimple,
)
from githubkit.versions.v2022_11_28.models.group_0412 import CodeSearchResultItem as GitHubKitCodeSearchResultItem
from pydantic import BaseModel, ConfigDict, Field, RootModel

from github_research_mcp.servers.shared.utility import decode_content

if TYPE_CHECKING:
    from githubkit.versions.v2022_11_28.models.group_0411 import SearchResultTextMatchesItems as GitHubKitSearchResultTextMatchesItems

DEFAULT_TRUNCATE_CONTENT = 1000
DEFAULT_README_TRUNCATE_CONTENT = 2000


class BaseRepositoryError(Exception):
    """A base repository error."""

    def __init__(self, message: str):
        super().__init__(message)


class UnknownGitHubError(BaseRepositoryError):
    def __init__(self, action: str, github_exception: GitHubKitGitHubException | None = None, extra_info: str | None = None):
        super().__init__(f"{action}: {github_exception}{f': {extra_info}' if extra_info else ''}")


class RepositoryNotFoundError(BaseRepositoryError):
    """A repository was not found."""

    def __init__(self, action: str, extra_info: str | None = None):
        super().__init__(f"{action}: {extra_info}")


class MiscRepositoryError(BaseRepositoryError):
    """A miscellaneous repository error."""

    def __init__(self, action: str, extra_info: str | None = None):
        super().__init__(f"{action}: {extra_info}")


class FileLines(RootModel[dict[int, str]]):
    """A dictionary of line numbers and content pairs."""

    @classmethod
    def from_text(cls, text: str) -> Self:
        text_lines = text.split("\n")

        file_lines = {i + 1: line for i, line in enumerate(text_lines)}

        return cls(root=file_lines)

    def truncate(self, truncate: int) -> Self:
        return self.model_copy(update={"root": {k: v for k, v in self.root.items() if k <= truncate}})


class RepositoryLicense(BaseModel):
    """A repository license."""

    name: str = Field(description="The name of the license.")
    url: str | None = Field(description="The URL of the license.")

    @classmethod
    def from_license_simple(cls, license_simple: GitHubKitLicenseSimple) -> Self:
        return cls(name=license_simple.name, url=license_simple.url)


class Repository(BaseModel):
    """A repository."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str = Field(description="The name of the repository.")
    description: str | None = Field(description="The description of the repository.")
    fork: bool = Field(description="Whether the repository is a fork.")
    url: str = Field(description="The URL of the repository.")
    stars: int = Field(description="The number of stars the repository has.")
    homepage_url: str | None = Field(description="The homepage URL of the repository.")
    language: str | None = Field(description="The language of the repository.")
    default_branch: str = Field(description="The default branch of the repository.")
    topics: list[str] = Field(
        description="The topics of the repository.",
    )
    archived: bool = Field(description="Whether the repository is archived.")
    created_at: datetime = Field(description="The date and time the repository was created.")
    updated_at: datetime = Field(description="The date and time the repository was updated.")
    pushed_at: datetime = Field(description="The date and time the repository was pushed to.")
    license: RepositoryLicense | None = Field(description="The license information of the repository.")

    @classmethod
    def from_full_repository(cls, full_repository: GitHubKitFullRepository) -> Self:
        repository_license = (
            RepositoryLicense.from_license_simple(license_simple=full_repository.license_) if full_repository.license_ else None
        )
        return cls(
            name=full_repository.name,
            description=full_repository.description,
            fork=full_repository.fork,
            url=full_repository.url,
            stars=full_repository.stargazers_count,
            homepage_url=full_repository.homepage,
            language=full_repository.language,
            default_branch=full_repository.default_branch,
            topics=full_repository.topics or [],
            archived=full_repository.archived,
            created_at=full_repository.created_at,
            updated_at=full_repository.updated_at,
            pushed_at=full_repository.pushed_at,
            license=repository_license,
        )


class RepositoryFileWithContent(BaseModel):
    """A file with its path and content."""

    path: str = Field(description="The path of the file.")
    content: FileLines = Field(description="The content of the file.")
    truncated: bool = Field(default=False, description="Whether the content has been truncated.")

    @classmethod
    def from_content_file(cls, content_file: GitHubKitContentFile, truncate: int = DEFAULT_TRUNCATE_CONTENT) -> Self:
        decoded_content = decode_content(content_file.content)

        file_lines = FileLines.from_text(text=decoded_content)

        return cls(path=content_file.path, content=file_lines).truncate(truncate=truncate)

    def truncate(self, truncate: int) -> Self:
        return self.model_copy(update={"content": self.content.truncate(truncate=truncate)})


class RepositoryFileWithLineMatches(BaseModel):
    """A file with its path and line matches from a search result."""

    path: str = Field(description="The path of the file.")
    matches: list[str] = Field(description="The fragments of the file that match the search query.")

    @classmethod
    def from_code_search_result_item(cls, code_search_result_item: GitHubKitCodeSearchResultItem) -> Self:
        if not code_search_result_item.text_matches:
            msg = f"Expected a list of SearchResultTextMatchesItems, got {type(code_search_result_item.text_matches)}"
            raise TypeError(msg)

        text_matches: list[GitHubKitSearchResultTextMatchesItems] = code_search_result_item.text_matches

        fragments: list[str] = [match.fragment for match in text_matches if match.fragment]

        return cls(path=code_search_result_item.path, matches=fragments)


class RepositorySummary(RootModel[str]):
    """A summary of a repository."""


class RequestFiles(BaseModel):
    """A request for files from a repository."""

    files: list[str] = Field(description="The files to get the content of.")

    def remove_files(self, files: list[str]) -> Self:
        return self.model_copy(update={"files": [file for file in self.files if file not in files]})

    def truncate(self, truncate: int) -> Self:
        return self.model_copy(update={"files": self.files[:truncate]})


class RequestFilesForSummary(BaseModel):
    """A request for files from a repository."""

    foundational_docs: list[str] = Field(description="Paths to foundational docs to get the content of.")
    build_ci_cd_runtime: list[str] = Field(description="Paths to build, CI/CD, and runtime files to get the content of.")
    entry_points_configuration: list[str] = Field(description="Paths to entry points and configuration files to get the content of.")
    tests_examples: list[str] = Field(description="Paths to tests and examples files to get the content of.")
    code_quality_style: list[str] = Field(description="Paths to code quality and style files to get the content of.")
    other: list[str] = Field(description="Paths to other files to get the content of.")

    @property
    def files(self) -> list[str]:
        return [
            *self.foundational_docs,
            *self.build_ci_cd_runtime,
            *self.entry_points_configuration,
            *self.tests_examples,
            *self.code_quality_style,
            *self.other,
        ]

    def trim(self, remove_files: list[str], truncate: int) -> list[str]:
        return [file for file in self.files if file not in remove_files][:truncate]
