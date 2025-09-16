# GitHub Research MCP

A comprehensive Model Context Protocol (MCP) server for researching GitHub repositories, issues, and pull requests with AI-powered analysis and summarization capabilities.

## Features

### Repository Analysis
- **File Discovery**: Browse repository structure and find files by patterns
- **Code Search**: Search for code across repositories with advanced filtering
- **File Analysis**: Get file contents, README files, and file extension statistics
- **Repository Summarization**: AI-powered analysis of entire repositories

### Issue & Pull Request Research
- **Detailed Research**: Get comprehensive information about specific issues and pull requests
- **Advanced Search**: Search issues/PRs by keywords, labels, authors, and more
- **Timeline Analysis**: Track related issues, PRs, and cross-references
- **Comment Analysis**: Review all comments and discussion threads

### AI-Powered Analysis
- **Intelligent Summarization**: Generate focused summaries using OpenAI models
- **Context-Aware Research**: AI-driven analysis of complex GitHub data
- **Flexible Prompting**: Customizable prompts for different analysis needs
- **Structured Data Extraction**: Convert unstructured GitHub data into structured formats

### Technical Features
- **GraphQL Integration**: Efficient data fetching using GitHub's GraphQL API
- **REST API Support**: Fallback to REST API for broader compatibility
- **Rate Limiting**: Built-in rate limiting and request management
- **Flexible Configuration**: Support for both stdio and HTTP transports
- **Public Repository Support**: Specialized tools for public repository analysis

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

**Required:**
- `GITHUB_TOKEN` or `GITHUB_PERSONAL_ACCESS_TOKEN`: Required for GitHub API access

**AI Features (Optional):**
- `OPENAI_API_KEY`: Required for AI summarization features (optional if sampling is disabled)
- `OPENAI_MODEL`: OpenAI model to use for summarization (e.g., "gpt-4", "gpt-3.5-turbo")
- `OPENAI_BASE_URL`: Custom OpenAI API base URL (optional)
- `DISABLE_SAMPLING`: Set to "true" to disable AI summarization features

**Public Repository Features:**
- `MINIMUM_STARS`: Minimum star count for repository summarization (default: 10)
- `OWNER_ALLOWLIST`: Comma-separated list of owners to allow regardless of star count

## Usage

### Command-Line Interface

Run the MCP server:

```bash
# Main server with full functionality (requires OpenAI configuration)
uv run github-research-mcp

# Without AI summarization
DISABLE_SAMPLING=true uv run github-research-mcp

# Public repository server (specialized for public repos)
uv run python -m github_research_mcp.public

# With HTTP transport
uv run github-research-mcp --mcp-transport streamable-http
```

### Available Tools

The server provides multiple tool categories:

**Repository Tools** (always available):
- `get_files`: Browse repository file structure
- `find_files`: Search for files by patterns
- `search_files`: Advanced file search with filtering
- `get_readmes`: Retrieve README files
- `count_file_extensions`: Analyze file type distribution

**Issue & Pull Request Tools** (always available):
- `get_issue_or_pull_request`: Get detailed information about specific issues/PRs
- `search_issues_or_pull_requests`: Search issues/PRs with advanced filtering

**AI-Powered Tools** (requires OpenAI configuration):
- `summarize`: Generate AI-powered repository summaries
- `research_issue_or_pull_request`: AI-driven analysis of issues/PRs

**Public Repository Tools** (public server only):
- `summarize`: Generate summaries for public repositories with star/owner filtering

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

Once configured, you can use the tools for comprehensive GitHub research:

**Repository Analysis:**
- **Browse files**: Explore repository structure and find specific files
- **Code search**: Search for functions, classes, or patterns across the codebase
- **File analysis**: Get file contents and analyze file type distribution
- **Repository summaries**: Get AI-powered analysis of entire repositories

**Issue & Pull Request Research:**
- **Research specific items**: Get detailed information about issue #123 or PR #456
- **Advanced search**: Find issues/PRs by keywords, labels, authors, or states
- **Timeline analysis**: Track related issues, PRs, and cross-references
- **AI analysis**: Get intelligent summaries and insights about issues/PRs

**Public Repository Research:**
- **Public repo summaries**: Analyze public repositories with star count filtering
- **Owner allowlisting**: Bypass star requirements for specific organizations

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
├── main.py                    # Main MCP server entry point
├── public.py                  # Public repository server entry point
├── clients/
│   └── github.py              # GitHub API client with token management
├── models/
│   ├── graphql/
│   │   ├── fragments.py       # GraphQL fragments for issues, PRs, comments
│   │   └── queries.py         # GraphQL query definitions
│   ├── query/
│   │   ├── base.py            # Base query qualifiers and operators
│   │   ├── code.py            # Code search query builders
│   │   └── issue_or_pull_request.py  # Issue/PR search query builders
│   ├── repository/
│   │   └── tree.py            # Repository tree and file analysis models
│   └── rest/
│       └── models.py          # REST API response models
├── sampling/
│   ├── extract.py             # Structured data extraction utilities
│   └── prompts.py             # AI prompt building and management
└── servers/
    ├── base.py                # Base server with common functionality
    ├── public.py              # Public repository server
    ├── repository.py          # Repository analysis server
    ├── issues_or_pull_requests.py  # Issue/PR research server
    └── shared/
        ├── annotations.py     # Type annotations and field definitions
        └── utility.py         # Shared utility functions
```

### Key Dependencies

- **fastmcp**: MCP server framework with sampling support
- **githubkit**: GitHub API client with GraphQL and REST support
- **openai**: AI model integration for summarization
- **pydantic**: Data validation and serialization
- **asyncclick**: CLI framework for command-line interface
- **async-lru**: LRU caching for performance optimization
- **yaml**: YAML processing for prompt configuration

## Architecture

### Server Types

The project provides two distinct MCP servers:

1. **Main Server** (`main.py`): Full-featured server with repository analysis, issue/PR research, and AI summarization
2. **Public Server** (`public.py`): Specialized server for public repositories with star count filtering and rate limiting

### Key Components

**Query System**: Sophisticated query builder supporting:
- Multiple qualifier types (keywords, labels, authors, states, etc.)
- Boolean operators (AND/OR) for complex queries
- Advanced filtering for both code and issue/PR searches

**AI Integration**: 
- Structured data extraction from AI responses
- Flexible prompt building system
- Support for multiple AI models and configurations

**Data Models**:
- Comprehensive GraphQL fragments for GitHub data
- Pydantic models for type safety and validation
- Repository tree analysis and file type statistics

**Caching & Performance**:
- LRU caching for frequently accessed data
- Token estimation for AI model optimization
- Efficient GraphQL query construction

## License

See [LICENSE](LICENSE).