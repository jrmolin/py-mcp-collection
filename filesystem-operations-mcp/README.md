# Filesystem Operations MCP Server

This project provides a FastMCP server that exposes tools for performing bulk file and folder operations. It includes centralized exception handling for filesystem operations.

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
- `--max-size`: The maximum size of a result in bytes before throwing an exception. Defaults to 400 kb.
- `--serialize-as`: The format to serialize the response in. Defaults to json (options: json, yaml).
- `--mcp-transport`: The transport to use for the MCP server. Defaults to stdio (options: stdio, sse, streamable-http).

Note: When running the server, the `--root-dir` parameter determines the base directory for all file operations. Paths provided to the tools are relative to this root directory. During testing, the server's working directory was observed to be the repository root `/Users/billeaston/Documents/repos/py-mcp-collection/filesystem-operations-mcp`. Directory listing tools (`directory_list`, `directory_preview`, `directory_read`) when starting from the root (`.`) appear to be scoped to the server's root directory and its subdirectories.

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
| `bypass_default_exclusions` | `bool`        | Whether to bypass the server's default exclusions (hidden folders, cache directories, compiled files). Defaults to `false`. | `true`              |

**Search Parameters** (Used in Search Operations)

| Parameter           | Type    | Description                                                                 | Example             |
|---------------------|---------|-----------------------------------------------------------------------------|---------------------|
| `search`            | `str`   | The string or regex pattern to search for within file contents.             | `"hello world"`     |
| `search_is_regex`   | `bool`  | Whether the `search` parameter should be treated as a regex pattern. Defaults to `false`. | `true`              |
| `before`            | `int`   | The number of lines to include before a match in the result chunks. Defaults to `3`. | `1`                 |
| `after`             | `int`   | The number of lines to include after a match in the result chunks. Defaults to `3`.  | `1`                 |

#### Tool Specific Parameters

**File Operations:**

- `file_read`: Read the contents of a specific file.
  - Parameters: `path` (Path)
- `file_preview`: Get a preview of the contents of a specific file.
  - Parameters: `path` (Path)
- `file_delete`: Delete a specific file.
  - Parameters: `path` (Path)
- `file_search`: Search a specific file for a string or regex pattern.
  - Parameters: `path` (Path), `search` (str), `search_is_regex` (bool, optional), `before` (int, optional), `after` (int, optional)
- `file_create`: Create a new file with specified content.
  - Parameters: `path` (Path), `content` (str)
- `file_append`: Append content to an existing file.
  - Parameters: `path` (Path), `content` (str)

**Directory Operations:**

- `directory_list`: List the contents of one or more directories.
  - Parameters: `path` (list[Path]), `recurse` (bool, optional), `include` (list[str], optional), `exclude` (list[str], optional), `bypass_default_exclusions` (bool, optional)
- `directory_preview`: Preview the contents of files within one or more directories.
  - Parameters: `path` (list[Path]), `recurse` (bool, optional), `include` (list[str], optional), `exclude` (list[str], optional), `bypass_default_exclusions` (bool, optional)
- `directory_read`: Read the contents of files within one or more directories.
  - Parameters: `path` (list[Path]), `recurse` (bool, optional), `include` (list[str], optional), `exclude` (list[str], optional), `bypass_default_exclusions` (bool, optional)
- `directory_search`: Search the contents of files within one or more directories for a string or regex pattern.
  - Parameters: `path` (list[Path]), `search` (str), `recurse` (bool, optional), `include` (list[str], optional), `exclude` (list[str], optional), `before` (int, optional), `after` (int, optional), `search_is_regex` (bool, optional), `bypass_default_exclusions` (bool, optional)

## Development & Testing

- Tests are located in the `tests/` directory.
- Use `pytest` for running tests:

```bash
pytest
```

## License

See [LICENSE](LICENSE).