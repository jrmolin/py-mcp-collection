# mcp-oops

It's easy to run into "Oops"-es while using MCP Servers. It's great that I can query every issue in my GitHub repo but why did the LLM try to do it in one call?

What you need is an MCP Server that prevents these kinds of Oops-es. With MCPOops, "Oops"-es are no more.

The mcp-oops server gives any existing uvx (npx coming soon), sse, or streamable MCP Server an "Oops"-proof wrapper by:
- Limiting the size of responses from tool calls
- Allowing you to redirect any tool call to a file on disk
- Splitting large tool calls into multiple files that can be consumed in a fan-out fan-in workflow

(Coming Soon): Another major feature is the ability to set default parameters for tool calls, restricting tools to being called with only the parameters you want them to have. Give your Assistant the ability to post a comment only on the PR that is being reviewed, not any PR in the repo! That's a great way to prevent "Oops"-es.

## Features

- **Block Large Tool Calls**: Prevents tool calls from returning responses that are too large. Enabling the LLM to call tools that return large responses is a great way to get "Oops"-es.
- **Large Response Handling**: Intercepts tool call responses and redirects large ones to specified files, optionally splitting them into chunks.
- **Default Parameters**: Set default parameters for tool calls, restricting tools to being called with only the parameters you want them to have. (Coming Soon)

## Usage

### VS Code McpServer Usage

```json
{
    "mcp": {
        "servers": {
            "MCPOopsProxy": {
                "command": "uvx",
                "args": [
                    "https://github.com/strawgate/py-mcp-collection.git#subdirectory=mcp-oops",
                    "--mcp-config",
                    "/path/to/your/mcp-config.yml",
                    "--max-response-size",
                    "200", // 200KB
                    "--max-redirected-response-size",
                    "10000", // 10MB
                    "--split-redirected-responses",
                    "1000",
                    "--mcp-transport",
                    "stdio"
                ]
            }
        }
    }
}
```

### Roo Code / Cline McpServer Usage

Simply add the following to your McpServer configuration, adjusting the arguments as needed. Edit the AlwaysAllow list to include the tools you want to use without confirmation.

```
    "MCPOopsProxy": {
      "command": "uvx",
      "args": [
        "https://github.com/strawgate/py-mcp-collection.git#subdirectory=mcp-oops",
        "--mcp-config",
        "/path/to/your/mcp-config.yml",
        "--max-response-size",
        "200", // 200KB
        "--max-redirected-response-size",
        "10000", // 10MB
        "--split-redirected-responses",
        "1000", // 1MB
        "--mcp-transport",
        "stdio"
      ]
    }
```