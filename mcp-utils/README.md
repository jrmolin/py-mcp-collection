# MCP Utilities

Provides helper functions for Python MCP and FastMCP Servers.

Helper functions include:

## MCP Helpers

| Function | Description |
|----------|-------------|
| `read_content` | Read the data out of an MCP Content object. |
| `size_content` | Get the size of the data in an MCP Content object. |
| `preview_content` | Preview the data in an MCP Content object. |
| `split_text_content` | Split a text content into a list of text contents, each of which is less than or equal to the split size. |
| `limit_tool_response` | Limit the response of a tool call to a given number of bytes. |
| `truncate_tool_response` | Truncate the response of a tool call to a given number of bytes. |

## FastMCP Helpers

| Function | Description |
|----------|-------------|
| `redirect_to_tool_call` | Redirect the response of a FastMCP tool call to a new tool call. |
| `redirect_to_split_tool_calls` | Redirect the response of a FastMCP tool call to multiple tool calls. |
| `redirect_to_files` | Redirect the response of a FastMCP tool call to a list of files. |
| `redirect_to_split_files` | Redirect the response of a FastMCP tool call to a list of files, split into multiple tool calls. |