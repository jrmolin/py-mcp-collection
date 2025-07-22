import asyncio
import inspect
import json
import time
from collections.abc import AsyncIterator, Awaitable, Callable
from typing import Annotated, Any, ClassVar, Self

from makefun import wraps as makefun_wraps  # pyright: ignore[reportUnknownVariableType]
from pydantic import BaseModel, ConfigDict, Field, field_serializer, model_validator
from pydantic.fields import computed_field
from pydantic.functional_serializers import model_serializer

from filesystem_operations_mcp.filesystem.nodes import FileEntry, FileEntryTypeEnum, FileEntryWithMatches
from filesystem_operations_mcp.filesystem.summarize.code import summarize_code
from filesystem_operations_mcp.filesystem.summarize.markdown import summarize_markdown
from filesystem_operations_mcp.filesystem.summarize.text import summarizer
from filesystem_operations_mcp.filesystem.utils.workers import gather_results_from_queue, worker_pool
from filesystem_operations_mcp.logging import BASE_LOGGER

logger = BASE_LOGGER.getChild("view")


MAX_SUMMARY_BYTES = 1000
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

    def apply(self, node: FileEntry | FileEntryWithMatches) -> tuple[dict[str, Any], int | None]:
        """Apply the file fields to a file entry."""

        includes: set[str] = self.to_model_dump_include() | {"relative_path_str", "matches", "matches_limit_reached"}

        model = node.model_dump(include=includes, exclude_none=True)

        if model.get("type") and isinstance(model["type"], FileEntryTypeEnum):
            model["type"] = model["type"].value

        return model, self.apply_read_lines_count(node)

    async def aapply(self, node: FileEntry | FileEntryWithMatches) -> dict[str, Any]:  # noqa: PLR0912
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
            try:
                model.update(self._apply_code_summary(node, lines=file_lines.first(1000).lines()))
            except Exception as e:
                model.update({"code_summary_skipped": str(e)})
                logger.warning(f"Error applying code summary: {e}")

        if self.summarize and node.type == FileEntryTypeEnum.TEXT:
            try:
                if node.mime_type == "text/markdown":
                    model.update(self._apply_markdown_summary(lines=file_lines.first(100).lines()))
                elif node.extension == ".asciidoc":
                    model.update(self._apply_asciidoc_summary(lines=file_lines.first(100).lines()))
                else:
                    model.update(self._apply_text_summary(lines=file_lines.first(100).lines()))
            except Exception as e:
                model.update({"text_summary_skipped": str(e)})
                logger.warning(f"Error applying text summary: {e}")

        if "summary" in model and not model["summary"]:
            model.pop("summary")

        return model


class ResponseModel(BaseModel):
    """The response model for the customizable file materializer."""

    model_config: ClassVar[ConfigDict] = ConfigDict(arbitrary_types_allowed=True, use_attribute_docstrings=True)

    warnings: list[str] = Field(default_factory=list, description="An optional list of warnings to include in the response.")

    errors: list[str] = Field(default_factory=list, description="An optional error message to include in the response.")

    max_results: int = Field(..., description="The maximum number of results to return.", exclude=True)

    duration: float = Field(default=0, description="The duration of the request in seconds.")

    results: dict[str, Any] = Field(default_factory=dict, description="The files in the response.")
    """The files in the response."""

    @field_serializer("results")
    def serialize_results(self, results: dict[str, Any]) -> dict[str, Any]:
        return dict(sorted(results.items(), key=lambda x: x[0]))

    @computed_field
    @property
    def result_count(self) -> int:
        return len(self.results)

    @computed_field
    @property
    def limit_reached(self) -> bool:
        """Whether the limit was reached."""
        return self.result_count >= self.max_results

    @model_serializer
    def serialize(self) -> dict[str, Any]:
        """Serialize the model removing empty fields."""
        kv: dict[str, Any] = {
            "result_count": self.result_count,
            "duration": self.duration,
        }

        if self.errors:
            kv["errors"] = self.errors

        if self.warnings:
            kv["warnings"] = self.warnings

        if self.limit_reached:
            kv["limit_reached"] = True
            kv["max_results"] = self.max_results

        if self.results:
            kv["results"] = self.results

        return kv


def customizable_file_materializer(
    func: Callable[..., AsyncIterator[FileEntry | FileEntryWithMatches]],
    default_file_fields: FileExportableField,
) -> Callable[..., Awaitable[ResponseModel]]:
    @makefun_wraps(
        func,
        append_args=[
            inspect.Parameter(
                "basename",
                inspect.Parameter.KEYWORD_ONLY,
                default=default_file_fields.basename,
                annotation=Annotated[bool, FileExportableField.model_fields["basename"]],
            ),
            inspect.Parameter(
                "extension",
                inspect.Parameter.KEYWORD_ONLY,
                default=default_file_fields.extension,
                annotation=Annotated[bool, FileExportableField.model_fields["extension"]],
            ),
            inspect.Parameter(
                "type",
                inspect.Parameter.KEYWORD_ONLY,
                default=default_file_fields.type,
                annotation=Annotated[bool, FileExportableField.model_fields["type"]],
            ),
            inspect.Parameter(
                "mime_type",
                inspect.Parameter.KEYWORD_ONLY,
                default=default_file_fields.mime_type,
                annotation=Annotated[bool, FileExportableField.model_fields["mime_type"]],
            ),
            inspect.Parameter(
                "size",
                inspect.Parameter.KEYWORD_ONLY,
                default=default_file_fields.size,
                annotation=Annotated[bool, FileExportableField.model_fields["size"]],
            ),
            inspect.Parameter(
                "read",
                inspect.Parameter.KEYWORD_ONLY,
                default=default_file_fields.read,
                annotation=Annotated[bool, FileExportableField.model_fields["read"]],
            ),
            inspect.Parameter(
                "read_lines",
                inspect.Parameter.KEYWORD_ONLY,
                default=default_file_fields.read_lines,
                annotation=Annotated[int, FileExportableField.model_fields["read_lines"]],
            ),
            inspect.Parameter(
                "preview",
                inspect.Parameter.KEYWORD_ONLY,
                default=default_file_fields.preview,
                annotation=Annotated[bool, FileExportableField.model_fields["preview"]],
            ),
            inspect.Parameter(
                "preview_lines",
                inspect.Parameter.KEYWORD_ONLY,
                default=default_file_fields.preview_lines,
                annotation=Annotated[int, FileExportableField.model_fields["preview_lines"]],
            ),
            inspect.Parameter(
                "summarize",
                inspect.Parameter.KEYWORD_ONLY,
                default=default_file_fields.summarize,
                annotation=Annotated[bool, FileExportableField.model_fields["summarize"]],
            ),
            inspect.Parameter(
                "created_at",
                inspect.Parameter.KEYWORD_ONLY,
                default=default_file_fields.created_at,
                annotation=Annotated[bool, FileExportableField.model_fields["created_at"]],
            ),
            inspect.Parameter(
                "modified_at",
                inspect.Parameter.KEYWORD_ONLY,
                default=default_file_fields.modified_at,
                annotation=Annotated[bool, FileExportableField.model_fields["modified_at"]],
            ),
            inspect.Parameter(
                "owner",
                inspect.Parameter.KEYWORD_ONLY,
                default=default_file_fields.owner,
                annotation=Annotated[bool, FileExportableField.model_fields["owner"]],
            ),
            inspect.Parameter(
                "group",
                inspect.Parameter.KEYWORD_ONLY,
                default=default_file_fields.group,
                annotation=Annotated[bool, FileExportableField.model_fields["group"]],
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
        basename: bool,
        extension: bool,
        type: bool,  # noqa: A002
        mime_type: bool,
        size: bool,
        read: bool,
        read_lines: int,
        preview: bool,
        preview_lines: int,
        summarize: bool,
        created_at: bool,
        modified_at: bool,
        owner: bool,
        group: bool,
        max_results: int,
        *args: Any,  # pyright: ignore[reportAny]
        **kwargs: Any,  # pyright: ignore[reportAny]
    ) -> ResponseModel:
        timers: dict[str, float] = {
            "start": time.perf_counter(),
        }

        file_fields = FileExportableField(
            read=read,
            read_lines=read_lines,
            preview=preview,
            preview_lines=preview_lines,
            summarize=summarize,
            created_at=created_at,
            modified_at=modified_at,
            basename=basename,
            extension=extension,
            type=type,
            mime_type=mime_type,
            size=size,
            owner=owner,
            group=group,
        )

        logger.info(f"Handling request to {func.__name__} with file_fields: {file_fields} args: {args} and kwargs: {kwargs}")

        errors: list[str] = []

        warnings: list[str] = []

        work_queue: asyncio.Queue[FileEntry | FileEntryWithMatches] = asyncio.Queue()

        result_iter: AsyncIterator[FileEntry | FileEntryWithMatches] = func(*args, **kwargs)

        results_by_path: dict[str, Any] = {}

        async for node in result_iter:
            if max_results and len(results_by_path) >= max_results:
                logger.info(f"Reached max results: {max_results} for call to {func.__name__} with args: {args} and kwargs: {kwargs}")
                warnings.append(
                    f"Reached max_results {max_results} results. To get more results, refine the query or increase max_results."
                )
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

        return ResponseModel(results=results_by_path, errors=errors, warnings=warnings, max_results=max_results, duration=total_time)

    signature = inspect.signature(wrapper)

    signature = signature.replace(return_annotation=ResponseModel)

    wrapper.__signature__ = signature  # pyright: ignore[reportFunctionMemberAccess]

    return wrapper
