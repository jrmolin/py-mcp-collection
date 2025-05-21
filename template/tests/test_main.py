import tempfile
from pathlib import Path

import pytest

from template.main import cli

def test_main_imports():
    assert cli is not None
