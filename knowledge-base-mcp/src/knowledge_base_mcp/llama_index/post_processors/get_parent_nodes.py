from collections import defaultdict
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


def get_scored_nodes_size(nodes: list[NodeWithScore]) -> int:
    """Get the size of the nodes."""
    return sum(len(node.node.get_content(metadata_mode=MetadataMode.NONE).strip()) for node in nodes)


def get_nodes_size(nodes: list[BaseNode]) -> int:
    """Get the size of the nodes."""
    return sum(len(node.get_content(metadata_mode=MetadataMode.NONE).strip()) for node in nodes)


class GetParentNodesPostprocessor(BaseNodePostprocessor):
    """Get the parent nodes of the child nodes."""

    doc_store: BaseDocumentStore
    """The document store to get the parent nodes from."""

    keep_child_nodes: bool = Field(default=False)
    """Whether to keep the child nodes in the results."""

    minimum_coverage: float = Field(default=0.0)
    """The % of a parent node that must be present in the results to bring the parent node in."""

    minimum_size: int | None = Field(default=None)
    """If the parent node is smaller than this, bring it in regardless of the minimum coverage."""

    maximum_size: int | None = Field(default=None)
    """The maximum size of the parent node to bring in."""

    @classmethod
    @override
    def class_name(cls) -> str:
        return "GetParentNodesPostprocessor"

    @override
    def _postprocess_nodes(
        self,
        nodes: list[NodeWithScore],
        query_bundle: QueryBundle | None = None,
    ) -> list[NodeWithScore]:
        """Postprocess nodes."""

        resultant_nodes: list[NodeWithScore] = []

        scored_nodes_by_id: dict[str, NodeWithScore] = {node.node_id: node for node in nodes}

        nodes_without_parents: list[NodeWithScore] = [node for node in nodes if not node.node.parent_node]

        parent_nodes: list[BaseNode] = self.gather_parent_nodes(nodes_with_scores=nodes)

        for parent_node in parent_nodes:
            if not parent_node.child_nodes:
                msg = f"No child nodes found for the parent node {parent_node.node_id}!"
                raise ValueError(msg)

            scored_children: list[NodeWithScore] = [
                scored_nodes_by_id[child_node.node_id] for child_node in parent_node.child_nodes if child_node.node_id in scored_nodes_by_id
            ]

            child_coverage = len(scored_children) / len(parent_node.child_nodes)
            parent_size = get_nodes_size(nodes=[parent_node])

            # If the child coverage is too low or the parent size is too small, skip this node.
            small_enough: bool = parent_size < (self.minimum_size or 0)
            low_coverage: bool = child_coverage < self.minimum_coverage
            too_large: bool = (parent_size > self.maximum_size) if self.maximum_size else False

            if not small_enough and (low_coverage or too_large):
                logger.debug(
                    f"Skipping parent node {parent_node.node_id} because it does not meet the minimum child coverage or size criteria."
                )
                resultant_nodes.extend(scored_children)
                continue

            # Merge the child scores into the new parent node.
            resultant_nodes.append(self.new_scored_node(parent_node=parent_node, children=scored_children))

            if self.keep_child_nodes:
                resultant_nodes.extend(scored_children)

        return resultant_nodes + nodes_without_parents

    def new_scored_node(self, parent_node: BaseNode, children: list[NodeWithScore]) -> NodeWithScore:
        """Create a new scored node from the parent node and the children."""

        scores: list[float] = [child.score for child in children if child.score is not None]

        return NodeWithScore(node=parent_node, score=sum(scores) / len(scores))

    def gather_parent_nodes(self, nodes_with_scores: list[NodeWithScore]) -> list[BaseNode]:
        """Get the deduplicated set of parent nodes for the given nodes."""

        nodes_with_parents: list[NodeWithScore] = [node for node in nodes_with_scores if node.node.parent_node]

        nodes_by_parent_id: dict[str, list[NodeWithScore]] = defaultdict(list)
        for node in nodes_with_parents:
            if node.node.parent_node:
                nodes_by_parent_id[node.node.parent_node.node_id].append(node)

        parent_nodes: list[BaseNode] = self.doc_store.get_nodes(node_ids=list(nodes_by_parent_id.keys()))

        return parent_nodes
