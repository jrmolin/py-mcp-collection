# local-references-mcp

A local reference management and preview tool, built on [FastMCP](https://github.com/jlowin/fastmcp), for serving and interacting with local reference files (such as documentation, best practices, or knowledge snippets) via an MCP Server.

Useful to allow a coding assistant to preview local documentation, best practices, or knowledge snippets.

## The Story

Imagine you're in the Beats repo and you tell it that there's a "Winlogbeat" reference at https://github.com/elastic/beats/tree/main/docs/reference/winlogbeat. For this, you'd pass `--reference "Winlogbeat:docs/reference/winlogbeat"`. From there, the LLM has a couple of tools available to it.

### List References 

When the LLM calls List References, something like this is returned:

``` 
  # Local References 
  Below is a list of available reference types. We will show each type, and a preview of its entries.Note: previews are truncated to 1000 characters.
  
  ## References for: `Winlogbeat`
  Below are the available references that you can leverage when working with Winlogbeat
  
  ### Type: `Winlogbeat`, Name: `Add cloud metadata`
  The add_cloud_metadata processor enriches each event with instance metadata from the machine’s hosting provider. At startup it will query a list of hosting providers and cache the instance metadata.

  ### Type: `Winlogbeat`, Name: `Add Cloud Foundry metadata`
  The add_cloudfoundry_metadata processor annotates each event with relevant metadata from Cloud Foundry applications. The events are annotated with Cloud Foundry metadata, only if the event contains a reference to a Cloud Foundry application (using field cloudfoundry.app.id) and the configured Cloud Foundry client is able to retrieve information for the application.
  ....
```

and if the LLM wants the full reference can call, `get_reference("Winlogbeat", "Add Cloud Metadata")`

You can have the LLM run list_references automatically on start-up and then it knows how and where to get best practices, how tos, etc from the docs in your repo.

This is especially useful when you want to expose guides / instructions to an LLM without giving it general read/write access to the filesystem.

## VS Code McpServer Usage

1. Open the command palette (Ctrl+Shift+P or Cmd+Shift+P).
2. Type "Settings" and select "Preferences: Open User Settings (JSON)".
3. Add the following MCP Server configuration

```json
{
    "mcp": {
        "servers": {
            "Local References": {
                "command": "uvx",
                "args": [
                    "git+https://github.com/strawgate/py-mcp-collection.git#subdirectory=local-references-mcp",
                    "--reference",
                    "Best Practices:/docs/best_practices.md",
                    "--reference",
                    "How To:/docs/how_to.md"
                ]
            }
        }
    }
}
```

## Roo Code / Cline McpServer Usage
Simply add the following to your McpServer configuration. Edit the AlwaysAllow list to include the tools you want to use without confirmation.

```
    "Local References": {
      "command": "uvx",
      "args": [
        "git+https://github.com/strawgate/py-mcp-collection.git#subdirectory=local-references-mcp"
      ]
    }
```
## Development

```bash
uv sync --group dev
```

## Usage

### Command-Line Interface

Run the MCP server with your references:

```bash
python -m local_references_mcp.main --reference "Type1:/path/to/file1.md" --reference "Type2:/path/to/file2.md"
```

- Each `--reference` argument should be in the format `name:path`.
- You can specify multiple references.

### Example

```bash
python -m local_references_mcp.main --reference "Best Practices:/docs/best_practices.md" --reference "How To:/docs/how_to.md"
```

## How It Works

- **Reference**: Represents a single reference file, identified by a name and a path.
- **ReferenceEntry**: Represents an entry within a reference (currently, each reference is a single file).
- **ReferenceManager**: Manages a collection of references, provides preview and retrieval tools, and integrates with FastMCP.



## Extending

To add new reference types or customize entry parsing, extend the `Reference` and `ReferenceEntry` classes in `references.py`.

## Development & Testing

- Tests should be placed alongside the source code or in a dedicated `tests/` directory.
- Use `pytest` for running tests.

```bash
pytest
```

## License

See [LICENSE](LICENSE).
