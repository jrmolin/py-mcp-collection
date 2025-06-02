import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from mcp.types import EmbeddedResource, ImageContent, TextContent

from mcp_utils.responses.redirect import (
    redirect_to_files,
    redirect_to_split_files,
    redirect_to_split_tool_calls,
    redirect_to_tool_call,
    write_contents_to_files,
)


@pytest.fixture
def mock_first_tool():
    return AsyncMock()


@pytest.fixture
def mock_second_tool():
    return AsyncMock()


@pytest.fixture
def temp_directory():
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.mark.asyncio
async def test_redirect_to_tool_call(mock_ctx, mock_first_tool, mock_second_tool):
    """Test redirect_to_tool_call redirects the result of the first tool to the second."""

    first_tool_result = [TextContent(text="result from first tool", type="text")]
    mock_first_tool.run.return_value = first_tool_result
    mock_second_tool.run.return_value = [TextContent(text="result from second tool", type="text")]

    mock_ctx.fastmcp.get_tools.return_value = {
        "first_tool": mock_first_tool,
        "second_tool": mock_second_tool,
    }

    second_tool_args = {"input_arg": "some_value"}
    second_tool_response_arg = "tool_output"

    result = await redirect_to_tool_call(
        mock_ctx,
        first_tool_name="first_tool",
        first_tool_arguments={"arg1": "value1"},
        second_tool_name="second_tool",
        second_tool_arguments=second_tool_args,
        second_tool_response_argument=second_tool_response_arg,
    )

    mock_first_tool.run.assert_awaited_once_with({"arg1": "value1"})
    expected_second_args = second_tool_args.copy()
    expected_second_args[second_tool_response_arg] = first_tool_result[0].text

    mock_second_tool.run.assert_awaited_once_with(expected_second_args)
    assert result == [TextContent(text="result from second tool", type="text")]


@pytest.mark.asyncio
async def test_redirect_to_split_tool_calls(mock_ctx, mock_first_tool, mock_second_tool):
    """Test redirect_to_split_tool_calls splits the result of the first tool and redirects to multiple second tool calls."""

    first_tool_result = [
        TextContent(text='[{"data": "item1"}, {"data": "item2"}]', type="text"),
        TextContent(text='[{"data": "item3"}, {"data": "item4"}]', type="text"),
        TextContent(text='[{"data": "item5"}, {"data": "item6"}]', type="text"),
    ]
    mock_first_tool.run.return_value = first_tool_result
    mock_second_tool.run.return_value = [TextContent(text="result from second tool", type="text")]

    mock_ctx.fastmcp.get_tools.return_value = {
        "first_tool": mock_first_tool,
        "second_tool": mock_second_tool,
    }

    second_tool_args = {"input_list": []}
    second_tool_response_arg = "input_list"

    with patch("mcp_utils.responses.redirect.write_content_to_file", new_callable=AsyncMock):
        result = await redirect_to_split_tool_calls(
            mock_ctx,
            first_tool_name="first_tool",
            first_tool_arguments={"arg1": "value1"},
            second_tool_name="second_tool",
            second_tool_arguments=second_tool_args,
            second_tool_response_argument=second_tool_response_arg,
            split_on_json_array_entries=True,
            entries_per_tool_call=1,
        )

    mock_first_tool.run.assert_awaited_once_with({"arg1": "value1"})
    assert mock_second_tool.run.call_count == 6
    mock_second_tool.run.assert_awaited_with({"input_list": [{"data": "item6"}]})  # Check the last call
    assert len(result) == 6  # Expecting 6 results from 3 calls


@pytest.mark.asyncio
async def test_write_contents_to_files(mock_ctx, temp_directory):
    """Test write_contents_to_files writes content to files."""
    contents: list[TextContent | ImageContent | EmbeddedResource] = [
        TextContent(text="content1", type="text"),
        TextContent(text="content2", type="text"),
    ]

    with patch("mcp_utils.responses.redirect.write_content_to_file", new_callable=AsyncMock) as mock_write_content_to_file:
        await write_contents_to_files(
            mock_ctx,
            contents=contents,
            directory=temp_directory,
            stem="output",
            extension="txt",
        )

        first_mock_call = mock_write_content_to_file.mock_calls[0]
        second_mock_call = mock_write_content_to_file.mock_calls[1]

        assert first_mock_call.args[0] == contents[0]
        assert first_mock_call.kwargs["path"] == temp_directory / "output-0.txt"

        assert second_mock_call.args[0] == contents[1]
        assert second_mock_call.kwargs["path"] == temp_directory / "output-1.txt"


@pytest.mark.asyncio
async def test_redirect_to_files(mock_ctx, mock_fastmcp, mock_first_tool, temp_directory):
    """Test redirect_to_files calls the tool and then write_contents_to_files."""
    tool_result = [TextContent(text="tool output", type="text")]
    mock_first_tool.run.return_value = tool_result
    mock_fastmcp.get_tools.return_value = {"test_tool": mock_first_tool}

    with patch("mcp_utils.responses.redirect.write_content_to_file", new_callable=AsyncMock) as mock_write_content_to_file:
        mock_write_content_to_file.return_value = temp_directory / "output-0.txt"

        result = await redirect_to_files(
            mock_ctx,
            tool_name="test_tool",
            arguments={"arg": "value"},
            directory=temp_directory,
            stem="output",
            extension="txt",
        )

    mock_first_tool.run.assert_awaited_once_with({"arg": "value"})
    mock_write_content_to_file.assert_awaited_once_with(tool_result[0], path=temp_directory / "output-0.txt")
    assert result == [temp_directory / "output-0.txt"]


@pytest.mark.asyncio
async def test_redirect_to_split_files(mock_ctx, mock_fastmcp, mock_first_tool, temp_directory):
    """Test redirect_to_split_files calls the tool and then write_contents_to_files with splitting."""
    tool_result = [TextContent(text="tool output that needs splitting", type="text")]
    mock_first_tool.run.return_value = tool_result
    mock_fastmcp.get_tools.return_value = {"test_tool": mock_first_tool}

    with patch("mcp_utils.responses.redirect.write_content_to_file", new_callable=AsyncMock) as mock_write_content_to_file:
        mock_write_content_to_file.return_value = temp_directory / "output-0.txt"

        result = await redirect_to_split_files(
            mock_ctx,
            tool_name="test_tool",
            arguments={"arg": "value"},
            directory=temp_directory,
            stem="output",
            extension="txt",
            split_text_size=10,
        )

    mock_first_tool.run.assert_awaited_once_with({"arg": "value"})

    write_content_calls = mock_write_content_to_file.mock_calls

    assert len(write_content_calls) == 4
    assert write_content_calls[0].args[0].text == "tool outpu"
    assert write_content_calls[0].kwargs["path"] == temp_directory / "output-0.txt"
    assert write_content_calls[1].args[0].text == "t that nee"
    assert write_content_calls[1].kwargs["path"] == temp_directory / "output-1.txt"

    assert write_content_calls[2].args[0].text == "ds splitti"
    assert write_content_calls[2].kwargs["path"] == temp_directory / "output-2.txt"
    assert write_content_calls[3].args[0].text == "ng"
    assert write_content_calls[3].kwargs["path"] == temp_directory / "output-3.txt"

    assert result == [
        temp_directory / "output-0.txt",
        temp_directory / "output-1.txt",
        temp_directory / "output-2.txt",
        temp_directory / "output-3.txt",
    ]
