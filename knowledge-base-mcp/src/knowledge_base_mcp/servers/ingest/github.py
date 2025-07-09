from collections.abc import Sequence
from functools import cached_property
from logging import Logger
from typing import Annotated, Literal, override

from fastmcp import Context
from fastmcp.tools import Tool as FastMCPTool
from llama_index.core.ingestion.pipeline import IngestionPipeline
from llama_index.core.schema import BaseNode, Node
from pydantic import Field

from knowledge_base_mcp.llama_index.readers.github import GithubIssuesReader
from knowledge_base_mcp.llama_index.transformations.metadata import AddMetadata, IncludeMetadata
from knowledge_base_mcp.servers.ingest.base import BaseIngestServer
from knowledge_base_mcp.utils.logging import BASE_LOGGER
from knowledge_base_mcp.utils.patches import apply_patches

apply_patches()


logger: Logger = BASE_LOGGER.getChild(suffix=__name__)


NewKnowledgeBaseField = Annotated[
    str,
    Field(
        description="The name of the Knowledge Base to create to store this webpage.",
        examples=["Python Language - 3.12", "Python Library - Pydantic - 2.11", "Python Library - FastAPI - 0.115"],
    ),
]


class GitHubIngestServer(BaseIngestServer):
    """A server for ingesting documentation from a GitHub repository."""

    server_name: str = "GitHub Ingest Server"

    knowledge_base_type: str = "github_issues"

    @override
    def get_tools(self) -> list[FastMCPTool]:
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

        async with self.start_rumbling() as (queue_nodes, _, ingest_result):
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
