import asyncio
import inspect
import json
import time
from collections.abc import AsyncIterator, Awaitable, Callable
from typing import Annotated, Any, ClassVar, Self

from makefun import wraps as makefun_wraps  # pyright: ignore[reportUnknownVariableType]
from pydantic import BaseModel, ConfigDict, Field, field_serializer, model_validator
from pydantic.fields import computed_field

from filesystem_operations_mcp.filesystem.nodes import FileEntry, FileEntryTypeEnum, FileEntryWithMatches
from filesystem_operations_mcp.filesystem.summarize.code import summarize_code
from filesystem_operations_mcp.filesystem.summarize.markdown import summarize_markdown
from filesystem_operations_mcp.filesystem.summarize.text import summarizer
from filesystem_operations_mcp.filesystem.utils.workers import gather_results_from_queue, worker_pool
from filesystem_operations_mcp.logging import BASE_LOGGER

logger = BASE_LOGGER.getChild("view")


MAX_SUMMARY_BYTES = 2000
ASYNC_READ_THRESHOLD = 1000


class FileExportableField(BaseModel):
    """The fields of a file that can be included in the response. Enabling a field will include the field in the response."""

    model_config: ClassVar[ConfigDict] = ConfigDict(use_attribute_docstrings=True)

    basename: bool = Field(default=False)
    """Basename of the file. For example, `main`."""

    extension: bool = Field(default=False)
    """Extension of the file. For example, `.py`."""

    type: bool = Field(default=True)
    """Type of the file. For example, `binary`, `text`, `code`, `data`, `unknown`."""

    mime_type: bool = Field(default=False)
    """Mime type of the file. For example, `text/plain`."""

    size: bool = Field(default=True)
    """Size of the file in bytes. """

    read: bool = Field(default=False)
    """Read the file as a set of lines. The response will be a dictionary of line numbers to lines of text.
    Will not be included if the file is binary."""

    read_lines: int = Field(default=100)
    """Limit the number of lines to read from the target files."""

    preview: bool = Field(default=False)
    """Include a preview of the file only if it is text . Preview will be ignored if read or summarize is enabled."""

    preview_lines: int = Field(default=5)
    """Limit the number of lines to preview from the target files."""

    summarize: bool = Field(default=False)
    """Include a summary of the file.
    Text summaries will summarize the first 100 lines of the file.
    Code summaries will summarize the first 2000 lines of the file.
    Summaries will never return more than 2000 bytes."""

    created_at: bool = Field(default=False)
    """Whether to include the creation time of the file."""

    modified_at: bool = Field(default=False)
    """Whether to include the modification time of the file."""

    owner: bool = Field(default=False)
    """Whether to include the owner of the file."""

    group: bool = Field(default=False)
    """Whether to include the group of the file."""

    @model_validator(mode="after")
    def validate_read_limit(self) -> Self:
        if self.read and self.preview:
            self.preview = False

        if self.summarize and self.preview:
            self.preview = False

        return self

    def to_model_dump_include(self) -> set[str]:
        include: set[str] = set()

        if self.basename:
            include.add("stem")

        if self.extension:
            include.add("extension")

        if self.type:
            include.add("type")

        if self.mime_type:
            include.add("mime_type")

        if self.size:
            include.add("size")

        if self.owner:
            include.add("owner")

        if self.group:
            include.add("group")

        if self.created_at:
            include.add("created_at")

        if self.modified_at:
            include.add("modified_at")

        return include

    def _apply_code_summary(self, node: FileEntry, lines: list[str]) -> dict[str, Any]:
        if not node.tree_sitter_language:
            return {"code_summary_skipped": "Not a summarizable language"}

        summary = summarize_code(node.tree_sitter_language.value, "\n".join(lines))
        as_json = json.dumps(summary)

        if len(as_json) > MAX_SUMMARY_BYTES:
            return {"summary": as_json[:MAX_SUMMARY_BYTES]}

        return {"summary": summary}

    def _apply_text_summary(self, lines: list[str]) -> dict[str, Any]:
        summary = summarizer.summarize("\n".join(lines))
        return {"summary": summary[:MAX_SUMMARY_BYTES]}

    def _apply_markdown_summary(self, lines: list[str]) -> dict[str, Any]:
        summary = summarize_markdown("\n".join(lines))

        summary = summarizer.summarize(summary)

        return {"summary": summary[:MAX_SUMMARY_BYTES]}

    def _apply_asciidoc_summary(self, lines: list[str]) -> dict[str, Any]:
        # Keep lines which start with an alpha character and are not the start of hyperlinks
        lines = [
            stripped_line
            for line in lines
            if (stripped_line := line.strip()) and stripped_line[0].isalpha() and not stripped_line.startswith("http")  # No wrapping please
        ]

        if not lines:
            return {}

        summary = summarizer.summarize("\n".join(lines))
        return {"summary": summary[:MAX_SUMMARY_BYTES]}

    # def apply(self, node: FileEntry | FileEntryWithMatches) -> dict[str, Any]:
    #     """Apply the file fields to a file entry."""
    #     includes: set[str] = self.to_model_dump_include() | {"relative_path_str", "matches", "matches_limit_reached"}

    #     return dict(node.model_dump(include=includes, exclude_none=True).items())

    def apply_read_lines_count(self, node: FileEntry | FileEntryWithMatches) -> int | None:
        """Get the lines to read from the file."""
        if node.type == FileEntryTypeEnum.BINARY:
            return None

        counts: list[int] = []

        if self.summarize and node.type == FileEntryTypeEnum.CODE:
            counts.append(2000)

        if self.summarize and node.type == FileEntryTypeEnum.TEXT:
            counts.append(100)

        if self.read:
            counts.append(self.read_lines)

        if self.preview:
            counts.append(self.preview_lines)

        return max(counts) if counts else None

    # async def get_lines_for_file(self, node: FileEntry | FileEntryWithMatches, line_count: int) -> FileLines:
    #     """Get the lines to read from the file."""
    #     counts: list[int] = []

    #     if self.summarize and node.type == FileEntryTypeEnum.CODE:
    #         counts.append(1000)

    #     if self.summarize and node.type == FileEntryTypeEnum.TEXT:
    #         counts.append(100)

    #     if self.read:
    #         counts.append(self.read_limit)

    #     if self.preview:
    #         counts.append(self.preview_limit)

    #     return await node.afile_lines(count=line_count)

    def apply(self, node: FileEntry | FileEntryWithMatches) -> tuple[dict[str, Any], int | None]:
        """Apply the file fields to a file entry."""

        includes: set[str] = self.to_model_dump_include() | {"relative_path_str", "matches", "matches_limit_reached"}

        model = node.model_dump(include=includes, exclude_none=True)

        if model.get("type") and isinstance(model["type"], FileEntryTypeEnum):
            model["type"] = model["type"].value

        return model, self.apply_read_lines_count(node)

    async def aapply(self, node: FileEntry | FileEntryWithMatches) -> dict[str, Any]:
        lines_to_read = self.apply_read_lines_count(node)

        if lines_to_read and lines_to_read < ASYNC_READ_THRESHOLD:
            file_lines = node.file_lines(count=lines_to_read)
        else:
            file_lines = await node.afile_lines(count=lines_to_read)

        if node.type == FileEntryTypeEnum.BINARY or not file_lines:
            return {}

        model: dict[str, Any] = {
            "relative_path_str": node.relative_path_str,
        }

        if self.read:
            model.update({"read": file_lines.first(self.read_lines).model_dump()})

        if self.preview:
            model.update({"preview": file_lines.first(self.preview_lines).model_dump()})

        if self.summarize and node.type == FileEntryTypeEnum.CODE:
            model.update(self._apply_code_summary(node, lines=file_lines.first(1000).lines()))

        if self.summarize and node.type == FileEntryTypeEnum.TEXT:
            if node.mime_type == "text/markdown":
                model.update(self._apply_markdown_summary(lines=file_lines.first(100).lines()))
            elif node.extension == ".asciidoc":
                model.update(self._apply_asciidoc_summary(lines=file_lines.first(100).lines()))
            else:
                model.update(self._apply_text_summary(lines=file_lines.first(100).lines()))

        return model


class ResponseModel(BaseModel):
    """The response model for the customizable file materializer."""

    model_config: ClassVar[ConfigDict] = ConfigDict(arbitrary_types_allowed=True, use_attribute_docstrings=True)

    errors: list[str] | bool = Field(default=False, description="An optional error message to include in the response.")

    max_results: int = Field(..., description="The maximum number of results to return.", exclude=True)

    duration: float = Field(default=0, description="The duration of the request in seconds.")

    files: dict[str, Any] = Field(default_factory=dict, description="The files in the response.")
    """The files in the response."""

    @field_serializer("files")
    def serialize_files(self, files: dict[str, Any]) -> dict[str, Any]:
        return dict(sorted(files.items(), key=lambda x: x[0]))

    @computed_field
    @property
    def files_count(self) -> int:
        return len(self.files)

    @computed_field
    @property
    def limit_reached(self) -> bool | None:
        """Whether the limit was reached. If the limit was not reached, return None."""
        if self.files_count < self.max_results:
            return None

        return self.files_count >= self.max_results


def customizable_file_materializer(
    func: Callable[..., AsyncIterator[FileEntry | FileEntryWithMatches]],
) -> Callable[..., Awaitable[ResponseModel]]:
    @makefun_wraps(
        func,
        append_args=[
            inspect.Parameter(
                "file_fields",
                inspect.Parameter.KEYWORD_ONLY,
                default=FileExportableField(),
                annotation=FileExportableField,
            ),
            inspect.Parameter(
                "max_results",
                inspect.Parameter.KEYWORD_ONLY,
                default=50,
                annotation=Annotated[int, Field(description="The maximum number of results to return.")],
            ),
        ],
    )
    async def wrapper(
        file_fields: FileExportableField,
        max_results: int,
        *args: Any,  # pyright: ignore[reportAny]
        **kwargs: Any,  # pyright: ignore[reportAny]
    ) -> ResponseModel:
        logger.info(f"Handling request to {func.__name__} with args: {args} and kwargs: {kwargs}")
        timers: dict[str, float] = {
            "start": time.perf_counter(),
        }

        errors: list[str] = []

        work_queue: asyncio.Queue[FileEntry | FileEntryWithMatches] = asyncio.Queue()

        result_iter: AsyncIterator[FileEntry | FileEntryWithMatches] = func(*args, **kwargs)

        results_by_path: dict[str, Any] = {}

        async for node in result_iter:
            if max_results and len(results_by_path) >= max_results:
                logger.info(f"Reached max results: {max_results} for call to {func.__name__} with args: {args} and kwargs: {kwargs}")
                errors.append(f"Reached max_results {max_results} results. To get more results, refine the query or increase max_results.")
                break

            model, line_count = file_fields.apply(node)

            if line_count:
                work_queue.put_nowait(node)

            results_by_path[node.relative_path_str] = model

        if work_queue.qsize() > 0:
            result_queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue()

            async with worker_pool(file_fields.aapply, work_queue=work_queue, result_queue=result_queue, workers=4) as (
                work_queue,
                error_queue,
            ):
                pass

            error_results = await gather_results_from_queue(error_queue)
            errors.extend([str(f"{error_result[0].relative_path_str}: {error_result[1]}") for error_result in error_results])

            for result in await gather_results_from_queue(result_queue):
                results_by_path.get(result["relative_path_str"], {}).update(result)  # pyright: ignore[reportAny]

        for result in results_by_path.values():  # pyright: ignore[reportAny]
            _ = result.pop("relative_path_str")  # pyright: ignore[reportAny]

        total_time = time.perf_counter() - timers["start"]

        logger.info(f"Time taken to gather and prepare {len(results_by_path)} files: {total_time} seconds")

        return ResponseModel(files=results_by_path, errors=errors, max_results=max_results, duration=total_time)

    return wrapper


def customizable_file(
    func: Callable[..., FileEntry | FileEntryWithMatches],
) -> Callable[..., Awaitable[dict[str, Any]]]:
    @makefun_wraps(
        func,
        append_args=[
            inspect.Parameter(
                "file_fields",
                inspect.Parameter.KEYWORD_ONLY,
                default=FileExportableField(),
                annotation=FileExportableField,
            ),
        ],
    )
    async def wrapper(
        file_fields: FileExportableField,
        *args: Any,  # pyright: ignore[reportAny]
        **kwargs: Any,  # pyright: ignore[reportAny]
    ) -> dict[str, Any]:
        start_time = time.perf_counter()

        result = func(*args, **kwargs)

        model, line_count = file_fields.apply(result)

        if line_count:
            model = await file_fields.aapply(result)

        model["name"] = result.name
        model.pop("relative_path_str")

        end_time = time.perf_counter()
        logger.info(f"Time taken to apply file fields: {end_time - start_time} seconds")

        return model

    return wrapper
