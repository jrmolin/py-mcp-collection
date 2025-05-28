import tempfile
from pathlib import Path

import pytest

from es_mcp.main import cli

def test_main_imports():
    assert cli is not None
