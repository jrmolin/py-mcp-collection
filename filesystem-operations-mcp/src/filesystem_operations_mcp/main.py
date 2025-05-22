import asyncio
from pathlib import Path
from typing import Any

import asyncclick as click
import pydantic_core
import yaml
from fastmcp import Context, FastMCP
from fastmcp.contrib.mcp_mixin.mcp_mixin import MCPMixin, mcp_tool
from pydantic import BaseModel, Field

from filesystem_operations_mcp.filesystem.models import (
    FileEntry,
    FileEntryChunkedContent,
    FileEntryContent,
    FileEntryPreview,
    FileEntryWithSize,
    FlatDirectoryResult,
)
from filesystem_operations_mcp.filesystem.server import FilesystemServer
from filesystem_operations_mcp.filesystem.skip import DEFAULT_SKIP_LIST, DEFAULT_SKIP_READ

PATH_DIR_SINGLE_FIELD = Field(..., description="A single directory to operate on.")
PATH_FILE_SINGLE_FIELD = Field(..., description="A single file to operate on.")

PATH_DIR_MULTI_FIELD = Field(default_factory=list, min_length=1, description="A list of directories to operate on.")
PATH_FILE_MULTI_FIELD = Field(default_factory=list, min_length=1, description="A list of files to operate on.")

SEARCH_FIELD = Field(
    default_factory=list,
    description="A string to search for. If `search_is_regex` is `True`, this will be treated as a regex pattern. Otherwise, only files that contain the exact string will be included.",
)
SEARCH_IS_REGEX_FIELD = Field(default=False, description="Whether the search string is a regex pattern.")

BEFORE_LINES_FIELD = Field(default=3, description="The number of lines to include before the match.")
AFTER_LINES_FIELD = Field(default=3, description="The number of lines to include after the match.")

CONTENT_FIELD = Field(..., description="The content to write to the file.")

INCLUDE_FILTERS_FIELD = Field(default_factory=list, description="A list of glob patterns to use to constrain the results.")
EXCLUDE_FILTERS_FIELD = Field(default_factory=list, description="A list of glob patterns to use to exclude from the results.")

RECURSE_FIELD = Field(default=False, description="Whether to recurse into subdirectories.")
BYPASS_DEFAULT_EXCLUSIONS_FIELD = Field(
    default=False,
    description="Whether to bypass the default exclusions. Not typical, do not set this unless you're sure you're searching for hidden or system files.",
)


class FileServer(MCPMixin):
    def __init__(self, filesystem_server: FilesystemServer):
        self.filesystem_server = filesystem_server

    @mcp_tool()
    def read(self, ctx: Context, path: Path = PATH_FILE_SINGLE_FIELD) -> str:
        """Read the contents of a file.

        Returns:
            The contents of the file.
        """
        ctx.info(f"Request to read file {path}")
        return self.filesystem_server.read_file(path)

    @mcp_tool()
    def preview(self, ctx: Context, path: Path = PATH_FILE_SINGLE_FIELD) -> str:
        """Preview the contents of a file.

        Returns:
            A preview of the contents of the file.
        """
        ctx.info(f"Request to preview file {path}")
        return self.filesystem_server.preview_file(path)

    @mcp_tool()
    def delete(self, ctx: Context, path: Path = PATH_FILE_SINGLE_FIELD) -> bool:
        """Delete a file.

        Returns:
            True if the file was deleted. Raises an error otherwise.
        """
        ctx.info(f"Request to delete file {path}")
        self.filesystem_server.delete_file(path)
        return True

    @mcp_tool()
    def search(
        self,
        ctx: Context,
        path: Path = PATH_FILE_SINGLE_FIELD,
        search: str = SEARCH_FIELD,
        search_is_regex: bool = SEARCH_IS_REGEX_FIELD,
        before: int = BEFORE_LINES_FIELD,
        after: int = AFTER_LINES_FIELD,
    ) -> FileEntryChunkedContent | None:
        """Search a specific file for a string or regex pattern.

        Returns:
            A list of chunks containing the search results.

        Example:
            >>> search(path="a.txt", search="hello", search_is_regex=False, before=3, after=3)
            [
                FileEntryChunkedContent(path="a.txt", content="hello world"),
            ]
        """
        ctx.info(f"Request to search file {path} for {search}")
        return self.filesystem_server.search_file(path=path, search=search, search_is_regex=search_is_regex, before=before, after=after)

    @mcp_tool()
    def create(self, ctx: Context, path: Path = PATH_FILE_SINGLE_FIELD, content: str = CONTENT_FIELD) -> bool:
        """Create a file.

        Returns:
            True if the file was created. Raises an error otherwise.
        """
        ctx.info(f"Request to create file {path}")

        self.filesystem_server.create_file(path, content)

        return True

    @mcp_tool()
    def append(self, ctx: Context, path: Path = PATH_FILE_SINGLE_FIELD, content: str = CONTENT_FIELD) -> bool:
        """Append to a file.

        Returns:
            True if the file was appended to. Raises an error otherwise.
        """

        ctx.info(f"Request to append to file {path}")

        self.filesystem_server.append_file(path, content)

        return True


class DirectoryServer(MCPMixin):
    def __init__(self, filesystem_server: FilesystemServer):
        self.filesystem_server = filesystem_server

    @mcp_tool(name="create")
    def create_dir(self, ctx: Context, path: Path = PATH_DIR_SINGLE_FIELD) -> bool:
        """Create a directory.

        Returns:
            True if the directory was created. Raises an error otherwise.
        """

        ctx.info(f"Request to create directory {path}")
        self.filesystem_server.create_dir(path)
        return True

    @mcp_tool(name="list")
    def list_contents(
        self,
        ctx: Context,
        path: list[Path] = PATH_DIR_MULTI_FIELD,
        include: list[str] = INCLUDE_FILTERS_FIELD,
        exclude: list[str] = EXCLUDE_FILTERS_FIELD,
        recurse: bool = RECURSE_FIELD,
        bypass_default_exclusions: bool = BYPASS_DEFAULT_EXCLUSIONS_FIELD,
    ) -> FlatDirectoryResult[FileEntry]:
        """List the contents of a directory.

        Returns:
            A flat directory result containing the contents of listed directories.

        Example:
            >>> list(recurse=True, include=["*.txt"], exclude=["*.md"])
            {
                ".": {
                    "a.txt": FileEntry(path="a.txt", size=100),
                    "b.txt": FileEntry(path="b.txt", size=100),
                },
                "subdir": {
                    "c.txt": FileEntry(path="subdir/c.txt", size=100),
                },
            }
        """

        if not bypass_default_exclusions:
            exclude = exclude or []
            exclude.extend(DEFAULT_SKIP_LIST)

        ctx.info(f"Request to list contents of {path}: recurse={recurse}, include={include}, exclude={exclude}")
        return self.filesystem_server.flat_dir(FileEntryWithSize, path, recurse, include, exclude)

    @mcp_tool(name="preview")
    def preview_contents(
        self,
        ctx: Context,
        path: list[Path] = PATH_DIR_MULTI_FIELD,
        include: list[str] = INCLUDE_FILTERS_FIELD,
        exclude: list[str] = EXCLUDE_FILTERS_FIELD,
        recurse: bool = RECURSE_FIELD,
        bypass_default_exclusions: bool = BYPASS_DEFAULT_EXCLUSIONS_FIELD,
    ) -> FlatDirectoryResult[FileEntryPreview]:
        """Preview the contents of the files in a directory.

        Returns:
            A flat directory result containing the previewed contents of listed directories. If the file is smaller than the preview
            size, the preview will be placed in the contents field. A preview will always end in `...`

        Example:
            >>> preview(recurse=True, include=["*.txt"], exclude=["*.md"])
            {
                ".": {
                    "a.txt": FileEntryPreview(path="a.txt", size=11, content="hello world"),
                },
                "subdir": {
                    "c.txt": FileEntryPreview(path="subdir/c.txt", size=1000, preview="hello world how are you doing today..."),
                },
            }
        """
        if not bypass_default_exclusions:
            exclude = exclude or []
            exclude.extend(DEFAULT_SKIP_READ)
            exclude.extend(DEFAULT_SKIP_LIST)

        ctx.info(f"Request to preview contents of {path}: recurse={recurse}, include={include}, exclude={exclude}")
        return self.filesystem_server.flat_dir(FileEntryPreview, path, recurse, include, exclude)

    @mcp_tool(name="read")
    def read_contents(
        self,
        ctx: Context,
        path: list[Path] = PATH_DIR_MULTI_FIELD,
        include: list[str] = INCLUDE_FILTERS_FIELD,
        exclude: list[str] = EXCLUDE_FILTERS_FIELD,
        recurse: bool = RECURSE_FIELD,
        bypass_default_exclusions: bool = BYPASS_DEFAULT_EXCLUSIONS_FIELD,
    ) -> FlatDirectoryResult[FileEntryContent]:
        """Read the contents of the files in a directory.

        Returns:
            A flat directory result containing the read contents of listed directories.

        Example:
            >>> read_all_contents(recurse=True, include=["*.txt"], exclude=["*.md"])
            {
                ".": {
                    "a.txt": FileEntryContent(path="a.txt", content="hello world"),
                },
            }
        """

        if not bypass_default_exclusions:
            exclude = exclude or []
            exclude.extend(DEFAULT_SKIP_READ)
            exclude.extend(DEFAULT_SKIP_LIST)

        ctx.info(f"Request to read contents of {path}: recurse={recurse}, include={include}, exclude={exclude}")
        return self.filesystem_server.flat_dir(FileEntryContent, path, recurse, include, exclude)

    @mcp_tool(name="search")
    def search_contents(
        self,
        ctx: Context,
        path: list[Path] = PATH_DIR_MULTI_FIELD,
        search: str = SEARCH_FIELD,
        include: list[str] = INCLUDE_FILTERS_FIELD,
        exclude: list[str] = EXCLUDE_FILTERS_FIELD,
        recurse: bool = RECURSE_FIELD,
        before: int = BEFORE_LINES_FIELD,
        after: int = AFTER_LINES_FIELD,
        search_is_regex: bool = SEARCH_IS_REGEX_FIELD,
        bypass_default_exclusions: bool = BYPASS_DEFAULT_EXCLUSIONS_FIELD,
    ) -> FlatDirectoryResult[FileEntryChunkedContent]:
        """Search the contents of the files in a directory.

        Returns:
            A flat directory result containing the search results.

        Example:
            >>> search(recurse=True, include=["*.txt"], exclude=["*.md"], before=3, after=3, search_is_regex=False)
            {
                ".": {
                    "a.txt": FileEntryChunkedContent(path="a.txt", content="hello world"),
                },
            }
        """
        if not bypass_default_exclusions:
            exclude = exclude or []
            exclude.extend(DEFAULT_SKIP_READ)
            exclude.extend(DEFAULT_SKIP_LIST)

        ctx.info(
            f"Request to search contents of {path}: recurse={recurse}, include={include}, exclude={exclude}, before={before}, after={after}, search_is_regex={search_is_regex}"  # noqa: E501
        )
        return self.filesystem_server.search_content(
            path=path,
            search=search,
            recurse=recurse,
            include=include,
            exclude=exclude,
            before=before,
            after=after,
            search_is_regex=search_is_regex,
        )


ROOT_DIR_HELP = "The allowed filesystem paths for filesystem operations. Defaults to the current working directory for the server."
MAX_SIZE_HELP = "The maximum size of a result in bytes before throwing an exception. Defaults to 400 kb or about 100k tokens."
SERIALIZE_AS_HELP = "The format to serialize the response in. Defaults to Yaml"
MCP_TRANSPORT_HELP = "The transport to use for the MCP server. Defaults to stdio."


@click.command()
@click.option("--root-dir", type=str, default=Path.cwd(), help=ROOT_DIR_HELP)
@click.option("--max-size", type=int, default=400_000, help=MAX_SIZE_HELP)
@click.option("--serialize-as", type=click.Choice(["json", "yaml"]), default="json", help=SERIALIZE_AS_HELP)
@click.option("--mcp-transport", type=click.Choice(["stdio", "sse", "streamable-http"]), default="stdio", help=MCP_TRANSPORT_HELP)
async def cli(root_dir: str, max_size: int, serialize_as: str, mcp_transport: str):
    def yaml_serializer(data: Any) -> str:
        if isinstance(data, BaseModel):
            data = pydantic_core.to_jsonable_python(data, fallback=str, exclude_none=True)

        result = yaml.safe_dump(data, width=300, sort_keys=False, default_flow_style=False)

        if len(result) > max_size:
            msg = f"Result is too large {len(result)} bytes. Max size is {max_size} bytes. Use more specific filters to return less data."
            raise ValueError(msg)

        return result

    def json_serializer(data: Any) -> str:
        result = pydantic_core.to_json(data, fallback=str, indent=2, exclude_none=True).decode()

        if len(result) > max_size:
            msg = f"Result is too large {len(result)} bytes. Max size is {max_size} bytes. Use more specific filters to return less data."
            raise ValueError(msg)

        return result

    serializer = yaml_serializer if serialize_as == "yaml" else json_serializer

    mcp = FastMCP(name="Local Filesystem Operations MCP", tool_serializer=serializer)

    server = FilesystemServer(Path(root_dir))

    directory_server = DirectoryServer(server)
    directory_server.register_tools(mcp, prefix="directory")

    file_server = FileServer(server)
    file_server.register_tools(mcp, prefix="file")

    await mcp.run_async(transport=mcp_transport)


def run_mcp():
    asyncio.run(cli())


if __name__ == "__main__":
    run_mcp()
