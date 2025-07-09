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


class ChildReplacerNodePostprocessor(BaseNodePostprocessor):
    doc_store: BaseDocumentStore
    """The document store to get the parent nodes from."""

    threshold: float = Field(default=0.25)
    """The % of a parent node that must be present in the results to bring it in."""

    keep_children: bool = Field(default=False)
    """Whether to keep the children nodes in the results."""

    maximum_size: int = Field(default=4096)
    """The maximum size of the parent node to bring in."""

    @classmethod
    @override
    def class_name(cls) -> str:
        return "ChildReplacerNodePostprocessor"

    @override
    def _postprocess_nodes(
        self,
        nodes: list[NodeWithScore],
        query_bundle: QueryBundle | None = None,
    ) -> list[NodeWithScore]:
        """Postprocess nodes."""

        completed_nodes: list[NodeWithScore] = [node for node in nodes if not node.node.parent_node]
        completed_nodes_ids: set[str] = {node.node_id for node in completed_nodes}

        expandable_nodes: list[NodeWithScore] = [node for node in nodes if node.node.parent_node]

        # If we already have the parent node, we don't need to expand it
        for node in expandable_nodes:
            if node.node.parent_node and node.node.parent_node.node_id in completed_nodes_ids:
                expandable_nodes.remove(node)

        # Get the parent nodes that we need to expand
        parent_nodes = self.gather_parents(nodes_with_scores=expandable_nodes)

        # Expand the parent nodes
        for parent_node in parent_nodes:
            child_nodes = self.get_child_nodes(parent_node=parent_node, nodes_with_scores=expandable_nodes)

            # If the parent node should be merged into the child nodes, do it
            if self.should_merge_children_into_parent(parent_node=parent_node, children=child_nodes):
                completed_nodes.append(self.merge_children_into_parent(parent_node=parent_node, children=child_nodes))

                if self.keep_children:
                    completed_nodes.extend(child_nodes)

            else:
                continue

        return completed_nodes

    def get_child_nodes(self, parent_node: BaseNode, nodes_with_scores: list[NodeWithScore]) -> list[NodeWithScore]:
        """Get the child nodes for the given parent node."""
        return [node for node in nodes_with_scores if node.node.parent_node and node.node.parent_node.node_id == parent_node.node_id]

    def merge_children_into_parent(self, parent_node: BaseNode, children: list[NodeWithScore]) -> NodeWithScore:
        """Merge the children into the parent."""

        average_score = sum(node.score or 0 for node in children) / len(children)

        return NodeWithScore(node=parent_node, score=average_score)

    def gather_parents(self, nodes_with_scores: list[NodeWithScore]) -> list[BaseNode]:
        """Get the deduplicated set of parent nodes for the given nodes."""

        parent_nodes_ids: set[str] = {node.node.parent_node.node_id for node in nodes_with_scores if node.node.parent_node}

        new_parent_nodes: list[BaseNode] = self.doc_store.get_nodes(node_ids=list(parent_nodes_ids))

        return new_parent_nodes

    def should_merge_children_into_parent(self, parent_node: BaseNode, children: list[NodeWithScore]) -> bool:
        """Determine if the children should be merged into the parent."""

        if not parent_node.child_nodes:
            return False

        if len(parent_node.get_content(metadata_mode=MetadataMode.NONE)) > self.maximum_size:
            return False

        return len(children) / len(parent_node.child_nodes) >= self.threshold
