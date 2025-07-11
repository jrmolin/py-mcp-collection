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
from llama_index.core.vector_stores.types import BasePydanticVectorStore

from knowledge_base_mcp.utils.logging import BASE_LOGGER

logger: Logger = BASE_LOGGER.getChild(suffix=__name__)


def get_nodes_size(nodes: list[NodeWithScore]) -> int:
    """Get the size of the nodes."""
    return sum(len(node.node.get_content(metadata_mode=MetadataMode.NONE).strip()) for node in nodes)


class GetSiblingNodesPostprocessor(BaseNodePostprocessor):
    """Get the sibling nodes of the given nodes. The score for the nodes is the
    average of the scores of the previous and next nodes if they exist."""

    doc_store: BaseDocumentStore
    """The document store to get the parent nodes from."""

    vector_store: BasePydanticVectorStore | None = None
    """If the vector store supports Text, we will try to use it to get the sibling nodes."""

    maximum_size: int = Field(default=1024)
    """The maximum size of the sibling node to bring in."""

    @classmethod
    @override
    def class_name(cls) -> str:
        return "GetSiblingNodesPostprocessor"

    @override
    def _postprocess_nodes(
        self,
        nodes: list[NodeWithScore],
        query_bundle: QueryBundle | None = None,
    ) -> list[NodeWithScore]:
        """Postprocess nodes."""

        expandable_nodes: list[NodeWithScore] = [node for node in nodes if node.node.prev_node or node.node.next_node]
        expandable_nodes_by_id: dict[str, NodeWithScore] = {node.node_id: node for node in expandable_nodes}

        new_nodes: list[NodeWithScore] = nodes.copy()

        sibling_nodes: list[BaseNode] = self.gather_siblings(nodes_with_scores=expandable_nodes)

        for sibling_node in sibling_nodes:
            if len(sibling_node.get_content(metadata_mode=MetadataMode.NONE).strip()) > self.maximum_size:
                continue

            sibling_nodes_scores: list[float] = []
            if sibling_node.prev_node:  # noqa: SIM102
                if prev_node := expandable_nodes_by_id.get(sibling_node.prev_node.node_id):  # noqa: SIM102
                    if prev_node.score:
                        sibling_nodes_scores.append(prev_node.score)

            if sibling_node.next_node:  # noqa: SIM102
                if next_node := expandable_nodes_by_id.get(sibling_node.next_node.node_id):  # noqa: SIM102
                    if next_node.score:
                        sibling_nodes_scores.append(next_node.score)

            if sibling_nodes_scores:
                new_nodes.append(NodeWithScore(node=sibling_node, score=sum(sibling_nodes_scores) / len(sibling_nodes_scores)))

        return new_nodes

    def gather_siblings(self, nodes_with_scores: list[NodeWithScore]) -> list[BaseNode]:
        """Get the deduplicated set of sibling nodes for the given nodes."""

        current_node_ids: set[str] = {node.node_id for node in nodes_with_scores}

        prev_sibling_nodes_ids: set[str] = {
            node.node.prev_node.node_id
            for node in nodes_with_scores
            if node.node.prev_node and node.node.prev_node.node_id not in current_node_ids
        }
        next_sibling_nodes_ids: set[str] = {
            node.node.next_node.node_id
            for node in nodes_with_scores
            if node.node.next_node and node.node.next_node.node_id not in current_node_ids
        }

        nodes_to_fetch = prev_sibling_nodes_ids | next_sibling_nodes_ids

        new_sibling_nodes: list[BaseNode] = []

        if self.vector_store and self.vector_store.stores_text:
            new_sibling_nodes = self.vector_store.get_nodes(node_ids=list(nodes_to_fetch))

        missing_nodes = nodes_to_fetch - {node.node_id for node in new_sibling_nodes}

        if missing_nodes:
            new_sibling_nodes.extend(self.doc_store.get_nodes(node_ids=list(missing_nodes)))

        return new_sibling_nodes
