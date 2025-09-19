import re
from collections import defaultdict
from typing import Self

from githubkit.versions.v2022_11_28.models import GitTree
from pydantic import BaseModel, field_validator


def get_file_extension(file_path: str) -> str | None:
    if "." not in file_path:
        return None
    return file_path.split(".")[-1]


def matches_pattern(pattern: str, regex: bool, negated: bool, directory_path: str, file_path: str) -> bool:
    """If the pattern is a regex, it will be matched against the directory_path and file_path.
    if the pattern is not a regex, we do a simple contains check."""

    full_path = f"{directory_path}/{file_path}"
    if regex:
        return re.match(pattern, full_path) != negated
    return pattern in full_path != negated


def matches_include_exclude(
    full_path: str, include: list[str] | None, exclude: list[str] | None, include_exclude_is_regex: bool = False
) -> bool:
    if exclude is not None:
        for exclude_pattern in exclude:
            if matches_pattern(
                pattern=exclude_pattern, regex=include_exclude_is_regex, negated=True, directory_path=full_path, file_path=full_path
            ):
                return False

    if include is not None:
        for include_pattern in include:
            if matches_pattern(
                pattern=include_pattern, regex=include_exclude_is_regex, negated=False, directory_path=full_path, file_path=full_path
            ):
                return True
        return False

    return True


def get_dir_and_file_from_path(path: str) -> tuple[str, str]:
    path_parts = path.split("/")
    directory_path = "/".join(path_parts[:-1])
    file_path = path_parts[-1]
    return directory_path, file_path


class RepositoryFileCountEntry(BaseModel):
    extension: str
    count: int

    @staticmethod
    def sort(entries: list["RepositoryFileCountEntry"]) -> list["RepositoryFileCountEntry"]:
        return sorted(entries, key=lambda x: x.count, reverse=True)

    @staticmethod
    def sort_and_truncate(entries: list["RepositoryFileCountEntry"], top_n: int = 50) -> list["RepositoryFileCountEntry"]:
        return RepositoryFileCountEntry.sort(entries=entries)[:top_n]


class RepositoryTreeDirectory(BaseModel):
    path: str
    files: list[str]

    def to_filtered_directory(
        self,
        include: list[str] | None,
        exclude: list[str] | None,
        include_exclude_is_regex: bool = False,
    ) -> "RepositoryTreeDirectory":
        return RepositoryTreeDirectory(
            path=self.path,
            files=[
                file
                for file in self.files
                if matches_include_exclude(
                    full_path=f"{self.path}/{file}",
                    include=include,
                    exclude=exclude,
                    include_exclude_is_regex=include_exclude_is_regex,
                )
            ],
        )

    def count_files(self) -> int:
        return len(self.files)

    def count_file_extensions(self) -> list[RepositoryFileCountEntry]:
        count_by_extension: dict[str, int] = defaultdict(int)

        for file in self.files:
            if extension := get_file_extension(file):
                count_by_extension[extension] += 1

        return [RepositoryFileCountEntry(extension=extension, count=count) for extension, count in count_by_extension.items()]


class RepositoryTree(BaseModel):
    directories: list[RepositoryTreeDirectory]
    files: list[str]

    @field_validator("directories")
    @classmethod
    def validate_directories(cls, v: list[RepositoryTreeDirectory]) -> list[RepositoryTreeDirectory]:
        return [directory for directory in v if directory.files]

    @classmethod
    def from_git_tree(cls, git_tree: GitTree) -> Self:
        directories: dict[str, RepositoryTreeDirectory] = {}
        files: list[str] = []

        for tree_item in git_tree.tree:
            if tree_item.type == "tree":
                directories[tree_item.path] = RepositoryTreeDirectory(path=tree_item.path, files=[])

        for tree_item in git_tree.tree:
            if tree_item.type == "blob":
                # Split the path into directories and file
                directory_path, file_path = get_dir_and_file_from_path(tree_item.path)

                if directory := directories.get(directory_path):
                    directory.files.append(file_path)
                    continue

                files.append(file_path)

        return cls(directories=[directory for directory in directories.values() if directory.files], files=files)

    def filter_files(self, files: list[str], case_insensitive: bool = True) -> list[str]:
        if case_insensitive:
            return [file for file in files if file.lower() in [file.lower() for file in self.files]]

        return [file for file in files if file in self.files]

    def to_filtered_tree(
        self,
        include: list[str] | None,
        exclude: list[str] | None,
        include_exclude_is_regex: bool = False,
    ) -> "RepositoryTree":
        directories = [
            directory.to_filtered_directory(include=include, exclude=exclude, include_exclude_is_regex=include_exclude_is_regex)
            for directory in self.directories
        ]

        files = [
            file
            for file in self.files
            if matches_include_exclude(full_path=file, include=include, exclude=exclude, include_exclude_is_regex=include_exclude_is_regex)
        ]

        return RepositoryTree(directories=directories, files=files)

    def count_files(self) -> int:
        return len(self.files) + sum(directory.count_files() for directory in self.directories)

    def count_file_extensions(self, top_n: int = 50) -> list[RepositoryFileCountEntry]:
        count_by_extension: dict[str, int] = defaultdict(int)
        for directory in self.directories:
            for entry in directory.count_file_extensions():
                count_by_extension[entry.extension] += entry.count

        for file in self.files:
            if extension := get_file_extension(file):
                count_by_extension[extension] += 1

        return RepositoryFileCountEntry.sort_and_truncate(
            entries=[RepositoryFileCountEntry(extension=extension, count=count) for extension, count in count_by_extension.items()],
            top_n=top_n,
        )
