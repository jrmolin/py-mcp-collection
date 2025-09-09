# GitHub Research MCP

A Model Context Protocol (MCP) server for researching GitHub issues with AI-powered summarization capabilities.

## Features

- **Issue Research**: Get detailed information about specific GitHub issues including comments and related items
- **Keyword Search**: Search issues by keywords with advanced filtering options (state, labels, sorting)
- **AI Summarization**: Generate focused summaries of issues and search results using OpenAI models
- **GraphQL Integration**: Efficient data fetching using GitHub's GraphQL API
- **Flexible Configuration**: Support for both stdio and HTTP transports
- **Optional Sampling**: Can run with or without AI summarization capabilities

## Installation

```bash
uv sync
```

Or, for development:

```bash
uv sync --group dev
```

## Configuration

### Environment Variables

- `GITHUB_TOKEN` or `GITHUB_PERSONAL_ACCESS_TOKEN`: Required for GitHub API access
- `OPENAI_API_KEY`: Required for AI summarization features (optional if sampling is disabled)
- `OPENAI_MODEL`: OpenAI model to use for summarization (e.g., "gpt-4", "gpt-3.5-turbo")
- `OPENAI_BASE_URL`: Custom OpenAI API base URL (optional)
- `DISABLE_SAMPLING`: Set to "true" to disable AI summarization features

## Usage

### Command-Line Interface

Run the MCP server:

```bash
# With AI summarization (requires OpenAI configuration)
uv run github-research-mcp

# Without AI summarization
DISABLE_SAMPLING=true uv run github-research-mcp

# With HTTP transport
uv run github-research-mcp --mcp-transport streamable-http
```

### Available Tools

The server provides 4 tools:

**Research Tools** (always available):
- `research_issue`: Get detailed information about a specific issue
- `research_issues_by_keywords`: Search issues by keywords with filtering

**Summary Tools** (requires OpenAI configuration):
- `summarize_issue`: Generate AI-powered summary of a specific issue
- `summarize_issues_by_keywords`: Generate AI-powered summary of search results

## MCP Client Configuration

### VS Code

1. Open the command palette (Ctrl+Shift+P or Cmd+Shift+P).
2. Type "Settings" and select "Preferences: Open User Settings (JSON)".
3. Add the following MCP Server configuration:

```json
{
    "mcp": {
        "servers": {
            "GitHub Research MCP": {
                "command": "uvx",
                "args": [
                    "https://github.com/strawgate/py-mcp-collection.git#subdirectory=github_research_mcp"
                ],
                "env": {
                    "GITHUB_TOKEN": "your_github_token_here",
                    "OPENAI_API_KEY": "your_openai_api_key_here",
                    "OPENAI_MODEL": "gpt-4"
                }
            }
        }
    }
}
```

### Cline / Roo Code

Add the following to your MCP Server configuration:

```json
{
    "GitHub Research MCP": {
        "command": "uvx",
        "args": [
            "https://github.com/strawgate/py-mcp-collection.git#subdirectory=github_research_mcp"
        ],
        "env": {
            "GITHUB_TOKEN": "your_github_token_here",
            "OPENAI_API_KEY": "your_openai_api_key_here",
            "OPENAI_MODEL": "gpt-4"
        }
    }
}
```

### Example Usage

Once configured, you can use the tools to research GitHub issues:

- **Research a specific issue**: Get detailed information about issue #123 in a repository
- **Search issues by keywords**: Find all issues related to "bug" or "feature request"
- **Generate summaries**: Get AI-powered summaries focused on specific aspects of issues

## Development & Testing

### Running Tests

```bash
# Install development dependencies
uv sync --group dev

# Run tests
pytest

# Run with coverage
pytest --cov=github_research_mcp
```

### Project Structure

```
src/github_research_mcp/
├── main.py              # MCP server entry point
├── servers/
│   └── issues.py        # GitHub issue research functionality
├── clients/
│   └── github.py        # GitHub API client
├── models/
│   ├── graphql/         # GraphQL queries and fragments
│   └── query/           # Search query builders
└── sampling/            # AI sampling utilities
```

### Key Dependencies

- **fastmcp**: MCP server framework
- **githubkit**: GitHub API client
- **openai**: AI model integration
- **pydantic**: Data validation and serialization
- **asyncclick**: CLI framework

## License

See [LICENSE](LICENSE).