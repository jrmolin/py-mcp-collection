# Collection of MCP Servers

This repository contains a collection of MCP servers that are useful for AI Coding Assistants.

Currently there are two MCP Servers ready to be used:
- Filesystem Operations
- Local References

## Filesystem Operations
This MCP Server provides tools for performing bulk file and folder operations. It includes centralized exception handling for filesystem operations.

## Local References
This MCP Server provides a way to reference local files and folders in the codebase. This allows you to expose existing documentation in the project as "Best Practices" or "How To" guides / etc to the AI Coding Assistant.

There are additional MCP servers under development:
- Doc Store Vector Search


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
            },
            "Local References": {
                "command": "uvx",
                "args": [
                    "git+https://github.com/strawgate/py-mcp-collection.git#subdirectory=local-references-mcp",
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
    "Local References": {
      "command": "uvx",
      "args": [
        "git+https://github.com/strawgate/py-mcp-collection.git#subdirectory=local-references-mcp"
      ],
    },
```