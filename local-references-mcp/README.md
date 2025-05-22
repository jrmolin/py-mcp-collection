# local-references-mcp

A local reference management and preview tool, built on [FastMCP](https://github.com/jlowin/fastmcp), for serving and interacting with local reference files (such as documentation, best practices, or knowledge snippets) via an MCP Server.

Useful to allow a coding assistant to preview local documentation, best practices, or knowledge snippets.

## Features

- **Reference Management**: Register and manage references from local files.
- **Preview References**: Quickly preview the contents of registered references.
- **Retrieve Reference Content**: Fetch the full content of a specific reference by type and name.
- **Extensible**: Easily add new reference types or integrate with other MCP tools.

## VS Code McpServer Usage

1. Open the command palette (Ctrl+Shift+P or Cmd+Shift+P).
2. Type "Settings" and select "Preferences: Open User Settings (JSON)".
3. Add the following MCP Server configuration

```json
{
    "mcp": {
        "servers": {
            "Local References": {
                "command": "uvx",
                "args": [
                    "https://github.com/strawgate/py-mcp-collection.git#subdirectory=local-references-mcp",
                    "--reference",
                    "Best Practices:/docs/best_practices.md",
                    "--reference",
                    "How To:/docs/how_to.md"
                ]
            }
        }
    }
}
```

## Roo Code / Cline McpServer Usage
Simply add the following to your McpServer configuration. Edit the AlwaysAllow list to include the tools you want to use without confirmation.

```
    "Local References": {
      "command": "uvx",
      "args": [
        "https://github.com/strawgate/local-references-mcp.git"
      ]
    }
```
## Development

```bash
uv sync --group dev
```

## Usage

### Command-Line Interface

Run the MCP server with your references:

```bash
python -m local_references_mcp.main --reference "Type1:/path/to/file1.md" --reference "Type2:/path/to/file2.md"
```

- Each `--reference` argument should be in the format `name:path`.
- You can specify multiple references.

### Example

```bash
python -m local_references_mcp.main --reference "Best Practices:/docs/best_practices.md" --reference "How To:/docs/how_to.md"
```

## How It Works

- **Reference**: Represents a single reference file, identified by a name and a path.
- **ReferenceEntry**: Represents an entry within a reference (currently, each reference is a single file).
- **ReferenceManager**: Manages a collection of references, provides preview and retrieval tools, and integrates with FastMCP.



## Extending

To add new reference types or customize entry parsing, extend the `Reference` and `ReferenceEntry` classes in `references.py`.

## Development & Testing

- Tests should be placed alongside the source code or in a dedicated `tests/` directory.
- Use `pytest` for running tests.

```bash
pytest
```

## License

See [LICENSE](LICENSE).