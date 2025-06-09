# Filesystem Operations MCP Server

This project provides a FastMCP server that exposes tools for performing bulk file and folder operations. It offers tree-sitter based code summarization and natural language text summarization for navigating codebases.

## Features

This server provides a comprehensive set of tools for interacting with the filesystem, designed for efficiency and flexibility:

-   **Comprehensive File & Directory Management**: Create, delete, append, insert, and replace content within files, and manage directories with robust error handling.
-   **Intelligent File Type Detection**: Utilizes Magika for highly accurate file type identification, including detection of binary, code, text, and data files, even for those lacking extensions.
-   **Customizable Data Retrieval**: Offers granular control over the returned data for files and directories, allowing users to select specific fields like path, size, type, content previews, and detailed metadata (creation/modification times, owner, group).
-   **Advanced Content Summarization**:
    -   **Code Summarization**: Leverages Tree-sitter to parse and provide structured summaries of code, extracting definitions and documentation.
    -   **Text Summarization**: Employs natural language processing techniques to generate concise summaries of text files.
-   **Powerful Search & Filtering**:
    -   **Glob-based Filtering**: Supports flexible glob patterns for including or excluding files and directories in searches and operations.
    -   **Content Search**: Enables full-text searches within files, supporting both literal strings and regular expressions, with options to include contextual lines around matches.
-   **Rich Metadata Access**: Provides access to detailed file and directory metadata, including size, creation/modification timestamps, and ownership information.
-   **Hidden Item Control**: Configurable options to include or skip hidden files and directories during various operations.
-   **Patch-based File Modifications**: Supports precise and validated modifications to file content through insert, append, delete, and replace patches.

## VS Code McpServer Usage
1. Open the command palette (Ctrl+Shift+P or Cmd+Shift+P).
2. Type "Settings" and select "Preferences: Open User Settings (JSON)".
3. Add the following MCP Server configuration

```json
{
    "mcp": {
        "servers": {
            "Filesystem Operations": {
                "command": "uvx",
                "args": [
                    "git+https://github.com/strawgate/py-mcp-collection.git#subdirectory=filesystem-operations-mcp",
                ]
            }
        }
    }
}
```

## Roo Code / Cline McpServer Usage
Simply add the following to your McpServer configuration. Edit the AlwaysAllow list to include the tools you want to use without confirmation.

```
    "Filesystem Operations": {
      "command": "uvx",
      "args": [
        "git+https://github.com/strawgate/py-mcp-collection.git#subdirectory=filesystem-operations-mcp"
      ],
      "alwaysAllow": []
    },
```

## Development

To set up the project, use `uv sync`:

```bash
uv sync
```

For development, including testing dependencies:

```bash
uv sync --group dev
```

## Usage

### Running the MCP Server

The server can be run using `uv run`:

```bash
uv run filesystem_operations_mcp
```

Optional command-line arguments:
- `--root-dir`: The allowed filesystem paths for filesystem operations. Defaults to the current working directory for the server.
- `--mcp-transport`: The transport to use for the MCP server. Defaults to stdio (options: stdio, sse, streamable-http).

Note: When running the server, the `--root-dir` parameter determines the base directory for all file operations. Paths provided to the tools are relative to this root directory.

### Available Tools

The server provides a comprehensive suite of tools, categorized by their function, to facilitate various filesystem operations. Many tools share common parameters for consistent usage.

#### Common Parameters

These parameters are frequently used across multiple tools to refine operations or control output.

**Path Parameters**

| Parameter | Type | Description | Example |
|---|---|---|---|
| `file_path` | `str` | The root-relative path to the file for the operation. | `"path/to/file.txt"` |
| `file_paths` | `list[str]` | A list of root-relative file paths for the operation. | `["path/to/file1.txt", "path/to/file2.txt"]` |
| `directory_path` | `str` | The root-relative path to the directory for the operation. | `"path/to/directory"` |
| `directory_paths` | `list[str]` | A list of root-relative directory paths for the operation. | `["path/to/dir1", "path/to/dir2"]` |

**Filtering Parameters** (Used in Directory Operations)

| Parameter | Type | Description | Example |
|---|---|---|---|
| `glob` | `str` | A glob pattern to search for files or directories. | `"*.py"`, `"src/**"` |
| `includes` | `list[str]` | A list of glob patterns to include. Only files/directories matching these patterns will be included. | `["*.py", "*.json"]` |
| `excludes` | `list[str]` | A list of glob patterns to exclude. Files/directories matching these patterns will be excluded. | `["*.md", "*.txt"]` |
| `skip_hidden` | `bool` | Whether to skip hidden files and directories. Defaults to `true`. | `false` |
| `skip_empty` | `bool` | Whether to skip empty directories. Defaults to `true`. | `false` |
| `depth` | `int` | The depth of the directory structure to retrieve. `0` means immediate children only. | `1`, `3` |

**Search Parameters** (Used in Search Operations)

| Parameter | Type | Description | Example |
|---|---|---|---|
| `pattern` | `str` | The string or regex pattern to search for within file contents. | `"hello world"` |
| `pattern_is_regex` | `bool` | Whether the `pattern` parameter should be treated as a regex pattern. Defaults to `false`. | `true` |
| `before` | `int` | The number of lines to include before a match in the result. | `2` |
| `after` | `int` | The number of lines to include after a match in the result. | `2` |

**Field Selection Parameters**

| Parameter | Type | Description | Example |
|---|---|---|---|
| `file_fields` | `FileExportableField` | A Pydantic model to specify which fields of a `FileEntry` to include in the response. | `{"file_path": true, "size": true, "read_text": true}` |
| `directory_fields` | `DirectoryExportableField` | A Pydantic model to specify which fields of a `DirectoryEntry` to include in the response. | `{"directory_path": true, "files_count": true}` |
| `include_summaries` | `bool` | Whether to include code and text summaries for files. Defaults to `false`. | `true` |

#### Core Operations

These tools provide fundamental capabilities for managing and querying the filesystem.

#### File Operations

-   `get_files(file_paths: list[str], file_fields: FileExportableField, include_summaries: bool)`: Retrieves detailed information for a list of specified files.
-   `get_text_files(file_paths: list[str], file_fields: FileExportableField, include_summaries: bool)`: Retrieves detailed information for a list of specified text files.
-   `get_file_matches(file_path: str, pattern: str, pattern_is_regex: bool, before: int, after: int)`: Searches for a pattern within a file and returns matching lines with optional context.
-   `find_files(glob: str, directory_path: str, includes: list[str], excludes: list[str], skip_hidden: bool)`: Finds files matching a glob pattern within a directory, with optional filtering.
-   `search_files(glob: str, pattern: str, pattern_is_regex: bool, directory_path: str, includes: list[str], excludes: list[str], skip_hidden: bool)`: Searches for files containing a specific pattern within a directory, with optional filtering.

#### Directory Operations

-   `get_root(directory_fields: DirectoryExportableField)`: Retrieves information about the root directory of the filesystem.
-   `get_structure(depth: int, includes: list[str], excludes: list[str], skip_hidden: bool, skip_empty: bool)`: Retrieves the directory structure up to a specified depth, with optional filtering.
-   `get_directories(directory_paths: list[str], directory_fields: DirectoryExportableField)`: Retrieves detailed information for a list of specified directories.
-   `find_dirs(glob: str, directory_path: str, includes: list[str], excludes: list[str], skip_hidden: bool)`: Finds directories matching a glob pattern within a directory, with optional filtering.

#### File Modification Operations

-   `create_file(file_path: str, content: str)`: Creates a new file with the specified content.
-   `append_file(file_path: str, content: str)`: Appends content to an existing file.
-   `delete_file_lines(file_path: str, line_numbers: list[int])`: Deletes specific lines from a file.
-   `replace_file_lines(file_path: str, patches: list[FileReplacePatch])`: Replaces lines in a file based on provided patches.
-   `insert_file_lines(file_path: str, patches: list[FileInsertPatch])`: Inserts lines into a file based on provided patches.
-   `delete_file(file_path: str)`: Deletes a specified file.

#### Directory Modification Operations

-   `create_directory(directory_path: str)`: Creates a new directory.
-   `delete_directory(directory_path: str)`: Deletes an empty directory.

## Development & Testing

- Tests are located in the `tests/` directory
- Tests use real filesystem operations with temporary directories
- Comprehensive test coverage for all major functionality
- Use `pytest` for running tests:

```bash
pytest
```

## License

See [LICENSE](LICENSE).