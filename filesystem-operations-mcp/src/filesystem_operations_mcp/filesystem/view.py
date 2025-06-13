import inspect
import json
from collections.abc import Awaitable, Callable
from typing import Annotated, Any

from makefun import wraps as makefun_wraps
from pydantic import BaseModel, ConfigDict, Field

from filesystem_operations_mcp.filesystem.errors import FilesystemServerResponseTooLargeError, FilesystemServerTooBigToSummarizeError
from filesystem_operations_mcp.filesystem.mappings.magika_to_tree_sitter import code_mappings
from filesystem_operations_mcp.filesystem.nodes.directory import DirectoryEntry
from filesystem_operations_mcp.filesystem.nodes.file import FileEntry
from filesystem_operations_mcp.filesystem.summarize.code import summarize_code
from filesystem_operations_mcp.filesystem.summarize.text import summarize_text
from filesystem_operations_mcp.logging import BASE_LOGGER

logger = BASE_LOGGER.getChild("view")

TOO_BIG_TO_SUMMARIZE_ITEMS_THRESHOLD = 300
TOO_BIG_TO_SUMMARIZE_BYTES_THRESHOLD = 1_000_000
TOO_BIG_TO_RETURN_BYTES_THRESHOLD = 1_000_000
TOO_MANY_NAMES_THRESHOLD = 10


class FileExportableField(BaseModel):
    """The fields of a file that can be included in the response. Enabling a field will include the field in the response."""

    model_config = ConfigDict(use_attribute_docstrings=True)

    file_path: bool = Field(default=True)
    """Relative path of the file. For example, `src/mycoolproject/main.py`."""

    basename: bool = Field(default=False)
    """Basename of the file. For example, `main`."""

    extension: bool = Field(default=False)
    """Extension of the file. For example, `.py`."""

    file_type: bool = Field(default=True)
    """File type of the file. For example, `python`."""

    mime_type: bool = Field(default=False)
    """Mime type of the file. For example, `text/plain`."""

    is_binary: bool = Field(default=False)
    """Include whether the file is binary."""

    size: bool = Field(default=True)
    """Size of the file in bytes. """

    read_text: bool = Field(default=False)
    """Read the contents of the file only if it is text. Do not use if you plan to apply edits to specific lines of the file."""

    read: bool = Field(default=False)
    """Read the file as a set of lines. The response will be a dictionary of line numbers to lines of text.
    Will not be included if the file is binary."""

    read_binary_base64: bool = Field(default=False)
    """Read the contents of the file as base64 encoded binary."""

    preview: bool = Field(default=False)
    """Include a preview of the file only if it is text."""

    limit_preview: int = Field(default=250)
    """Limit the number of bytes to include in the preview."""

    code_summary: bool = Field(default=False)
    """Include a summary of the code in the file. Control the number of bytes to include with `limit_summaries`.
    Code summaries are not supported for calls that return more than 300 results or with files larger than 1MB."""

    text_summary: bool = Field(default=False)
    """Include a summary of the text in the file. Control the number of bytes to include with `limit_summaries`.
    Text summaries are not supported for calls that return more than 300 results or with files larger than 1MB.
    """

    limit_summaries: int = Field(default=2000)
    """Limit the number of bytes to include in the summaries."""

    created_at: bool = Field(default=False)
    """Whether to include the creation time of the file."""

    modified_at: bool = Field(default=False)
    """Whether to include the modification time of the file."""

    owner: bool = Field(default=False)
    """Whether to include the owner of the file."""

    group: bool = Field(default=False)
    """Whether to include the group of the file."""

    async def _apply_summaries(self, node: FileEntry) -> dict[str, Any]:
        model = {}
        if self.code_summary and node.is_code and node.magika_content_type:
            if await node.size() > TOO_BIG_TO_SUMMARIZE_BYTES_THRESHOLD:
                model["code_summary"] = None
                model["code_summary_skipped"] = "Exceeded size limit"
            else:
                content_type_to_language = code_mappings.get(node.magika_content_type.label)
                if content_type_to_language is not None:
                    summary = summarize_code(content_type_to_language.value, await node.read_text())
                    as_json = json.dumps(summary)
                    if len(as_json) > self.limit_summaries:
                        model["code_summary"] = as_json[: self.limit_summaries]
                    else:
                        model["code_summary"] = summary

        if self.text_summary and node.is_text and node.magika_content_type:
            if await node.size() > TOO_BIG_TO_SUMMARIZE_BYTES_THRESHOLD:
                model["text_summary"] = None
                model["text_summary_skipped"] = "Exceeded size limit"
            else:
                summary = summarize_text(await node.read_text())
                model["text_summary"] = summary[: self.limit_summaries]

        return model

    async def _apply_owner_and_group(self, node: FileEntry) -> dict[str, Any]:
        model = {}
        if self.owner:
            model["owner"] = await node.owner()
        if self.group:
            model["group"] = await node.group()
        return model

    async def _apply_read_preview(self, node: FileEntry) -> dict[str, Any]:
        model = {}
        if self.preview and not node.is_binary:
            model["preview"] = await node.preview_contents(head=self.limit_preview)
        if self.read_text and not node.is_binary:
            model["read_text"] = await node.read_text()
        if self.read and not node.is_binary:
            model["read"] = (await node.read_lines()).model_dump()
        if self.read_binary_base64 and node.is_binary:
            model["read_binary_base64"] = await node.read_binary_base64()

        return model

    async def _apply_file_type(self, node: FileEntry) -> dict[str, Any]:
        model = {}
        if self.file_type:
            model["file_type"] = node.magika_content_type_label
        if self.mime_type:
            model["mime_type"] = node.mime_type
        if self.is_binary:
            model["is_binary"] = node.is_binary
        return model

    async def apply(self, node: FileEntry) -> dict[str, Any]:
        model = {}

        logger.info(f"Applying file fields to {node.file_path}")

        if self.file_path:
            model["file_path"] = node.file_path
        if self.basename:
            model["basename"] = node.name
        if self.extension:
            model["extension"] = node.extension
        if self.size:
            model["size"] = await node.size()

        if self.created_at:
            model["created_at"] = await node.created_at()
        if self.modified_at:
            model["modified_at"] = await node.modified_at()

        model.update(await self._apply_file_type(node))
        model.update(await self._apply_summaries(node))
        model.update(await self._apply_owner_and_group(node))
        model.update(await self._apply_read_preview(node))

        # remove null or empty values
        return {k: v for k, v in model.items() if v not in ("", [], {}, None)}


def caller_controlled_file_fields(
    func: Callable[..., Awaitable[FileEntry | list[FileEntry]]],
) -> Callable[..., Awaitable[dict[str, Any]]]:
    @makefun_wraps(
        func,
        append_args=[
            inspect.Parameter("file_fields", inspect.Parameter.KEYWORD_ONLY, default=FileExportableField(), annotation=FileExportableField),
            inspect.Parameter(
                "include_summaries",
                inspect.Parameter.KEYWORD_ONLY,
                default=False,
                annotation=Annotated[bool, Field(description="Whether to include summaries of each file in the response.")],
            ),
        ],
    )
    async def wrapper(
        file_fields: FileExportableField,
        include_summaries: bool,
        *args: Any,
        **kwargs: Any,
    ) -> dict[str, Any]:
        result = await func(*args, **kwargs)

        if include_summaries and isinstance(result, list) and len(result) > TOO_BIG_TO_SUMMARIZE_ITEMS_THRESHOLD:
            raise FilesystemServerTooBigToSummarizeError(result_set_size=len(result), max_size=TOO_BIG_TO_SUMMARIZE_ITEMS_THRESHOLD)

        if include_summaries:
            file_fields.code_summary = True
            file_fields.text_summary = True

        return_result = {}

        if isinstance(result, list):
            result = sorted(result, key=lambda x: x.file_path)
            for node in result:
                return_result[node.file_path] = await file_fields.apply(node)
                return_result[node.file_path].pop("file_path", None)
        else:
            return_result = await file_fields.apply(result)

        if len(json.dumps(return_result)) > TOO_BIG_TO_RETURN_BYTES_THRESHOLD:
            raise FilesystemServerResponseTooLargeError(
                response_size=len(json.dumps(return_result)), max_size=TOO_BIG_TO_RETURN_BYTES_THRESHOLD
            )

        return return_result

    return wrapper


class DirectoryExportableField(BaseModel):
    """The fields of a directory that can be included in the response."""

    directory_path: bool = Field(default=True)
    """The relative path of the directory. For example, `src/mycoolproject`."""

    basename: bool = Field(default=False)
    """The basename of the directory. For example, `mycoolproject`."""

    files_count: bool = Field(default=False)
    """The number of files in the directory."""

    directories_count: bool = Field(default=True)
    """The number of directories in the directory."""

    children_count: bool = Field(default=False)
    """The number of children of the directory."""

    children: bool = Field(default=False)
    """The children of the directory. The response will be a list of FileEntry and DirectoryEntry objects."""

    file_names: bool = Field(default=True)
    """The first 100 names of the files in the directory. The response will be a list of strings."""

    directory_names: bool = Field(default=False)
    """The first 100 names of the directories in the directory. The response will be a list of strings."""

    created_at: bool = Field(default=False)
    """The creation time of the directory. For example, `2021-01-01 12:00:00`."""

    modified_at: bool = Field(default=False)
    """The modification time of the directory. For example, `2021-01-01 12:00:00`."""

    owner: bool = Field(default=False)
    """The owner of the directory. For example, UID `1000`."""

    group: bool = Field(default=False)
    """The group of the directory. For example, GID `1000`."""

    async def apply(self, node: DirectoryEntry) -> dict[str, Any]:
        model = {}

        logger.info(f"Applying directory fields to {node.directory_path}")

        needs_children = any(
            [self.files_count, self.directories_count, self.children_count, self.children, self.file_names, self.directory_names]
        )
        if needs_children:
            children = await node.children()
            children = sorted(children, key=lambda x: x.name)

        if self.directory_path:
            model["directory_path"] = node.directory_path
        if self.basename:
            model["basename"] = node.name
        if self.files_count:
            model["files_count"] = len([child for child in children if child.is_file])
        if self.directories_count:
            model["directories_count"] = len([child for child in children if child.is_dir])
        if self.children_count:
            model["children_count"] = len(children)
        if self.children:
            model["children"] = children
        if self.file_names:
            file_names = [child.name for child in children if child.is_file]
            model["file_names"] = file_names[:TOO_MANY_NAMES_THRESHOLD]
            if len(file_names) > TOO_MANY_NAMES_THRESHOLD:
                model["file_names_error"] = f"Only showing names for {TOO_MANY_NAMES_THRESHOLD} of {len(file_names)} files"
        if self.directory_names:
            directory_names = [child.name for child in children if child.is_dir]
            model["directory_names"] = directory_names[:TOO_MANY_NAMES_THRESHOLD]
            if len(directory_names) > TOO_MANY_NAMES_THRESHOLD:
                model["directory_names_error"] = f"Only showing names for {TOO_MANY_NAMES_THRESHOLD} of {len(directory_names)} directories"
        if self.created_at:
            model["created_at"] = await node.created_at()
        if self.modified_at:
            model["modified_at"] = await node.modified_at()
        if self.owner:
            model["owner"] = await node.owner()
        if self.group:
            model["group"] = await node.group()

        # remove null or empty values
        return {k: v for k, v in model.items() if v not in ("", [], {}, None)}


def caller_controlled_directory_fields(
    func: Callable[..., Awaitable[DirectoryEntry | list[DirectoryEntry]]],
) -> Callable[..., Awaitable[dict[str, Any]]]:
    @makefun_wraps(
        func,
        append_args=inspect.Parameter(
            "directory_fields", inspect.Parameter.KEYWORD_ONLY, default=DirectoryExportableField(), annotation=DirectoryExportableField
        ),
    )
    async def wrapper(directory_fields: DirectoryExportableField, *args: Any, **kwargs: Any) -> dict[str, Any]:
        result = await func(*args, **kwargs)

        if isinstance(result, list):
            result = sorted(result, key=lambda x: x.directory_path)
            return_result = {}
            for node in result:
                return_result[node.directory_path] = await directory_fields.apply(node)
                return_result[node.directory_path].pop("directory_path", None)

            return return_result

        return await directory_fields.apply(result)

    return wrapper
