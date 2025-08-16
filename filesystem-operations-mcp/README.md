At the end of the day, every LLM-driven Code Agent is a wrapper around RipGrep along with the ability to read and write files. 

# Find 🎯, Summarize 📝,  Modify 🔧

This project provides an MCP server that acts as the critical building block for your LLM-driven Code Agent!
-   **Powerful File 🔍 Search & Discovery 🔎**: Extremely fast filesystem search capabilities. Search for files by name, content, and more.
-   **Text and Code 📝 Summarization**: Leverages Tree-sitter and (non-LLM, i.e. FREE!) Natural Language Processing to parse and provide structured summaries of code, extracting definitions and documentation.
-   **Patch-based File Modifications**: Supports precise and validated modifications to file content through insert, append, delete, and replace patches.
-   **Comprehensive File & Directory Management 📂**: Create, delete, append, insert, and replace content within files, and manage directories with robust error handling.
-   **Magical File Type Detection 🧙**: Utilizes Magika for highly accurate file type identification, including detection of binary, code, text, and data files, even for those lacking extensions.
-   **Customizable Data Retrieval 📊**: Offers granular control over the returned data for files and directories, allowing users to select specific fields like path, size, type, content previews, and detailed metadata (creation/modification times, owner, group).

Note: If you're interested in the RipGrep part check out [rpygrep](https://github.com/strawgate/rpygrep).

# Get Started

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
                    "filesystem-operations-mcp",
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
        "filesystem-operations-mcp"
      ],
      "alwaysAllow": []
    },
```

### Available Tools

The server provides a comprehensive suite of tools, categorized by their function, to facilitate various filesystem operations.

#### File Search & Discovery

-   `find_files(glob: str, directory_path: str, includes: list[str], excludes: list[str], skip_hidden: bool)`: Finds files matching a glob pattern within a directory, with optional filtering.
-   `search_files(glob: str, pattern: str, pattern_is_regex: bool, directory_path: str, includes: list[str], excludes: list[str], skip_hidden: bool)`: Searches for files containing a specific pattern within a directory, with optional filtering.
-   `get_file_type_options()`: Returns available file types for filtering operations.

#### File Information & Content

-   `get_files(file_paths: list[str], file_fields: FileExportableField, include_summaries: bool)`: Retrieves detailed information for a list of specified files.
-   `read_file_lines(file_path: str, start: int, count: int)`: Reads specific lines from a file with pagination support.
-   `read_file_lines_bulk(file_paths: list[str], start: int, count: int)`: Reads lines from multiple files in bulk.

#### Directory Structure

-   `get_structure(depth: int, includes: list[str], excludes: list[str], skip_hidden: bool, skip_empty: bool, max_results: int)`: Retrieves the directory structure up to a specified depth, with optional filtering and result limiting.

#### File Creation & Modification

-   `create_file(file_path: str, content: list[str])`: Creates a new file with the specified content.
-   `replace_file(file_path: str, content: list[str])`: Replaces the entire content of a file.
-   `append_file(file_path: str, content: list[str])`: Appends content to an existing file.
-   `delete_file(file_path: str)`: Deletes a specified file.

#### Line-level File Modifications

-   `delete_file_lines(file_path: str, line_numbers: list[int])`: Deletes specific lines from a file.
-   `replace_file_lines(file_path: str, start_line_number: int, current_lines: list[str], new_lines: list[str])`: Replaces specific lines in a file.
-   `replace_file_lines_bulk(file_path: str, patches: list[FileReplacePatch])`: Replaces lines in a file using bulk patches.
-   `insert_file_lines(file_path: str, start_line_number: int, current_line: str, before_or_after: str, insert_lines: list[str])`: Inserts lines into a file at a specific position.
-   `insert_file_lines_bulk(file_path: str, patches: list[FileInsertPatch])`: Inserts lines into a file using bulk patches.

#### Directory Management

-   `create_directory(directory_path: str)`: Creates a new directory.
-   `delete_directory(directory_path: str, recursive: bool)`: Deletes a directory, optionally recursively.

#### Common Parameters

These parameters are frequently used across multiple tools to refine operations or control output.

**Path Parameters**

| Parameter | Type | Description | Example |
|---|---|---|---|
| `file_path` | `str` | The root-relative path to the file for the operation. | `"path/to/file.txt"` |
| `file_paths` | `list[str]` | A list of root-relative file paths for the operation. | `["path/to/file1.txt", "path/to/file2.txt"]` |
| `directory_path` | `str` | The root-relative path to the directory for the operation. | `"path/to/directory"` |

**Filtering Parameters**

| Parameter | Type | Description | Example |
|---|---|---|---|
| `glob` | `str` | A glob pattern to search for files or directories. | `"*.py"`, `"src/**"` |
| `includes` | `list[str]` | A list of glob patterns to include. Only files/directories matching these patterns will be included. | `["*.py", "*.json"]` |
| `excludes` | `list[str]` | A list of glob patterns to exclude. Files/directories matching these patterns will be excluded. | `["*.md", "*.txt"]` |
| `skip_hidden` | `bool` | Whether to skip hidden files and directories. Defaults to `true`. | `false` |
| `skip_empty` | `bool` | Whether to skip empty directories. Defaults to `true`. | `false` |
| `depth` | `int` | The depth of the directory structure to retrieve. `0` means immediate children only. | `1`, `3` |

**Search Parameters**

| Parameter | Type | Description | Example |
|---|---|---|---|
| `pattern` | `str` | The string or regex pattern to search for within file contents. | `"hello world"` |
| `pattern_is_regex` | `bool` | Whether the `pattern` parameter should be treated as a regex pattern. Defaults to `false`. | `true` |

**Content Parameters**

| Parameter | Type | Description | Example |
|---|---|---|---|
| `content` | `list[str]` | Lines of content to write to a file. | `["Line 1", "Line 2"]` |
| `start_line_number` | `int` | The 1-indexed line number to start operations from. | `1` |
| `count` | `int` | The number of lines to read or process. | `10` |
| `line_numbers` | `list[int]` | 1-indexed line numbers for deletion operations. | `[1, 3, 5]` |

**Field Selection Parameters**

| Parameter | Type | Description | Example |
|---|---|---|---|
| `file_fields` | `FileExportableField` | A Pydantic model to specify which fields of a `FileEntry` to include in the response. | `{"file_path": true, "size": true, "read_text": true}` |
| `include_summaries` | `bool` | Whether to include code and text summaries for files. Defaults to `false`. | `true` |

## Advanced Usage

Optional command-line arguments:
- `--root-dir`: The allowed filesystem paths for filesystem operations. Defaults to the current working directory for the server.
- `--root-git-url`: Clone and work with a git repository instead of a local directory.
- `--mcp-transport`: The transport to use for the MCP server. Defaults to stdio (options: stdio, sse, streamable-http).
- `--default-summarize`: Whether to enable summarization by default. Defaults to true.

Note: When running the server, the `--root-dir` parameter determines the base directory for all file operations. Paths provided to the tools are relative to this root directory.

## License

See [LICENSE](LICENSE).

## Development

See [CONTRIBUTING](CONTRIBUTING.md).