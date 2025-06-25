from typing import Literal

from llama_index.core.bridge.pydantic import Field
from llama_index.core.postprocessor.types import BaseNodePostprocessor
from llama_index.core.schema import NodeRelationship, NodeWithScore, QueryBundle, RelatedNodeInfo
from llama_index.core.vector_stores.types import BasePydanticVectorStore


class VectorPrevNextNodePostprocessor(BaseNodePostprocessor):
    vector_store: BasePydanticVectorStore
    num_nodes: int = Field(default=3)
    mode: Literal["next", "previous", "both"] = Field(default="next")

    @classmethod
    def class_name(cls) -> str:
        return "VectorPrevNextNodePostprocessor"

    def _postprocess_nodes(
        self,
        nodes: list[NodeWithScore],
        query_bundle: QueryBundle | None = None,  # noqa: ARG002
    ) -> list[NodeWithScore]:
        """Postprocess nodes."""

        sibling_nodes = self._get_sibling_nodes(nodes, self.num_nodes, self.mode)

        return self._order_nodes(nodes, sibling_nodes)

    def _get_sibling_nodes(self, nodes_with_scores: list[NodeWithScore], num_nodes: int = 3, mode: str = "both") -> list[NodeWithScore]:
        """For each node, we will get its before and after nodes iteratively until we have the number of sibling nodes that we need.
        We will then return the list of the original nodes plus the nodes that we have fetched."""

        fetched_nodes: list[NodeWithScore] = nodes_with_scores.copy()

        for _ in range(num_nodes):
            fetched_nodes_ids = [node.node_id for node in fetched_nodes]
            node_ids_to_fetch: set[str] = set()

            before_node_ids = self._get_before_node_ids(fetched_nodes) if mode in {"previous", "both"} else []
            after_node_ids = self._get_after_node_ids(fetched_nodes) if mode in {"next", "both"} else []

            node_ids_to_fetch.update(before_node_ids)
            node_ids_to_fetch.update(after_node_ids)
            node_ids_to_fetch.difference_update(fetched_nodes_ids)

            if len(node_ids_to_fetch) == 0:
                break

            nodes = self.vector_store.get_nodes(node_ids=list(node_ids_to_fetch))
            fetched_nodes.extend([NodeWithScore(node=node) for node in nodes])

        return fetched_nodes

    def _order_nodes(
        self,
        nodes_with_scores: list[NodeWithScore],
        all_nodes: list[NodeWithScore],
    ) -> list[NodeWithScore]:
        """Order nodes by their relationships to their sibling nodes."""
        sorted_nodes = []

        for node_with_score in nodes_with_scores:
            before_nodes = self._walk_before_nodes(node_with_score, all_nodes)
            after_nodes = self._walk_after_nodes(node_with_score, all_nodes)

            sorted_nodes.extend([*before_nodes, node_with_score, *after_nodes])

        return sorted_nodes

    def _get_before_node_ids(self, nodes_with_scores: list[NodeWithScore]) -> list[str]:
        """Get the before node ids for a list of nodes."""
        before_node_ids: list[str] = []

        for node in nodes_with_scores:
            before_node_id = self._get_before_node_id(node)
            if before_node_id is not None:
                before_node_ids.append(before_node_id)

        return before_node_ids

    def _get_after_node_ids(self, nodes_with_scores: list[NodeWithScore]) -> list[str]:
        """Get the after node ids for a list of nodes."""
        after_node_ids: list[str] = []
        for node in nodes_with_scores:
            after_node_id = self._get_after_node_id(node)
            if after_node_id is not None:
                after_node_ids.append(after_node_id)

        return after_node_ids

    def _get_before_node_id(self, node: NodeWithScore) -> str | None:
        """Get the node id from the node stub in the relationships for a node."""
        before_node_relationship = node.node.relationships.get(NodeRelationship.PREVIOUS, None)
        if isinstance(before_node_relationship, RelatedNodeInfo):
            return before_node_relationship.node_id

        return None

    def _get_after_node_id(self, node: NodeWithScore) -> str | None:
        """Get the node id from the node stub in the relationships for a node."""
        after_node_relationship = node.node.relationships.get(NodeRelationship.NEXT, None)
        if isinstance(after_node_relationship, RelatedNodeInfo):
            return after_node_relationship.node_id

        return None

    def _get_before_node(self, node: NodeWithScore, sibling_nodes: list[NodeWithScore]) -> NodeWithScore | None:
        """Get the real node from the list of sibling nodes that is the before node."""
        before_node_id = self._get_before_node_id(node)
        if before_node_id is None:
            return None
        return next((node for node in sibling_nodes if node.node_id == before_node_id), None)

    def _get_after_node(self, node: NodeWithScore, sibling_nodes: list[NodeWithScore]) -> NodeWithScore | None:
        """Get the real node from the list of sibling nodes that is the after node."""
        after_node_id = self._get_after_node_id(node)
        if after_node_id is None:
            return None
        return next((node for node in sibling_nodes if node.node_id == after_node_id), None)

    def _walk_before_nodes(self, node_with_score: NodeWithScore, all_nodes: list[NodeWithScore], num_nodes: int = 3) -> list[NodeWithScore]:
        """Walk the before node ids for a node, starting from the node and going backwards."""
        starting_node = node_with_score
        before_nodes: list[NodeWithScore] = []

        for _ in range(num_nodes):
            before_node = self._get_before_node(starting_node, all_nodes)
            if before_node is not None:
                before_nodes.insert(0, before_node)

            starting_node = self._get_before_node(starting_node, all_nodes)
            if starting_node is None:
                break

        return before_nodes

    def _walk_after_nodes(self, node_with_score: NodeWithScore, all_nodes: list[NodeWithScore], num_nodes: int = 3) -> list[NodeWithScore]:
        """Walk the after node ids for a node, starting from the node and going forwards."""
        starting_node = node_with_score
        after_nodes: list[NodeWithScore] = []

        for _ in range(num_nodes):
            after_node = self._get_after_node(starting_node, all_nodes)
            if after_node is not None:
                after_nodes.append(after_node)

            starting_node = self._get_after_node(starting_node, all_nodes)
            if starting_node is None:
                break

        return after_nodes
