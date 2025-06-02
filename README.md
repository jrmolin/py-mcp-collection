This repository contains a collection of MCP servers that are useful for AI Coding Assistants.

Currently there are three MCP Servers ready to be used:
- 🎤 MCP Oops 🎤
- Filesystem Operations
- Local References

| MCP Server | Why it's neat | Status |
|------------|-------------|--------|
| [💾 Filesystem Operations](./filesystem-operations-mcp/README.md) | Performs bulk file read, preview and search operations and provides code and text summarization options to help find relevant files. | ✅ |
| [📚 Local References](./local-references-mcp/README.md) | Allows exposing existing documentation in the project as "Best Practices" or "How To" guides / etc to the AI Coding Assistant. | ✅ |
| [🔍 Doc Store Vector Search](./doc-store-vector-search-mcp/README.md) | Allows storing and searching documents in a vector store. | 🚧 |
| [🎤 MCP Oops](./mcp-oops/README.md) | Allows modifying the behavior of someone else's MCP Server. | 🚧 |

| MCP Libraries | Why it's neat | Status |
|------------|-------------|--------|
| [🔧 MCP Utils](./mcp-utils/README.md) | Provides utilities for MCP Servers. | Provides utilities for MCP Servers!! | 🚧 |

## MCP Oops
This MCP Oops is a wrapper server that allows you to significantly modify the behavior of an MCP Server. It can be used to limit response sizes, host multiple MCP Servers on a single port, change tool names, descriptions, call pre/post hooks, and more.

To get the started with MCP Oops, see the [MCP Oops README](./mcp-oops/README.md).

## Filesystem Operations
This MCP Server provides tools for performing bulk file and folder operations. It includes centralized exception handling for filesystem operations.

To get the started with Filesystem Operations, see the [Filesystem Operations README](./filesystem-operations-mcp/README.md).

## Local References
This MCP Server provides a way to reference local files and folders in the codebase. This allows you to expose existing documentation in the project as "Best Practices" or "How To" guides / etc to the AI Coding Assistant.

To get the started with Local References, see the [Local References README](./local-references-mcp/README.md).

There are additional MCP servers under development:
- Doc Store Vector Search