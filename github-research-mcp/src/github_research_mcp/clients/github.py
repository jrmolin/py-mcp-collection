import os
from typing import Any

from githubkit import GitHub
from githubkit.auth.token import TokenAuthStrategy


def get_github_token() -> str:
    env_vars: set[str] = {"GITHUB_TOKEN", "GITHUB_PERSONAL_ACCESS_TOKEN"}
    for env_var in env_vars:
        if env_var in os.environ:
            return os.environ[env_var]
    msg = "GITHUB_TOKEN or GITHUB_PERSONAL_ACCESS_TOKEN must be set"
    raise ValueError(msg)


def get_github_client() -> GitHub[Any]:
    return GitHub[TokenAuthStrategy](auth=TokenAuthStrategy(token=get_github_token()))
