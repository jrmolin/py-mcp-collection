from logging import getLogger
from pathlib import Path
from typing import Any

from fastmcp.contrib.tool_transformer.types import PostToolCallHookProtocol
from mcp.types import BlobResourceContents, EmbeddedResource, ImageContent, TextContent, TextResourceContents

from mcp_oops.models.errors import (
    MCPoopsRedirectSerializationError,
    MCPoopsResponseTooLargeError,
    MCPoopsWriteDataError,
)

logger = getLogger(__name__)


def convert_response_to_serializable(response: list[TextContent | ImageContent | EmbeddedResource]) -> str:
    serializable_response: list[str] = []

    for item in response:
        if isinstance(item, TextContent):
            serializable_response.append(item.text)
        elif isinstance(item, ImageContent):
            serializable_response.append(item.data)
        elif isinstance(item, EmbeddedResource) and isinstance(item.resource, TextResourceContents):
            serializable_response.append(item.resource.text)
        elif isinstance(item, EmbeddedResource) and isinstance(item.resource, BlobResourceContents):
            serializable_response.append(item.resource.blob)

    return "\n".join(serializable_response)


def write_data_to_file(data: str, file_path: str, split_size: int):
    file_paths_with_sizes: list[tuple[str, int]] = []

    for i in range(0, len(data), split_size):
        chunk = data[i : i + split_size]
        indexed_file_path = file_path.split(".")[0] + f"_{i}.json" if i > 0 else file_path
        with Path(indexed_file_path).open("w", encoding="utf-8") as f:
            f.write(chunk)
        logger.info(f"Wrote data to {indexed_file_path}")
        file_paths_with_sizes.append((indexed_file_path, len(chunk)))

    return file_paths_with_sizes


def redirect_response(
    tool_name: str,
    response: list[TextContent | ImageContent | EmbeddedResource],
    redirect_to: str,
    split_redirected_responses: int,
) -> list[tuple[str, int]]:
    try:
        blob: str = convert_response_to_serializable(response)
    except Exception as e:
        raise MCPoopsRedirectSerializationError(tool_name) from e

    try:
        file_paths_with_sizes = write_data_to_file(blob, redirect_to, split_redirected_responses)
    except Exception as e:
        raise MCPoopsWriteDataError(tool_name) from e

    logger.info(f"Redirected tool response to {redirect_to}")
    return file_paths_with_sizes


def get_content_size(response: list[TextContent | ImageContent | EmbeddedResource]) -> int:
    serializable_response = convert_response_to_serializable(response)
    return len(serializable_response)


def get_post_call_hook(
    limit_response_size: int,
) -> PostToolCallHookProtocol:
    async def post_call_hook(
        response: list[TextContent | ImageContent | EmbeddedResource],
        tool_args: dict[str, Any],
        hook_args: dict[str, Any],
    ) -> None:
        logger.debug("Post call hook called with response: %s", response)
        logger.debug("Post call hook called with tool args: %s", tool_args)
        logger.debug("Post call hook called with hook args: %s", hook_args)

        total_size = get_content_size(response)
        if total_size > limit_response_size:
            msg = f"Response for tool is too large: {total_size} bytes. The maximum size is {limit_response_size} bytes."
            raise MCPoopsResponseTooLargeError(msg)

    return post_call_hook
