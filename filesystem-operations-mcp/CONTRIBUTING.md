# Pull Requests

❌ Pull requests are not accepted
✅ Issue + Discussion + Pull Request is more than welcome!

# Development & Testing

- Tests are located in the `tests/` directory
- Tests use real filesystem operations with temporary directories
- Comprehensive test coverage for all major functionality including:
  - File operations (create, read, update, delete)
  - Directory operations
  - File patching and line-level modifications
  - Binary file handling
  - Error scenarios and edge cases
- Use `pytest` for running tests:

# Development

To set up the project, use `uv sync`:

```bash
uv sync
```

For development, including testing dependencies:

```bash
uv sync --group dev
```

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_file_operations.py
```

# Project Structure

```
filesystem-operations-mcp/
├── src/filesystem_operations_mcp/
│   ├── filesystem/
│   │   ├── detection/          # File type detection using Magika
│   │   ├── patches/            # File modification patches
│   │   ├── summarize/          # Code and text summarization
│   │   └── utils/              # Utility functions
│   ├── main.py                 # MCP server entry point
│   └── logging.py              # Logging configuration
├── tests/                      # Comprehensive test suite
├── pyproject.toml             # Project configuration
└── README.md                  # This file
```