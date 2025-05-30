import tempfile
from pathlib import Path

import pytest

from mcp_utils.main import cli

def test_main_imports():
    assert cli is not None
