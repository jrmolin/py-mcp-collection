from unittest.mock import AsyncMock, MagicMock

import pytest
from fastmcp import FastMCP


@pytest.fixture
def mock_fastmcp():
    mock_fastmcp = AsyncMock(wraps=FastMCP)
    mock_fastmcp.get_tools = AsyncMock()
    return mock_fastmcp


@pytest.fixture
def mock_ctx(mock_fastmcp):
    mock_ctx = MagicMock()
    mock_ctx.fastmcp = mock_fastmcp
    return mock_ctx
