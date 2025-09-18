from typing import TYPE_CHECKING

from fastmcp.utilities.logging import get_logger

from github_research_mcp.servers.repository import (
    RepositoryServer,
    RepositorySummary,
)
from github_research_mcp.servers.shared.annotations import OWNER, REPO

if TYPE_CHECKING:
    from github_research_mcp.servers.models.repository import Repository

ONE_DAY_IN_SECONDS = 60 * 60 * 24

logger = get_logger(__name__)


class PublicServer:
    repository_server: RepositoryServer

    minimum_stars: int

    owner_allowlist: list[str]

    def __init__(
        self,
        repository_server: RepositoryServer,
        minimum_stars: int,
        owner_allowlist: list[str],
    ):
        self.repository_server = repository_server
        self.minimum_stars = minimum_stars
        self.owner_allowlist = owner_allowlist

    async def _check_minimum_stars(self, owner: OWNER, repo: REPO) -> bool:
        repository: Repository | None = await self.repository_server._get_repository(owner=owner, repo=repo)

        if repository is None:
            msg = f"Repository {owner}/{repo} does not exist or access is not authorized"
            raise ValueError(msg)

        if repository.stars < self.minimum_stars:
            msg = f"Repository {owner}/{repo} has less than {self.minimum_stars} stars and is not eligible for summarization"
            return False

        return True

    async def _check_owner_allowlist(self, owner: OWNER) -> bool:
        return owner in self.owner_allowlist

    async def summarize(self, owner: OWNER, repo: REPO) -> RepositorySummary:
        if not await self._check_minimum_stars(owner=owner, repo=repo) and not await self._check_owner_allowlist(owner=owner):
            msg = (
                f"Repository {owner}/{repo} is not eligible for summarization, "
                f"it has less than {self.minimum_stars} stars and is not explicitly allowlisted."
            )
            raise ValueError(msg)

        return await self.repository_server.summarize(owner=owner, repo=repo)
