# MCPOops

A MCPOops project for creating MCP Servers.

## Features

- **CLI**: A CLI for the MCP Server.
- **Extensible**: Easily add new reference types or integrate with other MCP tools.

## Installation

```bash
uv sync
```

Or, for development:

```bash
uv sync --group dev
```

## Usage

### Command-Line Interface

Run the MCP server with your references:

```bash
uv run MCPOops --cli-arg-1 "cli-arg-1" --cli-arg-2 "cli-arg-2" --cli-arg-3 "cli-arg-3"
```

## VS Code McpServer Usage

1. Open the command palette (Ctrl+Shift+P or Cmd+Shift+P).
2. Type "Settings" and select "Preferences: Open User Settings (JSON)".
3. Add the following MCP Server configuration

```json
{
    "mcp": {
        "servers": {
            "Mcpoops": {
                "command": "uvx",
                "args": [
                    "https://github.com/strawgate/py-mcp-collection.git#subdirectory=MCPOops",
                    "--cli-arg-1",
                    "cli-arg-1",
                    "--cli-arg-2",
                    "cli-arg-2",
                    "--cli-arg-3",
                    "cli-arg-3"
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
        "https://github.com/strawgate/py-mcp-collection.git#subdirectory=MCPOops"
      ]
    }
```

## Development & Testing

- Tests should be placed alongside the source code or in a dedicated `tests/` directory.
- Use `pytest` for running tests.

```bash
pytest
```

## License

See [LICENSE](LICENSE).