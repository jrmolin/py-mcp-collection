from unittest.mock import AsyncMock

import pytest
from fastmcp.exceptions import ToolError
from mcp.types import ImageContent, TextContent
from mcp_utils.fastmcp.responses.limit import limit_tool_response, truncate_tool_response


@pytest.fixture
def mock_tool():
    return AsyncMock()


@pytest.mark.asyncio
async def test_limit_tool_response_within_limit(mock_ctx, mock_tool):
    """Test limit_tool_response when the tool result is within the limit."""
    mock_tool.run.return_value = [TextContent(text="short", type="text")]
    mock_ctx.fastmcp.get_tools.return_value = {"test_tool": mock_tool}

    result = await limit_tool_response(
        mock_ctx,
        tool_name="test_tool",
        tool_arguments={},
        limit=10,
    )
    assert len(result) == 1
    assert isinstance(result[0], TextContent)
    assert result[0].text == "short"
    mock_tool.run.assert_awaited_once_with({})


@pytest.mark.asyncio
async def test_limit_tool_response_exceeding_limit(mock_ctx, mock_tool):
    """Test limit_tool_response when the tool result exceeds the limit."""
    mock_tool.run.return_value = [TextContent(text="this is a long string", type="text")]
    mock_ctx.fastmcp.get_tools.return_value = {"test_tool": mock_tool}

    with pytest.raises(ToolError, match="Tool result was exceeded limit of 10 bytes: 21"):
        await limit_tool_response(
            mock_ctx,
            tool_name="test_tool",
            tool_arguments={},
            limit=10,
        )
    mock_tool.run.assert_awaited_once_with({})


@pytest.mark.asyncio
async def test_truncate_tool_response_within_limit(mock_ctx, mock_tool):
    """Test truncate_tool_response when the tool result is within the limit."""
    mock_tool.run.return_value = [TextContent(text="short", type="text")]
    mock_ctx.fastmcp.get_tools.return_value = {"test_tool": mock_tool}

    result = await truncate_tool_response(
        mock_ctx,
        tool_name="test_tool",
        tool_arguments={},
        limit=10,
    )
    assert len(result) == 1
    assert isinstance(result[0], TextContent)
    assert result[0].text == "short"
    mock_tool.run.assert_awaited_once_with({})


@pytest.mark.asyncio
async def test_truncate_tool_response_exceeding_limit_text(mock_ctx, mock_tool):
    """Test truncate_tool_response when the tool result exceeds the limit and is text."""
    mock_tool.run.return_value = [TextContent(text="this is a long string", type="text")]
    mock_ctx.fastmcp.get_tools.return_value = {"test_tool": mock_tool}

    result = await truncate_tool_response(
        mock_ctx,
        tool_name="test_tool",
        tool_arguments={},
        limit=10,
    )
    assert len(result) == 1
    assert isinstance(result[0], TextContent)
    assert result[0].text == "this is a "
    mock_tool.run.assert_awaited_once_with({})


@pytest.mark.asyncio
async def test_truncate_tool_response_exceeding_limit_non_text(mock_ctx, mock_tool):
    """Test truncate_tool_response when the tool result exceeds the limit and is non-text."""
    mock_tool.run.return_value = [ImageContent(data="image data", mimeType="image/png", type="image")]
    mock_ctx.fastmcp.get_tools.return_value = {"test_tool": mock_tool}

    with pytest.raises(
        ToolError, match="Truncate tool will only truncate text contents. The request size exceeds the limit and truncation is not allowed."
    ):
        await truncate_tool_response(
            mock_ctx,
            tool_name="test_tool",
            tool_arguments={},
            limit=5,
        )
    mock_tool.run.assert_awaited_once_with({})
