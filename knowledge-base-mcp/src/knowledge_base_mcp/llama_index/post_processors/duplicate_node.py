from llama_index.core.postprocessor.types import BaseNodePostprocessor
from llama_index.core.schema import NodeWithScore, QueryBundle


class DuplicateNodePostprocessor(BaseNodePostprocessor):
    """Duplicate Node processor."""

    @classmethod
    def class_name(cls) -> str:
        return "DuplicateNodePostprocessor"

    def _postprocess_nodes(
        self,
        nodes: list[NodeWithScore],
        query_bundle: QueryBundle | None = None,  # noqa: ARG002
    ) -> list[NodeWithScore]:
        """Postprocess nodes."""

        ids: set[str] = set()

        new_nodes: list[NodeWithScore] = []

        for node in nodes:
            if node.node_id in ids:
                continue

            ids.add(node.node_id)
            new_nodes.append(node)

        return new_nodes
