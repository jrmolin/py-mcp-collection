from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class CachedToolResult(BaseModel):
    """Serializable wrapper for tool call results for caching."""

    tool_name: str
    arguments: Any | None
    value: Any
