from collections import defaultdict
from functools import cached_property
from logging import Logger
from typing import TYPE_CHECKING, Annotated, ClassVar, Literal, Self, override

from fastmcp import Context
from fastmcp.tools import Tool as FastMCPTool
from llama_index.core.ingestion.pipeline import IngestionPipeline
from llama_index.core.postprocessor.types import BaseNodePostprocessor
from llama_index.core.schema import BaseNode, MetadataMode, Node, NodeWithScore
from llama_index.core.vector_stores import MetadataFilter, MetadataFilters
from pydantic import BaseModel, ConfigDict, Field

from knowledge_base_mcp.clients.knowledge_base import KnowledgeBaseClient
from knowledge_base_mcp.llama_index.post_processors.get_child_nodes import GetChildNodesPostprocessor
from knowledge_base_mcp.llama_index.post_processors.get_parent_nodes import GetParentNodesPostprocessor
from knowledge_base_mcp.llama_index.post_processors.remove_duplicate_nodes import RemoveDuplicateNodesPostprocessor
from knowledge_base_mcp.llama_index.readers.github import GithubIssuesReader
from knowledge_base_mcp.llama_index.transformations.metadata import AddMetadata, IncludeMetadata
from knowledge_base_mcp.servers.ingest.base import BaseIngestServer
from knowledge_base_mcp.servers.search.base import (
    BaseSearchResponse,
    BaseSearchServer,
    BaseSummaryResult,
    QueryKnowledgeBasesField,
)
from knowledge_base_mcp.utils.logging import BASE_LOGGER
from knowledge_base_mcp.utils.patches import TimerGroup

if TYPE_CHECKING:
    from collections.abc import Sequence

logger: Logger = BASE_LOGGER.getChild(suffix=__name__)


QueryStringField = Annotated[
    str,
    Field(
        description="The plain language query to search GitHub issues for.",
        examples=["Why did the thing break?", "What is this library?", "Why does version 1.0.0 not work?"],
    ),
]

NewKnowledgeBaseField = Annotated[
    str,
    Field(
        description="The name of the Knowledge Base to create to store this webpage.",
        examples=["Python Language - 3.12", "Python Library - Pydantic - 2.11", "Python Library - FastAPI - 0.115"],
    ),
]


class GitHubIssueComment(BaseModel):
    """An issue comment"""

    id: int
    author: str
    author_association: str
    reactions: int
    body: str

    @classmethod
    def from_node(cls, node: BaseNode) -> Self:
        """Create a GitHubIssueComment from a node"""

        return cls(
            id=node.metadata.get("id") or 0,
            author=node.metadata.get("user.login") or "N/A",
            author_association=node.metadata.get("user.association") or "N/A",
            reactions=node.metadata.get("reactions.total_count") or 0,
            body=node.get_content(metadata_mode=MetadataMode.NONE) or "N/A",
        )


class GitHubIssue(BaseModel):
    """An issue with its comments"""

    repository: str
    number: int
    title: str
    body: str
    comments: list[GitHubIssueComment] = Field(default_factory=list)

    @classmethod
    def from_node(cls, issue_node: NodeWithScore, comment_nodes: list[NodeWithScore] | None = None) -> Self:
        """Create a GitHubIssue from a node"""

        comments = [GitHubIssueComment.from_node(node=comment_node.node) for comment_node in comment_nodes or []]

        sorted_comments = sorted(comments, key=lambda x: x.id)

        return cls(
            repository=issue_node.metadata.get("repository") or "N/A",
            number=issue_node.metadata.get("number") or 0,
            title=issue_node.metadata.get("title") or "N/A",
            body=issue_node.get_content(metadata_mode=MetadataMode.NONE) or "N/A",
            comments=sorted_comments,
        )


class GitHubSearchResponse(BaseSearchResponse):
    """A response to a search query with a summary"""

    results: list[GitHubIssue] = Field(description="The results of the search")


class GitHubServer(BaseSearchServer, BaseIngestServer):
    """A server for searching and ingesting GitHub issues."""

    model_config: ClassVar[ConfigDict] = ConfigDict(arbitrary_types_allowed=True)

    server_name: str = "GitHub Server"

    knowledge_base_client: KnowledgeBaseClient

    knowledge_base_type: str = "github_issues"

    @override
    def get_search_tools(self) -> list[FastMCPTool]:
        """Get the search tools for the server."""
        return [
            FastMCPTool.from_function(fn=self.query),
        ]

    @override
    def get_ingest_tools(self) -> list[FastMCPTool]:
        """Get the ingest tools for the server."""
        return [
            FastMCPTool.from_function(fn=self.load_github_issues),
        ]

    @cached_property
    def github_issue_pipeline(self) -> IngestionPipeline:
        """The pipeline for ingesting GitHub issues."""

        return IngestionPipeline(
            name="GitHub Issue Parser",
            transformations=[
                AddMetadata(metadata={"knowledge_base_type": self.knowledge_base_type}),
                IncludeMetadata(embed_keys=["repository", "user.association", "title", "labels"], llm_keys=[]),
                self.knowledge_base_client.duplicate_document_checker,
            ],
            # TODO https://github.com/run-llama/llama_index/issues/19277
            disable_cache=True,
        )

    async def load_github_issues(
        self,
        context: Context | None = None,
        *,
        knowledge_base: NewKnowledgeBaseField,
        owner: Annotated[str, Field(description="The owner of the GitHub repository.")],
        repo: Annotated[str, Field(description="The name of the GitHub repository.")],
        milestone: Annotated[str | None, Field(description="The milestone to filter the issues by.")] = None,
        labels: Annotated[str | None, Field(description="The labels to filter the issues by.")] = None,
        assignee: Annotated[str | None, Field(description="The assignee to filter the issues by.")] = None,
        sort: Annotated[
            Literal["created", "updated", "comments"] | None, Field(description="The sort order to filter the issues by.")
        ] = None,
        direction: Annotated[Literal["asc", "desc"] | None, Field(description="The direction to filter the issues by.")] = None,
        creator: Annotated[str | None, Field(description="The creator to filter the issues by.")] = None,
        include_comments: Annotated[bool, Field(description="Whether to include comments in the issues.")] = False,
    ):
        """Ingest GitHub issues into a Knowledge Base."""

        reader: GithubIssuesReader = GithubIssuesReader(
            owner=owner,
            repo=repo,
        )
        count = 0
        post_process_count = 0

        async with self.start_rumbling(hierarchical=False) as (queue_nodes, _, ingest_result):
            async for document in reader.alazy_load_data(
                milestone=milestone,
                labels=labels,
                assignee=assignee,
                sort=sort,
                direction=direction,
                creator=creator,
                include_comments=include_comments,
            ):
                nodes: Sequence[BaseNode] = [Node(**document.model_dump())]  # pyright: ignore[reportAny]
                count += 1

                processed_nodes = await self.github_issue_pipeline.arun(nodes=nodes)

                post_process_count += len(processed_nodes)

                for node in processed_nodes:
                    node.metadata["knowledge_base"] = knowledge_base

                _ = await queue_nodes.send(item=processed_nodes)
                # _ = await queue_documents.send(item=[document])

        await self._log_info(
            context=context,
            message=f"Ingested {ingest_result.ingested_nodes} issues into {knowledge_base}",
        )

        return ingest_result

    @cached_property
    @override
    def result_post_processors(self) -> list[BaseNodePostprocessor]:
        return [
            RemoveDuplicateNodesPostprocessor(by_id=True, by_hash=True),
            self.knowledge_base_client.reranker,
            GetParentNodesPostprocessor(doc_store=self.knowledge_base_client.docstore, keep_child_nodes=False),
            GetChildNodesPostprocessor(doc_store=self.knowledge_base_client.docstore),
        ]

    def _convert_to_github_issues(self, nodes_with_scores: list[NodeWithScore]) -> list[GitHubIssue]:
        """Format the results"""

        nodes_by_id: dict[str, NodeWithScore] = {node_with_score.node.node_id: node_with_score for node_with_score in nodes_with_scores}
        nodes_by_parent_id: dict[str, list[NodeWithScore]] = defaultdict(list)

        for node_with_score in nodes_with_scores:
            if parent_id := node_with_score.node.parent_node:
                nodes_by_parent_id[parent_id.node_id].append(node_with_score)

        github_issues: list[GitHubIssue] = []

        for issue_node_id, comment_nodes in nodes_by_parent_id.items():
            if not (issue_node := nodes_by_id.get(issue_node_id)):
                logger.warning(f"Parent node not found: {issue_node_id}")
                continue

            github_issue: GitHubIssue = GitHubIssue.from_node(issue_node=issue_node, comment_nodes=comment_nodes)

            github_issues.append(github_issue)

        return github_issues

    @override
    async def query(
        self,
        query: QueryStringField,
        knowledge_bases: QueryKnowledgeBasesField | None = None,
        result_count: Annotated[int, Field(description="The number of results to return.")] = 20,
        issues_only: Annotated[bool, Field(description="Whether to only return issues.")] = False,
        repository: Annotated[str | None, Field(description="The indexed repository to search for issues in.")] = None,
    ) -> GitHubSearchResponse:
        """Query the GitHub issues"""
        timer_group: TimerGroup = TimerGroup(name="DocumentationSearchServer.query")

        extra_filters: list[MetadataFilter | MetadataFilters] = []
        if repository:
            extra_filters.append(MetadataFilter(key="repository", value=repository))
        elif issues_only:
            extra_filters.append(MetadataFilter(key="type", value="issue"))

        with timer_group.time(name="fetch_results"):
            nodes_with_scores = await self.knowledge_base_client.aretrieve(
                query=query,
                knowledge_base=knowledge_bases,
                knowledge_base_types=[self.knowledge_base_type],
                extra_filters=MetadataFilters(filters=extra_filters) if extra_filters else None,
            )

        summary: BaseSummaryResult = self.format_summary(nodes_with_scores=nodes_with_scores)

        nodes_with_scores = nodes_with_scores[:result_count]

        with timer_group.time(name="apply_post_processors"):
            nodes_with_scores = await self.apply_post_processors(
                query=query,
                nodes_with_scores=nodes_with_scores,
                post_processors=self.result_post_processors,
            )

        result: list[GitHubIssue] = self._convert_to_github_issues(nodes_with_scores=nodes_with_scores)

        return GitHubSearchResponse(query=query, summary=summary, results=result)
