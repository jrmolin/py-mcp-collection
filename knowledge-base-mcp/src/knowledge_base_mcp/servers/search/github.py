from collections import defaultdict
from logging import Logger
from typing import Annotated, ClassVar, Self, override

from fastmcp.tools import Tool as FastMCPTool
from llama_index.core.bridge.pydantic import Field
from llama_index.core.postprocessor import SentenceTransformerRerank
from llama_index.core.postprocessor.types import BaseNodePostprocessor
from llama_index.core.schema import BaseNode, MetadataMode, NodeRelationship, NodeWithScore
from pydantic import BaseModel, ConfigDict

from knowledge_base_mcp.clients.knowledge_base import KnowledgeBaseClient
from knowledge_base_mcp.llama_index.post_processors.child_replacer import ChildReplacerNodePostprocessor
from knowledge_base_mcp.llama_index.post_processors.parent_context import ParentContextNodePostprocessor
from knowledge_base_mcp.servers.models.documentation import KnowledgeBaseSummary
from knowledge_base_mcp.servers.search.base import BaseSearchServer
from knowledge_base_mcp.utils.logging import BASE_LOGGER

logger: Logger = BASE_LOGGER.getChild(suffix=__name__)


QueryStringField = Annotated[
    str,
    Field(
        description="The plain language query to search GitHub issues for.",
        examples=["Why did the thing break?", "What is this library?", "Why does version 1.0.0 not work?"],
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
    def from_node(cls, issue_node: BaseNode, comment_nodes: list[BaseNode] | None = None) -> Self:
        """Create a GitHubIssue from a node"""

        comments = [GitHubIssueComment.from_node(node=comment_node) for comment_node in comment_nodes or []]

        sorted_comments = sorted(comments, key=lambda x: x.id)

        return cls(
            repository=issue_node.metadata.get("repository") or "N/A",
            number=issue_node.metadata.get("number") or 0,
            title=issue_node.metadata.get("title") or "N/A",
            body=issue_node.get_content(metadata_mode=MetadataMode.NONE) or "N/A",
            comments=sorted_comments,
        )

    # @classmethod
    # def from_nodes(cls, nodes: list[BaseNode]) -> list["GitHubIssue"]:
    #     """Create a GitHubIssue from a list of nodes"""
    #     nodes_by_id: dict[str, BaseNode] = {node.node_id: node for node in nodes}

    #     issues: list["GitHubIssue"] = []

    #     nodes_by_parent_id: dict[str, list[BaseNode]] = defaultdict(list)
    #     for node in nodes:
    #         if parent_id := node.metadata.get("parent"):
    #             nodes_by_parent_id[parent_id].append(node)
    #         else:
    #             issues.append(cls.from_node(node=node))

    #     # The parents are GitHub Issues, the children are GitHub Issue Comments

    #     for github_issue_node_id, github_issue_comment_nodes in nodes_by_parent_id.items():
    #         if not (github_issue_node := nodes_by_id.get(github_issue_node_id)):
    #             logger.warning(f"GitHub issue node not found: {github_issue_node_id}")
    #             continue

    #         issues.append(GitHubIssue.from_node(node=github_issue_node, comment_nodes=github_issue_comment_nodes))

    #     return issues


class SearchResponseWithSummary(BaseModel):
    """A response to a search query with a summary"""

    query: str = Field(description="The query that was used to search the knowledge base")
    summary: KnowledgeBaseSummary = Field(description="The summary of the search")
    results: list[GitHubIssue] = Field(description="The results of the search")


class GitHubSearchServer(BaseSearchServer):
    """A server for searching GitHub issues."""

    model_config: ClassVar[ConfigDict] = ConfigDict(arbitrary_types_allowed=True)

    server_name: str = "GitHub Search Server"

    knowledge_base_client: KnowledgeBaseClient

    knowledge_base_type: str = "github_issues"

    reranker_model: str

    @override
    def get_tools(self) -> list[FastMCPTool]:
        """Get the tools for the server."""
        return [
            FastMCPTool.from_function(fn=self.query),
        ]

    @override
    def result_post_processors(self, result_count: int = 20) -> list[BaseNodePostprocessor]:
        post_processors: list[BaseNodePostprocessor] = super().result_post_processors(result_count=result_count)

        reranker = SentenceTransformerRerank(model=self.reranker_model, top_n=result_count)

        post_processors.append(reranker)

        return post_processors

    async def query(
        self,
        query: QueryStringField,
        repository: Annotated[str | None, Field(description="The indexed repository to search for issues in.")] = None,
        result_count: Annotated[int, Field(description="The number of results to return.")] = 20,
    ) -> SearchResponseWithSummary:
        """Query the GitHub issues"""

        nodes_with_scores: list[NodeWithScore] = await self.get_results(
            query, knowledge_bases=[repository] if repository else None, count=result_count
        )

        nodes: list[BaseNode] = [node.node for node in nodes_with_scores]

        issue_nodes: list[BaseNode] = [node for node in nodes if not node.parent_node]
        comment_nodes: list[BaseNode] = [node for node in nodes if node.parent_node]

        issue_nodes_to_gather: set[str] = {node.node_id for node in issue_nodes}

        for node in comment_nodes:
            if parent_id := node.parent_node:
                issue_nodes_to_gather.add(parent_id.node_id)

        issues: list[BaseNode] = self.knowledge_base_client.docstore.get_nodes(node_ids=list(issue_nodes_to_gather))
        issues_by_id: dict[str, BaseNode] = {issue.node_id: issue for issue in issues}

        comment_ids_to_gather: set[str] = set()

        for issue in issues:
            if child_nodes := issue.child_nodes:
                comment_ids_to_gather.update(child_node.node_id for child_node in child_nodes)

        comments: list[BaseNode] = self.knowledge_base_client.docstore.get_nodes(node_ids=list(comment_ids_to_gather))
        comments_by_issue_id: dict[str, list[BaseNode]] = defaultdict(list)

        for comment in comments:
            if parent_id := comment.parent_node:
                comments_by_issue_id[parent_id.node_id].append(comment)

        github_issues: list[GitHubIssue] = []

        for issue_id, comment_nodes in comments_by_issue_id.items():
            if not (issue := issues_by_id.get(issue_id)):
                logger.warning(f"Issue not found: {issue_id}")
                continue

            github_issues.append(GitHubIssue.from_node(issue_node=issue, comment_nodes=comment_nodes))

        summary: KnowledgeBaseSummary = await self.get_summary(query, knowledge_bases=[repository] if repository else None)

        return SearchResponseWithSummary(query=query, summary=summary, results=github_issues)
