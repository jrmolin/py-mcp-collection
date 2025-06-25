# Knowledge Base MCP

An MCP Server for creating knowledge bases and searching them!

## Features

- **Multiple Vector Store Backends**: Works with DuckDB and Elasticsearch.
- **Website Ingestion**: Load and crawl documentation or websites into a knowledge base.
- **Semantic Search**: Query across one or more knowledge bases using embeddings and reranking.
- **Knowledge Base Management**: List, remove, or clear knowledge bases. 

## Usage

### Command-Line Interface

The CLI supports both DuckDB (in-memory or persistent) and Elasticsearch as vector store backends. 

#### DuckDB (Persistent)

```bash
uv run knowledge_base_mcp duckdb persistent --db-dir ./storage --db-name knowledge_base.duckdb run
```

#### DuckDB (In-Memory)

```bash
uv run knowledge_base_mcp duckdb memory run
```

#### Elasticsearch

```bash
uv run knowledge_base_mcp elasticsearch --es-url http://localhost:9200 --es-index-name kbmcp run
```

You can also set Elasticsearch options via environment variables:
- `ES_URL`
- `ES_INDEX_NAME`
- `ES_USERNAME`
- `ES_PASSWORD`
- `ES_API_KEY`

### Main Server Tools/Endpoints

When running, the MCP server exposes the following tools:

- **load_website**: Ingest a website or documentation into a named knowledge base.
- **query**: Query all knowledge bases with a question.
- **query_knowledge_bases**: Query specific knowledge bases with a question.
- **get_knowledge_bases**: List all knowledge bases and their document counts.
- **remove_knowledge_base**: Remove a specific knowledge base.
- **remove_all_knowledge_bases**: Remove all knowledge bases from the vector store.


## VS Code McpServer Usage

1. Open the command palette (Ctrl+Shift+P or Cmd+Shift+P).
2. Type "Settings" and select "Preferences: Open User Settings (JSON)".
3. Add the following MCP Server configuration:

```json
{
    "mcp": {
        "servers": {
            "Knowledge Base Mcp": {
                "command": "uvx",
                "args": [
                    "https://github.com/strawgate/py-mcp-collection.git#subdirectory=knowledge_base_mcp",
                    "duckdb",
                    "persistent",
                    "run"
                ]
            }
        }
    }
}
```

## License

See [LICENSE](LICENSE).