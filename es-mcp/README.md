# es_mcp

A es_mcp project for creating MCP Servers.

## Features

- **CLI**: A CLI for the MCP Server.
- **Extensible**: Easily add new reference types or integrate with other MCP tools.

## Setup in Windsurf

On the right in the cascade window press the hammer icon and add a server with the following configuration:

```json
{
    "mcpServers": {
        "es-mcp": {
            "command": "uvx",
            "args": [
                "--from",
                "git+https://github.com/strawgate/py-mcp-collection.git#subdirectory=es-mcp",
                "es-mcp"
            ],
            "env": {
                "ES_HOST": "https://my-cloud-cluster:443",
                "ES_API_KEY": "MYCOOLAPIKEY"
            }
        }
    }
}
```

## VS Code McpServer Usage

1. Open the command palette (Ctrl+Shift+P or Cmd+Shift+P).
2. Type "Settings" and select "Preferences: Open User Settings (JSON)".
3. Add the following MCP Server configuration

```json
{
    "mcp": {
        "servers": {
            "Es Mcp": {
                "command": "uvx",
                "args": [
                    "--from",
                    "git+https://github.com/strawgate/py-mcp-collection.git#subdirectory=es_mcp",
                    "es-mcp"
                ]
            }
        }
    }
}
```

## Roo Code / Cline McpServer Usage
Simply add the following to your McpServer configuration. Edit the AlwaysAllow list to include the tools you want to use without confirmation.

```
    "es-mcp": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/strawgate/py-mcp-collection.git#subdirectory=es_mcp",
        "es-mcp"
      ]
    }
```


## License

See [LICENSE](LICENSE).