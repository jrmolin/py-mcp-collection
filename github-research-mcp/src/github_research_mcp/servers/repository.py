import asyncio
from typing import TYPE_CHECKING, Annotated, Any, Self

from async_lru import alru_cache
from fastmcp.utilities.logging import get_logger
from githubkit.github import GitHub
from githubkit.response import Response
from githubkit.versions.v2022_11_28.models import ContentDirectoryItems, ContentFile, GitTree
from githubkit.versions.v2022_11_28.models.group_0288 import ContentSymlink
from githubkit.versions.v2022_11_28.models.group_0289 import ContentSubmodule
from githubkit.versions.v2022_11_28.models.group_0412 import CodeSearchResultItem, SearchCodeGetResponse200
from githubkit.versions.v2022_11_28.types.group_0286 import ContentDirectoryItemsType
from githubkit.versions.v2022_11_28.types.group_0287 import ContentFileType
from githubkit.versions.v2022_11_28.types.group_0288 import ContentSymlinkType
from githubkit.versions.v2022_11_28.types.group_0289 import ContentSubmoduleType
from pydantic import BaseModel, Field, RootModel

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
from github_research_mcp.servers.shared.annotations import OWNER, PAGE, PER_PAGE, REPO
from github_research_mcp.servers.shared.utility import decode_content, extract_response

if TYPE_CHECKING:
    from githubkit.response import Response
    from githubkit.versions.v2022_11_28.models import ContentSubmodule, ContentSymlink
    from githubkit.versions.v2022_11_28.models.group_0286 import ContentDirectoryItems
    from githubkit.versions.v2022_11_28.models.group_0411 import SearchResultTextMatchesItems
    from githubkit.versions.v2022_11_28.types import (
        ContentDirectoryItemsType,
        ContentFileType,
        ContentSubmoduleType,
        ContentSymlinkType,
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

DEFAULT_TRUNCATE_CONTENT = 500

ONE_DAY_IN_SECONDS = 60 * 60 * 24


class FileLines(RootModel[dict[int, str]]):
    """A dictionary of line numbers and content pairs."""

    @classmethod
    def from_text(cls, text: str) -> Self:
        text_lines = text.split("\n")

        file_lines = {i + 1: line for i, line in enumerate(text_lines)}

        return cls(root=file_lines)

    def truncate(self, truncate: int) -> Self:
        return self.model_copy(update={"root": {k: v for k, v in self.root.items() if k <= truncate}})


class RepositoryFileWithContent(BaseModel):
    """A file with its path and content."""

    path: str = Field(description="The path of the file.")
    content: FileLines = Field(description="The content of the file.")
    truncated: bool = Field(default=False, description="Whether the content has been truncated.")

    @classmethod
    def from_content_file(cls, content_file: ContentFile, truncate: TRUNCATE_CONTENT = DEFAULT_TRUNCATE_CONTENT) -> Self:
        decoded_content = decode_content(content_file.content)

        file_lines = FileLines.from_text(text=decoded_content)

        return cls(path=content_file.path, content=file_lines).truncate(truncate=truncate)

    def truncate(self, truncate: int) -> Self:
        return self.model_copy(update={"content": self.content.truncate(truncate=truncate)})


class RepositoryFileWithLineMatches(BaseModel):
    """A file with its path and line matches from a search result."""

    path: str = Field(description="The path of the file.")
    matches: list[str] = Field(description="The fragments of the file that match the search query.")

    @classmethod
    def from_code_search_result_item(cls, code_search_result_item: CodeSearchResultItem) -> Self:
        if not code_search_result_item.text_matches:
            msg = f"Expected a list of SearchResultTextMatchesItems, got {type(code_search_result_item.text_matches)}"
            raise TypeError(msg)

        text_matches: list[SearchResultTextMatchesItems] = code_search_result_item.text_matches

        fragments: list[str] = [match.fragment for match in text_matches if match.fragment]

        return cls(path=code_search_result_item.path, matches=fragments)


class RepositorySummary(RootModel[str]):
    """A summary of a repository."""


class RequestFiles(BaseModel):
    """A request for files from a repository."""

    files: list[str] = Field(description="The files to get the content of.")


class RepositoryServer(BaseServer):
    def __init__(self, github_client: GitHub[Any]):
        self.github_client = github_client

    async def get_files(
        self, owner: OWNER, repo: REPO, paths: GET_FILE_PATHS, truncate: TRUNCATE_CONTENT = DEFAULT_TRUNCATE_CONTENT
    ) -> list[RepositoryFileWithContent]:
        """Get the files from a repository. Missing files are ignored."""

        results: list[RepositoryFileWithContent | BaseException] = await asyncio.gather(
            *[self._get_file(owner=owner, repo=repo, path=path, truncate=truncate) for path in paths], return_exceptions=True
        )

        [logger.error(f"Error getting file {result}") for result in results if isinstance(result, BaseException)]

        return [result for result in results if not isinstance(result, BaseException)]

    async def get_readmes(
        self, owner: OWNER, repo: REPO, readmes: README_FILES | None = None, truncate: TRUNCATE_CONTENT = DEFAULT_TRUNCATE_CONTENT
    ) -> list[RepositoryFileWithContent]:
        """Get Readmes from the repository. If none are provided, the README.md, CONTRIBUTING.md, and AGENTS.md will be gathered."""

        context_files: list[str] = readmes or ["README.md", "CONTRIBUTING.md", "AGENTS.md"]

        return await self.get_files(owner=owner, repo=repo, paths=context_files, truncate=truncate)

    async def count_file_extensions(self, owner: OWNER, repo: REPO, top_n: TOP_N_EXTENSIONS = 50) -> list[RepositoryFileCountEntry]:
        """Count the different file extensions found in the repository to identify the most common file types."""

        repository_tree = await self._get_repository_tree(owner=owner, repo=repo)

        return repository_tree.count_files(top_n=top_n)

    async def find_files(
        self,
        owner: OWNER,
        repo: REPO,
        include: INCLUDE_PATTERNS,
        exclude: EXCLUDE_PATTERNS = None,
        include_exclude_is_regex: INCLUDE_EXCLUDE_IS_REGEX = False,
    ) -> RepositoryTree:
        """Find files in a repository by their names/paths. Exclude patterns take precedence over include patterns.

        If Regex is not true, a pattern matches if it is a substring of the file path."""

        tree: Response[GitTree, GitTreeType] = await self.github_client.rest.git.async_get_tree(
            owner=owner, repo=repo, tree_sha="main", recursive="1"
        )

        repository_tree: RepositoryTree = RepositoryTree.from_git_tree(git_tree=tree.parsed_data)

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
        """Search for files in the repository that contain the provided symbols or keywords."""

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
        """Provide a high-level summary of the repository covering the readmes and code layout."""

        return await self._summarize(owner=owner, repo=repo)

    @alru_cache(maxsize=100, ttl=ONE_DAY_IN_SECONDS)
    async def _summarize(self, owner: OWNER, repo: REPO) -> RepositorySummary:
        """Provide a high-level summary of the repository covering the readmes and code layout."""

        repository_tree: RepositoryTree = await self._get_repository_tree(owner=owner, repo=repo)

        readmes: list[RepositoryFileWithContent] = await self.get_readmes(owner=owner, repo=repo)

        top_file_extensions: list[RepositoryFileCountEntry] = repository_tree.count_files(top_n=30)

        return await self._summarize_repository(
            owner=owner, repo=repo, readmes=readmes, top_file_extensions=top_file_extensions, repository_tree=repository_tree
        )

    @alru_cache(maxsize=100, ttl=ONE_DAY_IN_SECONDS)
    async def _get_file(
        self, owner: OWNER, repo: REPO, path: str, truncate: TRUNCATE_CONTENT = DEFAULT_TRUNCATE_CONTENT
    ) -> RepositoryFileWithContent:
        """Get the contents of a file from a repository."""

        try:
            response: Response[
                list[ContentDirectoryItems] | ContentFile | ContentSymlink | ContentSubmodule,
                list[ContentDirectoryItemsType] | ContentFileType | ContentSymlinkType | ContentSubmoduleType,
            ] = await self.github_client.rest.repos.async_get_content(owner=owner, repo=repo, path=path)

        except Exception:
            logger.exception(f"Error getting file {path} from {owner}/{repo}")
            raise

        if not isinstance(response.parsed_data, ContentFile):
            msg = f"Read {path} from {owner}/{repo}, expected a ContentFile, got {type(response.parsed_data)}"
            raise TypeError(msg)

        return RepositoryFileWithContent.from_content_file(content_file=response.parsed_data, truncate=truncate)

    @alru_cache(maxsize=100, ttl=ONE_DAY_IN_SECONDS)
    async def _get_repository_tree(self, owner: OWNER, repo: REPO) -> RepositoryTree:
        """Get the tree of a repository. This can be quite a large amount of data, so it is best to use this sparingly."""

        tree: Response[GitTree, GitTreeType] = await self.github_client.rest.git.async_get_tree(
            owner=owner, repo=repo, tree_sha="main", recursive="1"
        )

        return RepositoryTree.from_git_tree(git_tree=tree.parsed_data)

    async def _summarize_repository(
        self,
        owner: OWNER,
        repo: REPO,
        readmes: list[RepositoryFileWithContent],
        top_file_extensions: list[RepositoryFileCountEntry],
        repository_tree: RepositoryTree,
    ) -> RepositorySummary:
        """Summarize the repository using the readmes, file extension counts, and code layout."""

        system_prompt_builder = SystemPromptBuilder()

        system_prompt_builder.add_text_section(
            title="System Prompt",
            text="""
Your goal is to provide an extremely comprehensive analysis of the repository that would be helpful for an AI coding agent
to understand and work with the repository.

A great analysis includes:

## 1. Project Type & Technology Stack
- Identify the primary programming languages from file extensions
- Detect framework indicators (package.json, requirements.txt, Cargo.toml, etc.)
- Note build system files (Makefile, CMakeLists.txt, etc.)

## 2. Directory Structure Analysis
- Explain the purpose of each major directory
- Identify common patterns (src/, tests/, docs/, examples/)
- Note any unusual or project-specific directory structures
- Distinguish between source code, tests, documentation, and assets

## 3. Key Files & Entry Points
- Identify main/entry point files (main.py, index.js, src/main.rs, etc.)
- Highlight important configuration files (.env.example, config files, docker-compose.yml)
- Note dependency management files (package.json, requirements.txt, Pipfile, etc.)
- Identify CI/CD files (.github/workflows, .gitlab-ci.yml, etc.)
- Identify the primary data models or entities.
- Point to any schema definitions, migrations, or ORM/ODM models.

## 4. Key Patterns & Conventions
- Identify any key patterns or conventions used in the repository, especially patterns
  that are unique to the project. Do not mention conventions or patterns that are standard for
  projects of this type.
- Extensively spell out identified coding practices and patterns used in the repository
  that one must follow in order to match the style of the repository. This includes
  but is not limited to: Observability (logging, metrics, tracing), Error Handling (error codes,
  error messages, error types), Data Storage (database schemas, ORM models, NoSQL collections),
  API Design (endpoints, request/response formats, authentication), Security (authentication, authorization,
  encryption, data protection), Performance (caching, load balancing, optimization), and Testing (unit tests,
  integration tests, end-to-end tests). If any of these practices are standard for projects of this type,
  feel free to omit them or simply mention that they are standard.

## 5. Key Dependencies
- Identify any key dependencies, frameworks, and libraries used in the repository
- Do not mention dependencies that are standard for projects of this type
- List any critical external APIs or services the project communicates with (e.g., Stripe, Twilio, Google Maps API).
  and explain their purpose within the application.

## 6. Development Workflow Indicators
- Identify test directories and testing frameworks
- Note linting/formatting configuration (.eslintrc, .prettierrc, pyproject.toml)
- Highlight documentation files (README, CONTRIBUTING, CHANGELOG, etc.)
- Identify development tools and scripts

## 7. Navigation Guidance
- Provide guidance on where to look for specific types of files
- Highlight files that are likely to be important for understanding the codebase

You will structure your response to be actionable for an AI coding agent working with this repository.

Notes:
- When referencing files simply wrap their paths in backticks, do not make markdown links for them.
- If you are guessing at the purpose of a file that you have not read, mention that you are guessing by saying
  "likely" or "possibly" in your response.
""",
        )

        user_prompt_builder = PromptBuilder()

        readme_names: list[str] = [readme.path for readme in readmes]

        user_prompt_builder.add_yaml_section(
            title="Repository Readmes",
            preamble="The following readmes were gathered to help you provide a summary of the repository:",
            obj=readmes,
        )
        user_prompt_builder.add_yaml_section(
            title="Repository Most Common File Extensions",
            preamble="The following is the 30 most common file extensions in the repository:",
            obj=top_file_extensions,
        )
        user_prompt_builder.add_yaml_section(
            title="Repository Layout", preamble="The following is the layout of the repository:", obj=repository_tree
        )

        more_information_prompt = f"""
You will produce a much better summary if you read some of the files in the repository first,
so you should first make a single request to read the first 400 lines of (up to 30) of the files.

{object_in_text_instructions(object_type=RequestFiles, require=True)}

The file contents will be provided to you and then you can provide the summary after reviewing the files."""

        request_files: RequestFiles = await self._structured_sample(
            system_prompt=system_prompt_builder.render_text(),
            messages=[user_prompt_builder.render_text(), more_information_prompt],
            object_type=RequestFiles,
            max_tokens=5000,
        )

        logger.info(f"Repository Summary has requested files: {request_files.files}")

        request_files.files = [file for file in request_files.files if file not in readme_names][:20]

        requested_files: list[RepositoryFileWithContent] = await self.get_files(
            owner=owner, repo=repo, paths=request_files.files, truncate=400
        )

        user_prompt_builder.add_yaml_section(
            title="Sampling of Relevant Files",
            preamble=(
                "The following files were gathered to help you provide a summary of the repository. Files have been truncated to 400 lines:"
            ),
            obj=requested_files,
        )

        summary: str = await self._sample(
            system_prompt=system_prompt_builder.render_text(),
            messages=[user_prompt_builder.render_text()],
            max_tokens=10000,
        )

        return RepositorySummary.model_validate(summary)
