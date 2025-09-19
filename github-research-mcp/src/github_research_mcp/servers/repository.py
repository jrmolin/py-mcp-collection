import asyncio
from collections import defaultdict
from typing import TYPE_CHECKING, Annotated, Any

import httpx
from async_lru import alru_cache
from fastmcp.utilities.logging import get_logger
from githubkit.exception import GitHubException, RequestFailed
from githubkit.github import GitHub
from githubkit.response import Response
from githubkit.versions.v2022_11_28.models import ContentDirectoryItems, ContentFile, FullRepository, GitTree
from githubkit.versions.v2022_11_28.models.group_0288 import ContentSymlink
from githubkit.versions.v2022_11_28.models.group_0289 import ContentSubmodule
from githubkit.versions.v2022_11_28.types.group_0286 import ContentDirectoryItemsType
from githubkit.versions.v2022_11_28.types.group_0287 import ContentFileType
from githubkit.versions.v2022_11_28.types.group_0288 import ContentSymlinkType
from githubkit.versions.v2022_11_28.types.group_0289 import ContentSubmoduleType
from pydantic import Field

from github_research_mcp.models.query.base import (
    AllKeywordsQualifier,
    AllSymbolsQualifier,
    AnyKeywordsQualifier,
    AnySymbolsQualifier,
    LanguageQualifier,
    PathQualifier,
)
from github_research_mcp.models.query.code import CodeSearchQuery
from github_research_mcp.models.repository.tree import RepositoryFileCountEntry, RepositoryTree
from github_research_mcp.sampling.extract import object_in_text_instructions
from github_research_mcp.sampling.prompts import PromptBuilder, SystemPromptBuilder
from github_research_mcp.servers.base import BaseServer
from github_research_mcp.servers.models.repository import (
    DEFAULT_README_TRUNCATE_CONTENT,
    DEFAULT_TRUNCATE_CONTENT,
    Repository,
    RepositoryFileWithContent,
    RepositoryFileWithLineMatches,
    RepositoryNotFoundError,
    RepositorySummary,
    RequestFilesForSummary,
)
from github_research_mcp.servers.shared.annotations import OWNER, PAGE, PER_PAGE, REPO
from github_research_mcp.servers.shared.utility import extract_response

if TYPE_CHECKING:
    from githubkit.response import Response
    from githubkit.versions.v2022_11_28.models import ContentSubmodule, ContentSymlink
    from githubkit.versions.v2022_11_28.models.group_0286 import ContentDirectoryItems
    from githubkit.versions.v2022_11_28.models.group_0412 import SearchCodeGetResponse200
    from githubkit.versions.v2022_11_28.types import (
        ContentDirectoryItemsType,
        ContentFileType,
        ContentSubmoduleType,
        ContentSymlinkType,
        FullRepositoryType,
        GitTreeType,
    )

logger = get_logger(__name__)

INCLUDE_EXCLUDE_IS_REGEX = Annotated[
    bool, Field(description="Whether the include and exclude patterns provided should be evaluated as regex.")
]
INCLUDE_PATTERNS = Annotated[
    list[str],
    Field(
        description=(
            "The patterns to check file paths against. File paths matching any of these patterns will be included in the results. "
        ),
    ),
]
EXCLUDE_PATTERNS = Annotated[
    list[str] | None,
    Field(
        description=(
            "The patterns to check file paths against. File paths matching any of these patterns will be excluded from the results. "
            "If None, no files will be excluded."
        )
    ),
]
GET_FILE_PATHS = Annotated[
    list[str],
    Field(description="The paths of the files in the repository to get the content of. For example, 'README.md' or 'path/to/file.txt'."),
]
README_FILES = Annotated[list[str], Field(description="The files to get the content of. For example, 'README.md' or 'path/to/file.txt'.")]

TOP_N_EXTENSIONS = Annotated[int, Field(description="The number of top extensions to return.")]


TRUNCATE_CONTENT = Annotated[int, Field(description="The number of lines to truncate the content to.")]

ONE_DAY_IN_SECONDS = 60 * 60 * 24

LARGE_REPOSITORY_THRESHOLD = 1000


class RepositoryServer(BaseServer):
    validation_locks: dict[str, asyncio.Lock]
    summary_locks: dict[str, asyncio.Lock]

    def __init__(self, github_client: GitHub[Any]):
        self.github_client = github_client
        self.validation_locks = defaultdict(asyncio.Lock)
        self.summary_locks = defaultdict(asyncio.Lock)

    async def get_repository(self, owner: OWNER, repo: REPO) -> Repository:
        """Get basic information about a GitHub repository."""

        return await self._require_valid_repository(owner=owner, repo=repo)

    async def get_files(
        self, owner: OWNER, repo: REPO, paths: GET_FILE_PATHS, truncate: TRUNCATE_CONTENT = DEFAULT_TRUNCATE_CONTENT
    ) -> list[RepositoryFileWithContent]:
        """Get files from a GitHub repository, optionally truncating the content to a specified number of lines."""

        await self._require_valid_repository(owner=owner, repo=repo)

        results: list[RepositoryFileWithContent | BaseException] = await asyncio.gather(
            *[self._get_file(owner=owner, repo=repo, path=path, truncate=truncate) for path in paths], return_exceptions=True
        )

        [logger.error(f"Error getting file {result}") for result in results if isinstance(result, BaseException)]

        return [result for result in results if not isinstance(result, BaseException)]

    async def get_readmes(
        self, owner: OWNER, repo: REPO, truncate: TRUNCATE_CONTENT = DEFAULT_TRUNCATE_CONTENT
    ) -> list[RepositoryFileWithContent]:
        """Get all asciidoc (.adoc, .asciidoc), markdown (.md), and other text files (.txt, .rst) from the root of the
        GitHub repository."""

        await self._require_valid_repository(owner=owner, repo=repo)

        repository_tree: RepositoryTree = await self.find_files(
            owner=owner, repo=repo, include=[".md", ".adoc", ".asciidoc", ".txt", ".rst"], recursive=False
        )

        return await self.get_files(owner=owner, repo=repo, paths=repository_tree.files, truncate=truncate)

    # async def _get_readmes(
    #     self,
    #     owner: OWNER,
    #     repo: REPO,
    #     readmes: list[str],
    #     truncate: TRUNCATE_CONTENT = DEFAULT_TRUNCATE_CONTENT,
    #     error_on_missing: bool = True,
    # ) -> list[RepositoryFileWithContent]:
    #     repository_tree: RepositoryTree = await self.get_repository_tree(owner=owner, repo=repo, recursive=False)

    #     existing_readmes: list[str] = repository_tree.filter_files(files=readmes, case_insensitive=True)

    #     if not existing_readmes:
    #         if error_on_missing:
    #             raise MiscRepositoryError(action=f"Get readmes from {owner}/{repo}", extra_info=f"{readmes} not found in {owner}/{repo}")

    #         return []

    #     return await self.get_files(
    #         owner=owner,
    #         repo=repo,
    #         paths=existing_readmes,
    #         truncate=truncate,
    #     )

    async def get_file_extensions(self, owner: OWNER, repo: REPO, top_n: TOP_N_EXTENSIONS = 50) -> list[RepositoryFileCountEntry]:
        """Count the different file extensions found in a GitHub repository to identify the most common file types."""

        await self._require_valid_repository(owner=owner, repo=repo)

        repository_tree: RepositoryTree = await self.get_repository_tree(owner=owner, repo=repo)

        return repository_tree.count_file_extensions(top_n=top_n)

    async def find_files(
        self,
        owner: OWNER,
        repo: REPO,
        include: INCLUDE_PATTERNS,
        exclude: EXCLUDE_PATTERNS = None,
        include_exclude_is_regex: INCLUDE_EXCLUDE_IS_REGEX = False,
        recursive: bool = True,
    ) -> RepositoryTree:
        """Find files in a GitHub repository by their names/paths. Exclude patterns take precedence over include patterns.

        If Regex is not true, a pattern matches if it is a substring of the file path."""

        await self._require_valid_repository(owner=owner, repo=repo)

        repository_tree: RepositoryTree = await self.get_repository_tree(owner=owner, repo=repo, recursive=recursive)

        return repository_tree.to_filtered_tree(include=include, exclude=exclude, include_exclude_is_regex=include_exclude_is_regex)

    async def search_files(
        self,
        owner: OWNER,
        repo: REPO,
        keywords_or_symbols: AnyKeywordsQualifier | AllKeywordsQualifier | AnySymbolsQualifier | AllSymbolsQualifier,
        path: Annotated[PathQualifier | None, Field(description="Optional path to limit the search to.")] = None,
        language: Annotated[LanguageQualifier | None, Field(description="Optional programming language to limit the search to.")] = None,
        per_page: PER_PAGE = 30,
        page: PAGE = 1,
    ) -> list[RepositoryFileWithLineMatches]:
        """Search for files in a GitHub repository that contain the provided symbols or keywords."""

        await self._require_valid_repository(owner=owner, repo=repo)

        code_search_query: CodeSearchQuery = CodeSearchQuery.from_repo_or_owner(owner=owner, repo=repo)

        code_search_query.add_qualifier(qualifier=keywords_or_symbols)

        if language:
            code_search_query.add_qualifier(language)

        if path:
            code_search_query.add_qualifier(path)

        search_query: str = code_search_query.to_query()

        response: SearchCodeGetResponse200 = extract_response(
            await self.github_client.rest.search.async_code(
                q=search_query, per_page=per_page, page=page, headers={"Accept": "application/vnd.github.text-match+json"}
            )
        )

        return [
            RepositoryFileWithLineMatches.from_code_search_result_item(code_search_result_item=code_search_result_item)
            for code_search_result_item in response.items
        ]

    async def summarize(self, owner: OWNER, repo: REPO) -> RepositorySummary:
        """Provide a high-level summary of a GitHub repository covering the readmes and code layout."""

        async with self.summary_locks[f"{owner}/{repo}"]:
            return await self._summarize(owner=owner, repo=repo)

    @alru_cache(maxsize=100, ttl=ONE_DAY_IN_SECONDS)
    async def _summarize(self, owner: OWNER, repo: REPO) -> RepositorySummary:
        """Provide a high-level summary of a GitHub repository covering the readmes and code layout."""

        logger.info(f"Gathering repository context for {owner}/{repo}")

        repository: Repository = await self._require_valid_repository(owner=owner, repo=repo)

        repository_tree, readmes = await asyncio.gather(
            self.get_repository_tree(owner=owner, repo=repo),
            self.get_readmes(owner=owner, repo=repo, truncate=DEFAULT_README_TRUNCATE_CONTENT),
        )

        logger.info(f"Starting summarization of repository {owner}/{repo}")

        return await self._summarize_repository(
            owner=owner,
            repo=repo,
            repository=repository,
            readmes=readmes,
            repository_tree=repository_tree,
        )

    async def _get_file(
        self, owner: OWNER, repo: REPO, path: str, truncate: TRUNCATE_CONTENT = DEFAULT_TRUNCATE_CONTENT
    ) -> RepositoryFileWithContent:
        """Get the contents of a file from a repository."""

        try:
            response: Response[
                list[ContentDirectoryItems] | ContentFile | ContentSymlink | ContentSubmodule,
                list[ContentDirectoryItemsType] | ContentFileType | ContentSymlinkType | ContentSubmoduleType,
            ] = await self.github_client.rest.repos.async_get_content(owner=owner, repo=repo, path=path)

        except RequestFailed as request_error:
            self._log_request_errors(action=f"Get file {path} from {owner}/{repo}", github_exception=request_error)
            raise

        if not isinstance(response.parsed_data, ContentFile):
            msg = f"Read {path} from {owner}/{repo}, expected a ContentFile, got {type(response.parsed_data)}"
            raise TypeError(msg)

        return RepositoryFileWithContent.from_content_file(content_file=response.parsed_data, truncate=truncate)

    async def get_repository_tree(self, owner: OWNER, repo: REPO, recursive: bool = True) -> RepositoryTree:
        """Get the tree of a repository. This can be quite a large amount of data, so it is best to use this sparingly."""

        tree: Response[GitTree, GitTreeType] = await self.github_client.rest.git.async_get_tree(
            owner=owner, repo=repo, tree_sha="main", recursive="1" if recursive else None
        )

        return RepositoryTree.from_git_tree(git_tree=tree.parsed_data)

    def _log_request_errors(self, action: str, github_exception: GitHubException) -> None:
        if isinstance(github_exception, RequestFailed) and github_exception.response.status_code == httpx.codes.NOT_FOUND:
            logger.warning(f"{action}: Not found error for {github_exception.request.url}")
        else:
            logger.error(f"{action}: Unknown error: {github_exception}")

    async def _require_valid_repository(self, owner: OWNER, repo: REPO) -> Repository:
        """Validate a GitHub repository."""

        async with self.validation_locks[f"{owner}/{repo}"]:
            if repository := await self._get_repository(owner=owner, repo=repo):
                return repository

        msg = "Note -- Repositories that are private will report as not found."

        raise RepositoryNotFoundError(action=f"Validate repository {owner}/{repo}", extra_info=msg) from None

    async def _get_repository(self, owner: OWNER, repo: REPO) -> Repository | None:
        """Get a repository."""

        try:
            response: Response[FullRepository, FullRepositoryType] = await self.github_client.rest.repos.async_get(owner=owner, repo=repo)
        except GitHubException as github_exception:
            self._log_request_errors(action=f"Get repository {owner}/{repo}", github_exception=github_exception)
            return None

        return Repository.from_full_repository(full_repository=response.parsed_data)

    async def _summarize_repository(
        self,
        owner: OWNER,
        repo: REPO,
        repository: Repository,
        readmes: list[RepositoryFileWithContent],
        repository_tree: RepositoryTree,
    ) -> RepositorySummary:
        """Summarize the repository using the readmes, file extension counts, and code layout."""

        system_prompt_builder = SystemPromptBuilder()

        system_prompt_builder.add_text_section(
            title="System Prompt",
            text="""
Your goal is to produce an AGENTS.md++: comprehensive, information-dense, and immediately actionable for coding agents. Be concise per
bullet, but cover all important areas thoroughly. Optimize for density; ~150-250 lines is a good target if evidence warrants.

GLOBAL CONSTRAINTS:
- Prefer concrete evidence: cite files and key symbols; include short code/line ranges when decisive.
- Include non-obvious, project-unique details; if standard for this stack, say "standard for this project type."
- If a section is incomplete, include what you found and add a bullet "Where to learn more" listing the best
  files/dirs to consult and relevant search patterns. If no evidence exists, write "Not found" and cite what you searched.
- Avoid repetition; cross-reference earlier bullets instead of restating.
- Prefer concrete evidence over generalities. Prefer pointing to a location where more information can be found over
  attempting to provide a comprehensive analysis of every relevant file to the topic.
- At most 1-2 citations per bullet. Prefer the single best file + symbol.
- No long file lists; representative example + pointer.

OUTPUT FORMAT (use these exact section titles; keep each section compact but complete):

## Architecture Overview
- ≤120 words on purpose, major modules, and primary data flow. Cite 2-4 core files/dirs.

## Code Style & Conventions
- Extract explicit rules from linter/formatter/type-check configs; mark inferred rules as "(inferred)".
- Bullets: quote style, semicolons, indentation, naming (vars/functions), import rules, max line length, file naming,
  test naming, package layout.
- Cite exact config paths and keys (e.g., `pyproject.toml:[tool.black]`, `checkstyle.xml:RuleName`, `spotless*`) if known

## Observability & Error Handling
- Logging libraries/patterns, metrics/tracing (if any), error categorization/utilities. Cite files/symbols.

## Dependencies & Services
- Only critical/non-standard runtime dependencies and external services: version/purpose and integration points (path + symbol).

## Key Directories & Entry Points
- Major dirs with 1-2 example files each; identify app entry points and why they matter.

## Build & Test
Build and test commands should not be guessed. They must be exact from the existing documentation in the repository.
- Add a short "Quick recipes" sublist for common tasks (e.g., run subset of tests, format all files,
  run a specific module). If the repository uses a makefile, package.json, pyproject.toml, etc., prefer calling
  those commands over deriving commands from the makefile.

## Unique Workflows
- Generators/codegen, data pipelines, monorepo tooling, or custom build steps. Cite entry files/commands.

## API Surface Map
- Summarize primary external interfaces (REST/GraphQL/gRPC/CLI): list top endpoints/commands with paths and handler symbols.
- If partial, add "Where to learn more": point to routers/controllers
  (e.g., `**/routes*`, `**/controllers/**`, `server.*`), OpenAPI/Swagger (`**/openapi*`, `**/swagger*`),
  GraphQL schema/resolvers (`**/*.graphql*`, `**/schema*`, `**/resolver*`), gRPC protos (`**/*.proto`), and
  CLI help commands.

## Data Model & Storage
- Identify locations of schemas/migrations/models and provide a, "Where to learn more" for migrations directories,
  ORM models, schema registries, etc.

## Compatibility & Versioning
- Required language/toolchain versions; framework/library major versions; semver or compatibility guarantees.

## Governance & Ownership
- `CODEOWNERS`, maintainers, ownership notes; link to on-call/escalation info if present.

## Onboarding Steps and common gotchas
A high-level signal, 3-6 bullets pointing to the most valuable follow-up actions/files for
deeper onboarding. If identified in the documentation, share a short list of 2-5 gotchas
derived from docs/CI (e.g., required JVM arg, flaky test advice, platform-specific steps). Do not guess.

Notes:
- Wrap literal commands, filenames, and env vars in backticks.
- Prefer short bullets; use representative examples with citations.
""",
        )

        user_prompt_builder = PromptBuilder()

        readme_names: list[str] = [readme.path for readme in readmes]

        user_prompt_builder.add_yaml_section(
            title="Repository Information",
            preamble="The following is the information about the repository:",
            obj=repository,
        )

        user_prompt_builder.add_yaml_section(
            title="Repository Readmes",
            preamble="The following readmes were gathered to help you provide a summary of the repository:",
            obj=readmes,
        )

        user_prompt_builder.add_yaml_section(
            title="Repository Most Common File Extensions",
            preamble="The following is the 30 most common file extensions in the repository:",
            obj=repository_tree.count_file_extensions(top_n=30),
        )

        # We do directories here so that the yaml formatter puts a new line/space between each directory to help the LLM not mix up dirs
        user_prompt_builder.add_yaml_section(
            title="Repository Layout", preamble="The following is the layout of the repository:", obj=repository_tree.directories
        )

        user_prompt_builder.add_yaml_section(
            title="Repository Root Files", preamble="The following is the layout of the repository:", obj=repository_tree.files
        )

        user_prompt_builder.add_text_section(
            title="Request Files",
            text=f"""
To generate accurate commands and conventions, request the most informative files first.
Rules:
- Max 100 files, first 1000 lines each.
- Do not request files already provided in "Repository Readmes"
- Do not request the same file multiple times
- Prefer text/code files; skip binaries and large generated assets

The following patterns are examples. Only request files that exist in the provided repository tree.

Prioritized selection funnel (target distribution; adjust if missing):
1) Foundational docs (≈10-15)
- Docs: `docs/{{index,overview,architecture}}.{{md,adoc,mdx}}`
- ADRs: `**/adr/**.md`, `**/architecture/**.md`

2) Build, CI/CD, runtime (≈5-15)
- Build/manifests: `package.json`, `pnpm-lock.yaml`, `yarn.lock`, `pyproject.toml`, `requirements*.txt`,
    `setup.{{cfg,py}}`, `build.gradle`, `settings.gradle`, `pom.xml`, `Cargo.toml`, `Makefile`
- Container/runtime: `Dockerfile*`, `.dockerignore`, `docker-compose*.yml`, `Procfile`
- CI: `.github/workflows/*.yml` (cap 8 across jobs), `.gitlab-ci.yml`, `.buildkite/**`

3) Entry points & configuration (≈15-20)
- Executables/entry: `main.*`, `cmd/**/main.*`, `server.{{js,ts,py,go}}`, `app.{{py,rb,js,ts}}`, framework bootstraps
- App config: `config/**`, `settings.*`, `application.*`, `src/**/routes*`, controllers

4) Tests (prefer integration/e2e) (≈15-20)
- `tests/**/{{integration,e2e,javaRestTest,yamlRestTest,internalClusterTest}}/**`
- Central test helpers/configs: `pytest.ini`, `jest.config.*`, `vitest.config.*`, `test/**/helpers*`

5) Code quality and style (≈10-15)
- `.eslintrc*`, `.prettierrc*`, `ruff.toml`, `mypy.ini`, `pylintrc`, `checkstyle.xml`, `spotless*`, `.editorconfig`, `tsconfig.json`,
    `pyproject.toml` sections

6) Other (≈30-40)
- Other files that you see in the directory tree that you think will reveal helpful information about the repository.

If the repository is large, fill the full 100-file budget across the categories.

Language-specific overlays (choose relevant ones to meet the 100-file budget):
- Java/Gradle: `build.gradle`, `settings.gradle`, `gradle.properties`, `buildSrc/**`, `build-conventions/**`, `**/checkstyle.xml`,
  `**/spotless*`, module `*/src/{{main, test}}/java/**` entry points.
- Python: `pyproject.toml`, `setup.cfg`, `requirements*.txt`, `tox.ini`, `pytest.ini`, `mypy.ini`, `ruff.toml`, `src/**/__init__.py`
  and main entry points.
- Node/TypeScript: `package.json`, lockfiles, `.eslintrc*`, `.prettierrc*`, `tsconfig.json`, `src/**/index.{{ts, js}}`, API
  route/controller files.
- Go: `go.mod`, `go.sum`, `cmd/**`, `internal/**`, `pkg/**`, `Makefile`, `magefile.go`.
- Rust: `Cargo.toml`, `build.rs`, `src/main.rs`, `src/lib.rs`.
- .NET: `*.sln`, `*.csproj`, `Directory.Build.*`, `src/**/Program.cs`.

Only include overlays for stacks detected by manifests/config (e.g., presence of build.gradle, pyproject.toml). Omit non-relevant overlays
entirely.

{object_in_text_instructions(object_type=RequestFilesForSummary, require=True)}

The file contents will be provided to you and then you can provide the summary after reviewing the files.

Please request files now.""",
        )

        logger.info(f"Determining which files to gather for summary of {owner}/{repo}")

        request_files: RequestFilesForSummary = await self._structured_sample(
            system_prompt=system_prompt_builder.render_text(),
            messages=user_prompt_builder.to_sampling_messages(),
            object_type=RequestFilesForSummary,
            max_tokens=10000,
        )

        request_file_paths = request_files.trim(remove_files=readme_names, truncate=100)

        logger.info(f"Requesting {len(request_file_paths)} files for summary of {owner}/{repo}: {request_file_paths}")

        requested_files: list[RepositoryFileWithContent] = await self.get_files(
            owner=owner, repo=repo, paths=request_file_paths, truncate=400
        )

        # Remove the request files section
        user_prompt_builder.pop()

        user_prompt_builder.add_yaml_section(
            title="Sampling of Relevant Files",
            preamble=(
                "The following files were gathered to help you provide a summary of the repository. Files have been truncated to 400 lines:"
            ),
            obj=requested_files,
        )

        logger.info(f"Producing summary of {owner}/{repo} via sampling.")

        summary: str = await self._sample(
            system_prompt=system_prompt_builder.render_text(),
            messages=user_prompt_builder.to_sampling_messages(),
            max_tokens=55000,
        )

        logger.info(f"Completed summary of {owner}/{repo}")

        return RepositorySummary.model_validate(summary)
