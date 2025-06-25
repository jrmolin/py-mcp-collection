from collections import defaultdict

from llama_index.core.schema import NodeWithScore
from pydantic import BaseModel, Field, RootModel


class TitleResult(BaseModel):
    """A result from a search query"""

    title: str = Field(description="The title of the result", exclude=True)
    source: str = Field(description="The source of the result")
    headings: dict[str, list[str]] = Field(description="The results of the search by heading")

    @classmethod
    def from_nodes(cls, nodes: list[NodeWithScore]) -> dict[str, "TitleResult"]:
        """Convert a list of nodes with the same title to a search response"""
        results: dict[str, TitleResult] = {}

        nodes_by_title: dict[str, list[NodeWithScore]] = defaultdict(list)

        for node in nodes:
            title = node.node.metadata.get("title", "<no title>")
            nodes_by_title[title].append(node)

        for title, these_nodes in nodes_by_title.items():
            by_heading: dict[str, list[str]] = defaultdict(list)

            for node in these_nodes:
                heading = node.node.metadata.get("heading", "<no heading>")
                by_heading[heading].append(node.text.strip())

            results[title] = TitleResult(title=title, source=these_nodes[0].node.metadata.get("source", "<no source>"), headings=by_heading)

        return results


class KnowledgeBaseResult(BaseModel):
    """A result from a search query"""

    name: str = Field(description="The name of the knowledge base", exclude=True)
    documents: dict[str, TitleResult] = Field(description="The results of the search by document")

    @classmethod
    def from_nodes(cls, nodes: list[NodeWithScore]) -> dict[str, "KnowledgeBaseResult"]:
        """Convert a list of nodes to a search response"""

        results: dict[str, KnowledgeBaseResult] = {}

        nodes_by_knowledge_base: dict[str, list[NodeWithScore]] = defaultdict(list)

        for node in nodes:
            knowledge_base = node.node.metadata.get("knowledge_base", "<no knowledge base>")
            nodes_by_knowledge_base[knowledge_base].append(node)

        for knowledge_base, kb_nodes in nodes_by_knowledge_base.items():
            by_title: dict[str, TitleResult] = TitleResult.from_nodes(kb_nodes)

            results[knowledge_base] = KnowledgeBaseResult(name=knowledge_base, documents=by_title)

        return results


class KnowledgeBaseSummary(RootModel):
    """A high level summary of relevant documents across all knowledge bases"""

    root: dict[str, int] = Field(default_factory=dict, description="The number of documents in each knowledge base")

    @classmethod
    def from_nodes(cls, nodes: list[NodeWithScore]) -> "KnowledgeBaseSummary":
        """Convert a list of nodes to a summary"""
        results: dict[str, int] = {}

        for node in nodes:
            knowledge_base = node.node.metadata.get("knowledge_base", "<no knowledge base>")
            results[knowledge_base] = results.get(knowledge_base, 0) + 1

        return cls(root=results)


class TreeSearchResponse(BaseModel):
    """A response to a search query"""

    query: str = Field(description="The query that was used to search the knowledge base")
    knowledge_bases: dict[str, KnowledgeBaseResult] = Field(description="The knowledge bases that had results")

    @classmethod
    def from_nodes(cls, query: str, nodes: list[NodeWithScore]) -> "TreeSearchResponse":
        """Convert a list of nodes to a search response"""

        results = KnowledgeBaseResult.from_nodes(nodes)

        return cls(query=query, knowledge_bases=results)


class SearchResponseWithSummary(BaseModel):
    """A response to a search query with a summary"""

    query: str = Field(description="The query that was used to search the knowledge base")
    summary: KnowledgeBaseSummary = Field(description="The summary of the search")
    results: TreeSearchResponse = Field(description="The results of the search")
