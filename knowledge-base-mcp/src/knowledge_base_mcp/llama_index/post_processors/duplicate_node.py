from typing import override

from llama_index.core.postprocessor.types import BaseNodePostprocessor
from llama_index.core.schema import NodeWithScore, QueryBundle


class DuplicateNodePostprocessor(BaseNodePostprocessor):
    """Duplicate Node processor."""

    @classmethod
    @override
    def class_name(cls) -> str:
        return "DuplicateNodePostprocessor"

    @override
    def _postprocess_nodes(
        self,
        nodes: list[NodeWithScore],
        query_bundle: QueryBundle | None = None,
    ) -> list[NodeWithScore]:
        """Postprocess nodes."""

        ids: set[str] = set()
        hashes: set[str] = set()

        new_nodes: list[NodeWithScore] = []

        for node in nodes:
            if node.node_id in ids:
                continue

            if node.node.hash in hashes:
                continue

            ids.add(node.node_id)
            hashes.add(node.node.hash)

            new_nodes.append(node)

        return new_nodes
