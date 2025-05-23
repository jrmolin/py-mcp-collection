from logging import getLogger
from pathlib import Path
from typing import Any

from fastmcp.server.context import Context
from fastmcp.server.proxy import ProxyTool
from mcp.types import BlobResourceContents, EmbeddedResource, ImageContent, TextContent, TextResourceContents

from mcp_oops.models.errors import (
    MCPoopsRedirectSerializationError,
    MCPoopsRedirectTooLargeError,
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


def error_on_large_response(tool_name: str, tool_response: list[TextContent | ImageContent | EmbeddedResource], max_size: int):
    total_size = len(convert_response_to_serializable(tool_response))

    if total_size > max_size:
        raise MCPoopsResponseTooLargeError(tool_name, total_size, max_size)


def error_on_large_redirect(tool_name: str, tool_response: list[TextContent | ImageContent | EmbeddedResource], max_size: int):
    total_size = len(convert_response_to_serializable(tool_response))
    if total_size > max_size:
        raise MCPoopsRedirectTooLargeError(tool_name, total_size, max_size)


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


class InterceptingProxyTool(ProxyTool):
    """
    A ProxyTool subclass that intercepts the run method to handle redirection.
    """

    max_response_size: int
    max_redirected_response_size: int
    split_redirected_responses: int

    async def run(
        self,
        arguments: dict[str, Any],
        context: Context | None = None,
    ) -> list[TextContent | ImageContent | EmbeddedResource]:
        # Extract redirect_to from arguments
        redirect_to = arguments.pop("redirect_to", None)

        response = await super().run(arguments=arguments, context=context)

        error_on_large_response(self.name, response, self.max_response_size)

        if redirect_to:
            error_on_large_redirect(self.name, response, self.max_redirected_response_size)
            file_paths_with_sizes = redirect_response(self.name, response, redirect_to, self.split_redirected_responses)
            return [TextContent(type="text", text=f"Redirected tool responses to {file_paths_with_sizes}")]

        error_on_large_response(self.name, response, self.max_response_size)

        return response
