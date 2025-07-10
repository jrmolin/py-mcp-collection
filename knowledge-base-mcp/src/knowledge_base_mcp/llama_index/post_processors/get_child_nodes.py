from logging import Logger
from typing import override

from llama_index.core.bridge.pydantic import Field
from llama_index.core.postprocessor.types import BaseNodePostprocessor
from llama_index.core.schema import (
    BaseNode,
    MetadataMode,
    NodeWithScore,
    QueryBundle,
)
from llama_index.core.storage.docstore.types import BaseDocumentStore

from knowledge_base_mcp.utils.logging import BASE_LOGGER

logger: Logger = BASE_LOGGER.getChild(suffix=__name__)


def get_nodes_size(nodes: list[NodeWithScore]) -> int:
    """Get the size of the nodes."""
    return sum(len(node.node.get_content(metadata_mode=MetadataMode.NONE).strip()) for node in nodes)


class GetChildNodesPostprocessor(BaseNodePostprocessor):
    """Get the child nodes of the parent nodes."""

    doc_store: BaseDocumentStore
    """The document store to get the parent nodes from."""

    keep_parent_nodes: bool = Field(default=True)
    """Whether to keep the parent nodes in the results."""

    @classmethod
    @override
    def class_name(cls) -> str:
        return "GetChildNodesPostprocessor"

    @override
    def _postprocess_nodes(
        self,
        nodes: list[NodeWithScore],
        query_bundle: QueryBundle | None = None,
    ) -> list[NodeWithScore]:
        """Postprocess nodes."""

        childless_nodes: list[NodeWithScore] = [node for node in nodes if not node.node.child_nodes]

        parent_nodes: list[NodeWithScore] = [node for node in nodes if node.node.child_nodes]

        resultant_nodes: list[NodeWithScore] = []

        child_nodes: list[BaseNode] = self.gather_child_nodes(nodes_with_scores=parent_nodes)
        child_nodes_by_id: dict[str, BaseNode] = {child_node.node_id: child_node for child_node in child_nodes}

        for parent_node in parent_nodes:
            # Make the type-checker happy.
            if not parent_node.node.child_nodes:
                msg = "No child nodes found for the expandable node?!"
                raise ValueError(msg)

            for child_node in parent_node.node.child_nodes:
                if child_node.node_id in child_nodes_by_id:
                    new_scored_node: NodeWithScore = NodeWithScore(node=child_nodes_by_id[child_node.node_id], score=parent_node.score)
                    resultant_nodes.append(new_scored_node)

            if self.keep_parent_nodes:
                resultant_nodes.append(parent_node)

        return resultant_nodes + childless_nodes

    def gather_child_nodes(self, nodes_with_scores: list[NodeWithScore]) -> list[BaseNode]:
        """Get the deduplicated set of child nodes for the given nodes."""

        child_nodes_ids: set[str] = {
            child_node.node_id for node in nodes_with_scores if node.node.child_nodes for child_node in node.node.child_nodes
        }

        new_child_nodes: list[BaseNode] = self.doc_store.get_nodes(node_ids=list(child_nodes_ids))

        return new_child_nodes
