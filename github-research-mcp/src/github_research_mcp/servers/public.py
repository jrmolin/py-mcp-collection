from github_research_mcp.models.repository.tree import RepositoryTree
from github_research_mcp.servers.repository import (
    EXCLUDE_PATTERNS,
    INCLUDE_PATTERNS,
    RepositoryServer,
    RepositorySummary,
)
from github_research_mcp.servers.shared.annotations import OWNER, REPO


class PublicServer:
    repository_server: RepositoryServer

    owner_allowlist: list[str]

    def __init__(self, repository_server: RepositoryServer, owner_allowlist: list[str]):
        self.repository_server = repository_server
        self.owner_allowlist = owner_allowlist

    def _validate_owner(self, owner: OWNER) -> None:
        if owner not in self.owner_allowlist:
            msg = f"Owner {owner} is not in the allowlist"
            raise ValueError(msg)

    async def find_files(self, owner: OWNER, repo: REPO, include: INCLUDE_PATTERNS, exclude: EXCLUDE_PATTERNS) -> RepositoryTree:
        self._validate_owner(owner=owner)

        return await self.repository_server.find_files(owner=owner, repo=repo, include=include, exclude=exclude)

    async def summarize(self, owner: OWNER, repo: REPO) -> RepositorySummary:
        self._validate_owner(owner=owner)

        return await self.repository_server.summarize(owner=owner, repo=repo)
