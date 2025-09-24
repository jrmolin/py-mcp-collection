from pathlib import Path

import pytest
from dotenv import load_dotenv

env_file = Path(".env")


@pytest.fixture(autouse=True)
def load_env_file():
    load_dotenv(env_file)
