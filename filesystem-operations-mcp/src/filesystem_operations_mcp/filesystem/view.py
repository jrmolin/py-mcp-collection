import inspect
import json
from collections.abc import Awaitable, Callable
from enum import StrEnum
from pathlib import Path
from typing import Any

from makefun import wraps as makefun_wraps
from pydantic import Field, RootModel

from filesystem_operations_mcp.filesystem.mappings.magika_to_tree_sitter import code_mappings
from filesystem_operations_mcp.filesystem.nodes.directory import DirectoryEntry
from filesystem_operations_mcp.filesystem.nodes.file import FileEntry
from filesystem_operations_mcp.filesystem.summarize.code import summarize_code
from filesystem_operations_mcp.filesystem.summarize.text import summarize_text
from filesystem_operations_mcp.logging import BASE_LOGGER

logger = BASE_LOGGER.getChild("view")


def tips_file_exportable_field() -> str:
    """Returns a doc string for the fields of a file that can be included in the response."""
    return """
    The options for the `file_fields` parameter are:

    | Field | Type | Description | Example |
    |-------|------|-------------|---------|
    | file_path | Path | The relative path of the file. | "src/mycoolproject/main.py" |
    | basename | str | The basename of the file. | "main" |
    | extension | str | The extension of the file. | ".py" |
    | mime_type | str | The mime type of the file. | "text/plain" |
    | code_summary_2000 | str | A tree-sitter plus natural language summary of the code. | "The file contains a Python script that prints 'Hello, world!'." |
    | text_summary_2000 | str | A natural language summary of the text in the file. | "The file contains a Python script that prints 'Hello, world!'." |
    | is_binary | bool | Whether the file is binary. | False |
    | size | int | The size of the file in bytes. | 1000 |
    | read_all | str | The entire contents of the file as a string. | "print('Hello, world!')" |
    | read_all_lines | list[str] | The lines of the file as a list of strings. | ["print('Hello, world!')"] |
    | read_all_lines_with_numbers | list[FileLine] | The lines of the file as a list of FileLine objects which are a tuple of the line number and the line of text. | [(1, "print('Hello, world!')")] |
    | preview | str | The first 100 bytes of the file as a string. | "print('Hello, world!')" |
    | preview_1000 | str | The first 1000 bytes of the file as a string. | "print('Hello, world!')" |
    | created_at | datetime | The creation time of the file. | 2021-01-01 12:00:00 |
    | modified_at | datetime | The modification time of the file. | 2021-01-01 12:00:00 |
    | owner | int | The owner of the file. | 1000 |
    | group | int | The group of the file. | 1000 |
    """  # noqa: E501


class FileExportableField(StrEnum):
    """The fields of a file that can be included in the response."""

    file_path = "file_path"
    basename = "basename"
    extension = "extension"
    file_type = "file_type"
    mime_type = "mime_type"
    is_binary = "is_binary"
    size = "size"
    read_text = "read_text"
    read_text_lines = "read_text_lines"
    read_all_lines_with_numbers = "read_all_lines_with_numbers"
    preview = "preview"
    preview_1000 = "preview_1000"
    code_summary_2000 = "code_summary_2000"
    text_summary_2000 = "text_summary_2000"
    created_at = "created_at"
    modified_at = "modified_at"
    owner = "owner"
    group = "group"


class FileExportableFields(RootModel):
    """Description of the fields of a file to include in the response."""

    root: list[FileExportableField] = Field(
        default_factory=lambda: [
            FileExportableField.file_path,
            FileExportableField.size,
            FileExportableField.file_type,
            FileExportableField.mime_type,
        ],
        description="The fields of a file to include in the response.",
    )

    async def apply(self, node: FileEntry) -> dict[str, Any]:  # noqa: PLR0912
        model = {}

        logger.info(f"Applying file fields to {node.file_path}")

        is_text = not node.is_binary
        is_binary = node.is_binary

        summaries_dir = Path("summaries")
        summaries_dir.mkdir(exist_ok=True)

        # make a directory for this file
        file_summaries_dir = summaries_dir / node.stem
        file_summaries_dir.mkdir(exist_ok=True)

        # ["file_path", "file_type", "luhn_summary","text_rank_summary","reduction_summary"]

        for field in self.root:
            field_name = field.value
            if field == FileExportableField.file_path:
                model[field_name] = node.file_path
            elif field == FileExportableField.basename:
                model[field_name] = node.name
            elif field == FileExportableField.extension:
                model[field_name] = node.extension
            elif field == FileExportableField.file_type:
                model[field_name] = node.magika_content_type
            elif field == FileExportableField.mime_type:
                model[field_name] = node.mime_type
            elif field == FileExportableField.code_summary_2000 and node.is_code and node.magika_content_type:
                content_type_to_language = code_mappings.get(node.magika_content_type.label)
                if content_type_to_language is not None:
                    summary = summarize_code(content_type_to_language.value, await node.read_text)
                    model[field_name] = json.dumps(summary)[:2000]
            elif field == FileExportableField.text_summary_2000 and node.is_text and node.magika_content_type:
                summary = summarize_text(await node.read_text)
                model[field_name] = json.dumps(summary)[:2000]
            elif field == FileExportableField.is_binary:
                model[field_name] = is_binary
            elif field == FileExportableField.size:
                model[field_name] = await node.size
            elif field == FileExportableField.preview and is_text:
                model[field_name] = await node.preview_contents(head=100)
            elif field == FileExportableField.preview_1000 and is_text:
                model[field_name] = await node.preview_contents(head=1000)
            elif field == FileExportableField.read_text and is_text:
                model[field_name] = await node.read_text
            elif field == FileExportableField.read_text_lines and is_text:
                model[field_name] = await node.read_text_lines
            elif field == FileExportableField.read_all_lines_with_numbers and is_text:
                model[field_name] = await node.read_text_line_numbers
            elif field == FileExportableField.created_at:
                model[field_name] = await node.created_at
            elif field == FileExportableField.modified_at:
                model[field_name] = await node.modified_at
            elif field == FileExportableField.owner:
                model[field_name] = await node.owner
            elif field == FileExportableField.group:
                model[field_name] = await node.group

        return model


def caller_controlled_file_fields(
    func: Callable[..., Awaitable[FileEntry | list[FileEntry]]],
) -> Callable[..., Awaitable[dict[str, Any]]]:
    @makefun_wraps(
        func,
        append_args=inspect.Parameter(
            "file_fields", inspect.Parameter.KEYWORD_ONLY, default=FileExportableFields(), annotation=FileExportableFields
        ),
    )
    async def wrapper(file_fields: FileExportableFields, *args: Any, **kwargs: Any) -> dict[str, Any]:
        result = await func(*args, **kwargs)

        if isinstance(result, list):
            return_result = {}
            for node in result:
                return_result[node.file_path] = await file_fields.apply(node)
                return_result[node.file_path].pop("file_path")

            print(return_result)
            return return_result

        return await file_fields.apply(result)

    return wrapper


def tips_directory_exportable_field() -> str:
    """Returns a doc string for the fields of a directory that can be included in the response."""
    return """
    The options for the `directory_fields` parameter are:

    | Field | Type | Description | Example |
    |-------|------|-------------|---------|
    | directory_path | Path | The relative path of the directory. | "src/mycoolproject" |
    | files_count | int | The number of children of the directory. | 2 |
    | directories_count | int | The number of children of the directory. | 2 |
    | children_count | int | The number of children of the directory. | 2 |
    | children | list[FileEntry | DirectoryEntry] | The children of the directory. | [FileEntry(relative_path="src/mycoolproject/main.py", size=1000), DirectoryEntry(relative_path="src/mycoolproject/subdir", size=1000)] |
    | basename | str | The basename of the directory. | "mycoolproject" |
    | created_at | datetime | The creation time of the directory. | 2021-01-01 12:00:00 |
    | modified_at | datetime | The modification time of the directory. | 2021-01-01 12:00:00 |
    | owner | int | The owner of the directory. | 1000 |
    | group | int | The group of the directory. | 1000 |
    """  # noqa: E501


class DirectoryExportableField(StrEnum):
    """The fields of a directory that can be included in the response."""

    directory_path = "directory_path"
    basename = "basename"
    files_count = "files_count"
    directories_count = "directories_count"
    children_count = "children_count"
    children = "children"
    created_at = "created_at"
    modified_at = "modified_at"
    owner = "owner"
    group = "group"


class DirectoryExportableFields(RootModel):
    """Description of the fields of a directory to include in the response."""

    root: list[DirectoryExportableField] = Field(
        default_factory=lambda: [
            DirectoryExportableField.directory_path,
            DirectoryExportableField.children_count,
        ],
        description="The fields of a directory to include in the response.",
    )

    async def apply(self, node: DirectoryEntry) -> dict[str, Any]:
        model = {}

        logger.info(f"Applying directory fields to {node.directory_path}")

        for field in self.root:
            if field == DirectoryExportableField.directory_path:
                model[field] = node.directory_path
            elif field == DirectoryExportableField.basename:
                model[field] = node.name
            elif field == DirectoryExportableField.files_count:
                model[field] = len([child for child in await node.children if child.is_file()])
            elif field == DirectoryExportableField.directories_count:
                model[field] = len([child for child in await node.children if child.is_dir()])
            elif field == DirectoryExportableField.children_count:
                children = await node.children
                model[field] = len(children)
            elif field == DirectoryExportableField.created_at:
                model[field] = await node.created_at
            elif field == DirectoryExportableField.modified_at:
                model[field] = await node.modified_at
            elif field == DirectoryExportableField.owner:
                model[field] = await node.owner
            elif field == DirectoryExportableField.group:
                model[field] = await node.group

        return model


def caller_controlled_directory_fields(
    func: Callable[..., Awaitable[DirectoryEntry | list[DirectoryEntry]]],
) -> Callable[..., Awaitable[dict[str, Any]]]:
    @makefun_wraps(
        func,
        append_args=inspect.Parameter(
            "directory_fields", inspect.Parameter.KEYWORD_ONLY, default=DirectoryExportableFields(), annotation=DirectoryExportableFields
        ),
    )
    async def wrapper(directory_fields: DirectoryExportableFields, *args: Any, **kwargs: Any) -> dict[str, Any]:
        result = await func(*args, **kwargs)

        if isinstance(result, list):
            return_result = {}
            for node in result:
                return_result[node.directory_path] = await directory_fields.apply(node)
                return_result[node.directory_path].pop("directory_path")

            return return_result

        return await directory_fields.apply(result)

    return wrapper


def caller_controlled_files_and_directories_fields(
    func: Callable[..., Awaitable[FileEntry | DirectoryEntry | list[FileEntry | DirectoryEntry]]],
) -> Callable[..., Awaitable[dict[str, Any] | list[dict[str, Any]]]]:
    @makefun_wraps(
        func,
        append_args=[
            inspect.Parameter(
                "directory_fields",
                inspect.Parameter.KEYWORD_ONLY,
                default=DirectoryExportableFields(),
                annotation=DirectoryExportableFields,
            ),
            inspect.Parameter(
                "file_fields", inspect.Parameter.KEYWORD_ONLY, default=FileExportableFields(), annotation=FileExportableFields
            ),
        ],
    )
    async def wrapper(
        directory_fields: DirectoryExportableFields, file_fields: FileExportableFields, *args: Any, **kwargs: Any
    ) -> dict[str, Any] | list[dict[str, Any]]:
        result = await func(*args, **kwargs)

        if isinstance(result, list):
            results: list[dict[str, Any]] = []
            for node in result:
                if isinstance(node, FileEntry):
                    results.append(await file_fields.apply(node))
                elif isinstance(node, DirectoryEntry):
                    results.append(await directory_fields.apply(node))

            return results

        if isinstance(result, FileEntry):
            return await file_fields.apply(result)

        return await directory_fields.apply(result)

    return wrapper
