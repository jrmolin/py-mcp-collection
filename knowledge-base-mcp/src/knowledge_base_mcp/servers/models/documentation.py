from collections import defaultdict

from llama_index.core.schema import BaseNode, MetadataMode, NodeWithScore
from pydantic import BaseModel, Field, RootModel


class TitleResult(BaseModel):
    """A result from a search query"""

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
                heading = node.node.metadata.get("headings", "<no heading>")

                node_text = node.get_content(metadata_mode=MetadataMode.NONE).strip()

                by_heading[heading].append(node_text)

            results[title] = TitleResult(source=these_nodes[0].node.metadata.get("source", "<no source>"), headings=by_heading)

        return results


class KnowledgeBaseResult(RootModel[dict[str, TitleResult]]):
    """A result from a search query"""

    root: dict[str, TitleResult] = Field(description="The results of the search by document")

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

            results[knowledge_base] = KnowledgeBaseResult(root=by_title)

        return results


# class TreeSearchResponse(BaseModel):
#     """A response to a search query"""

#     query: str = Field(description="The query that was used to search the knowledge base")
#     knowledge_bases: dict[str, KnowledgeBaseResult] = Field(description="The knowledge bases that had results")

#     @classmethod
#     def from_nodes(cls, query: str, nodes: list[NodeWithScore]) -> "TreeSearchResponse":
#         """Convert a list of nodes to a search response"""

#         results = KnowledgeBaseResult.from_nodes(nodes)

#         return cls(query=query, knowledge_bases=results)


class TreeSearchResponse(RootModel[dict[str, KnowledgeBaseResult]]):
    """A response to a search query"""

    root: dict[str, KnowledgeBaseResult] = Field(description="The knowledge bases that had results")

    @classmethod
    def from_nodes(cls, nodes: list[NodeWithScore]) -> "TreeSearchResponse":
        """Convert a list of nodes to a search response"""

        results = KnowledgeBaseResult.from_nodes(nodes)

        return cls(root=results)


class DocumentResponse(BaseModel):
    """A response to a document request"""

    source: str = Field(description="The source of the document")
    title: str = Field(description="The title of the document")
    content: str = Field(description="The content of the document")

    @classmethod
    def from_node(cls, node: BaseNode) -> "DocumentResponse":
        """Convert a node to a document response"""
        return cls(
            source=node.metadata.get("source", "<no source>"),  #  pyright: ignore[reportAny]
            title=node.metadata.get("title", "<no title>"),  #  pyright: ignore[reportAny]
            content=node.get_content(metadata_mode=MetadataMode.NONE).strip(),
        )
