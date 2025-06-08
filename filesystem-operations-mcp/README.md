# Filesystem Operations MCP Server

This project provides a FastMCP server that exposes tools for performing bulk file and folder operations. It offers tree-sitter based code summarization and natural language text summarization for navigating codebases.

## Features

- **File System Operations**: Read, search, and manipulate files and directories
- **Smart File Type Detection**: Uses Magika for accurate file type detection, even for files without extensions
- **Dynamic Field Selection**: Select which fields to include in the response. Allowing you to control the size of the response. Include summaries, previews, contents, metadata. Include what you need, and exclude what you don't.
- **Code Summarization**: Tree-sitter based code analysis and summarization
- **Text Summarization**: Natural language summarization of text files
- **Flexible Filtering**: Glob-based include/exclude patterns for file operations
- **Content Search**: Full-text search with regex support and context lines
- **Metadata Access**: File and directory metadata (creation time, size, owner, etc.)
- **Hidden File Handling**: Configurable handling of hidden files and directories

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

The server provides the following tools, categorized by their function. Many tools share common parameters:

#### Common Parameters

**Path Parameters**

| Parameter | Type          | Description                                                                 | Example        |
|-----------|---------------|-----------------------------------------------------------------------------|----------------|
| `path`    | `Path` or `list[Path]` | The path(s) to the file(s) or directory(ies) for the operation. Relative to the server's root directory. | `.` (current dir), `../src`, `test.txt`, `["./dir1", "./dir2"]` |

**Filtering Parameters** (Used in Directory Operations)

| Parameter                 | Type          | Description                                                                                                | Example             |
|---------------------------|---------------|------------------------------------------------------------------------------------------------------------|---------------------|
| `include`                 | `list[str]`   | A list of glob patterns to include. Only files matching these patterns will be included. Defaults to `["*"]`. | `["*.py", "*.json"]` |
| `exclude`                 | `list[str]`   | A list of glob patterns to exclude. Files matching these patterns will be excluded.                          | `["*.md", "*.txt"]` |
| `skip_hidden`            | `bool`        | Whether to skip hidden files and directories. Defaults to `true`. | `false`              |

**Search Parameters** (Used in Search Operations)

| Parameter           | Type    | Description                                                                 | Example             |
|---------------------|---------|-----------------------------------------------------------------------------|---------------------|
| `search`            | `str`   | The string or regex pattern to search for within file contents.             | `"hello world"`     |
| `search_is_regex`   | `bool`  | Whether the `search` parameter should be treated as a regex pattern. Defaults to `false`. | `true`              |
| `before`            | `int`   | The number of lines to include before a match in the result chunks. Defaults to `3`. | `1`                 |
| `after`             | `int`   | The number of lines to include after a match in the result chunks. Defaults to `3`.  | `1`                 |

**Field Selection Parameters**

| Parameter           | Type    | Description                                                                 | Example             |
|---------------------|---------|-----------------------------------------------------------------------------|---------------------|
| `file_fields`       | `list[str]` | Fields to include in file responses. See `tips_file_exportable_field()` for options. | `["file_path", "size", "mime_type"]` |
| `directory_fields`  | `list[str]` | Fields to include in directory responses. See `tips_directory_exportable_field()` for options. | `["directory_path", "children_count"]` |

#### Core Operations

**File Operations:**
- `get_files`: Get information about specific files
- `get_text_files`: Get information about text files
- `get_file_matches`: Search file contents with context
- `find_files`: Find files matching glob patterns

**Directory Operations:**
- `get_root`: Get the root directory
- `get_structure`: Get directory structure with configurable depth
- `get_directories`: Get information about specific directories
- `find_dirs`: Find directories matching glob patterns

**Field Information:**
- `tips_file_exportable_field`: Get documentation about available file fields
- `tips_directory_exportable_field`: Get documentation about available directory fields

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