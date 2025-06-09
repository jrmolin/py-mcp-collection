# strawgate_es_mcp

Strawgate's Unofficial MCP Server for Elasticsearch.

Use at your own risk. This is not an official Elasticsearch product. This MCP Server will probably break your Elasticsearch cluster. Do not use it.

This project provides a Model Context Protocol (MCP) server implemented in Python using `fastmcp`. Its primary purpose is to expose a wide range of Elasticsearch client functionalities as callable MCP tools, allowing for interaction with an Elasticsearch cluster via the MCP.

## Features

- **Elasticsearch Tooling**: Exposes numerous Elasticsearch client APIs as MCP tools, including:
    - CAT APIs (allocation, aliases, count, indices, nodes, shards, etc.)
    - Cluster APIs (health, state, stats)
    - Nodes APIs (info, stats)
    - Indices APIs (create/get data stream, stats, resolve index)
    - ILM and SLM APIs (get/explain lifecycle, get status, get stats)
    - Shutdown APIs (get node)
    - Search API
- **CLI**: A CLI for the MCP Server.
- **Extensible**: Easily add new Elasticsearch client methods as MCP tools or integrate with other MCP tools.
- **Sample Script**: Includes `sample_multisearch.py` to demonstrate using the Elasticsearch Python client for multi-searches.
- **Testing**: Includes unit tests for the exposed tools and sample scripts using `pytest`.

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