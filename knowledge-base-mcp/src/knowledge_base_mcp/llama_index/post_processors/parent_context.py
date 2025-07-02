from collections import defaultdict
from logging import Logger
from typing import TYPE_CHECKING, override

from llama_index.core.bridge.pydantic import Field
from llama_index.core.postprocessor.types import BaseNodePostprocessor
from llama_index.core.schema import BaseNode, MetadataMode, NodeWithScore, QueryBundle
from llama_index.core.storage.docstore.types import BaseDocumentStore

from knowledge_base_mcp.utils.logging import BASE_LOGGER

logger: Logger = BASE_LOGGER.getChild(suffix=__name__)

if TYPE_CHECKING:
    from collections.abc import Sequence


class ParentContextNodePostprocessor(BaseNodePostprocessor):
    doc_store: BaseDocumentStore
    """The document store to get the parent nodes from."""

    threshold: float = Field(default=0.5)
    """The % of a parent node that must be present in the results to bring it in."""

    minimum_size: int = Field(default=1024)
    """The minimum size of the parent node to bring in."""

    maximum_size: int = Field(default=4096)
    """The maximum size of the parent node to bring in."""

    @classmethod
    @override
    def class_name(cls) -> str:
        return "ParentContextNodePostprocessor"

    @override
    def _postprocess_nodes(
        self,
        nodes: list[NodeWithScore],
        query_bundle: QueryBundle | None = None,
    ) -> list[NodeWithScore]:
        """Postprocess nodes."""

        nodes_by_parent_id: dict[str, list[NodeWithScore]] = defaultdict(list)

        for node in nodes:
            if parent_node := node.node.parent_node:
                nodes_by_parent_id[parent_node.node_id].append(node)

        candidate_parent_nodes: Sequence[BaseNode] = self.doc_store.get_nodes(node_ids=list(nodes_by_parent_id.keys()))

        logger.info(f"Found {len(candidate_parent_nodes)} candidate parent nodes")

        new_nodes: list[NodeWithScore] = nodes.copy()

        for candidate_parent_node in candidate_parent_nodes:
            if not candidate_parent_node.child_nodes:
                continue

            scored_children = nodes_by_parent_id[candidate_parent_node.node_id]

            if len(scored_children) / len(candidate_parent_node.child_nodes) < self.threshold:
                continue

            if len(candidate_parent_node.get_content(metadata_mode=MetadataMode.LLM)) > self.maximum_size:
                continue

            logger.info(f"Adding parent node {candidate_parent_node.node_id} to results")

            average_score = sum(node.score or 0 for node in scored_children) / len(scored_children)

            [new_nodes.remove(node) for node in scored_children]

            new_nodes.append(NodeWithScore(node=candidate_parent_node, score=average_score))

        return new_nodes
