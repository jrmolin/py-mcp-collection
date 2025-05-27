# mcp-oops

It's easy to run into "Oops"-es while using MCP Servers. It's great that I can query every issue in my GitHub repo but why did the LLM try to do it in one call?

What you need is an MCP Server that prevents these kinds of Oops-es. With MCPOops, "Oops"-es are no more.

## Two main commands

There are two main commands you can use to run MCP Oops:
- `stdio <cmd> <args>`
- `config <mcp-config.yml>`

## `stdio`

The `stdio` command is the simplest way to run MCP Oops. It takes the same arguments as the command you want to run, and then adds the MCP Oops server to the front of the command. It's great adding simple Oops protection to any existing MCP Server.

Currently provides:
- Response size protection (defaults to 400kb, use `--limit-response-size` to change)

For example, if you were using the fetch server as so:
```yaml
mcpServers:
  "fetch": {
    "command": "uvx",
    "args": ["mcp-server-fetch"]
  }
```

You would simply put `uvx` in the command, the first two args are always the MCP Oops server and the transport to use to connect to the mcp server.

```yaml
mcpServers:
  "fetch": {
    "command": "uvx",
    "args": [
        "https://github.com/strawgate/py-mcp-collection.git#subdirectory=mcp-oops",
        "stdio",
        // Your MCP Server command goes here
        "uvx", 
        "mcp-server-fetch"
    ]
}
```

## `config`

The `config` command is the most powerful way to run MCP Oops. It takes an extended MCP Server configuration file, which can include many MCP servers, and includes means to rewrite every part of a tool on the fly.

Currently provides:
1. Tool rewriting
   - Rename a tool
   - Change the description of a tool
   - Add default values to a tool
   - Add required values to a tool
2. Tool call wrapping
   - Pre-call hook runs before the tool call can read and modify the tool call arguments
   - Post-call hook runs after the tool call has returned and can read and modify tool call results
   - Clients can provide extra arguments to the tool call that you can leverage in your hooks. For example, redirecting large tool call responses to a file, vector db or an in-memory store for segmented retrieval.
3. Hide tools from the client


## Tool rewriting

One option for MCP Oops is to provide a yaml configuration file to the MCP Oops server. This file will contain the MCP Servers that you want to wrap with MCP Oops along with the parameters that you want to set for each tool call.

```yaml
mcpServers:
  "git":
    command: uvx
    args:
      - "git+https://github.com/modelcontextprotocol/servers.git#subdirectory=src/git"
    tools:
      "git_status":
        description: >-
          The `git_status` tool shows the working tree status, including changes
          staged for commit, unstaged changes, and untracked files. It provides
          a summary of the current state of your Git repository, helping you
          understand what changes are pending. Common Asks: - "What is the
          current status of my repository?" - "Show me what files have changed."
          Output: - A text summary of the repository's status, similar to `git
          status` command line output. Examples: - To check the status of the
          current repository: git_status(repo_path='./') - To check the status
          of a specific repository: git_status(repo_path='/path/to/my/repo')
        parameter_overrides:
          repo_path:
            description: Path to the Git repository.
```

You can then add the MCP Oops server to your MCP Server configuration file:

```json
"MCPOopsProxy": {
    "command": "uvx",
    "args": [
        "https://github.com/strawgate/py-mcp-collection.git#subdirectory=mcp-oops",
        "config",
        "/path/to/your/mcp-config.yml"
    ]
}
```

You can run as many underlying MCP Servers as you want, and MCP Oops will wrap them all.

```
mcpServers:
  fetch:
    command: "uvx"
    args: ["mcp-server-fetch"]
    description: "Access a webpage"
    tools:
      "fetch":
        description: "Access a webpage"
        parameter_overrides:
          url:
            description: "The URL to fetch"
            default: "https://www.fastmcp.com"

  "Filesystem Operations":
    command: "uvx"
    args: ["git+https://github.com/strawgate/py-mcp-collection.git#subdirectory=filesystem-operations-mcp"]
    description: "Access the local filesystem"
  tree-sitter:
    command: "uvx"
    args: ["--directory", ".", "mcp-server-tree-sitter"]
```
