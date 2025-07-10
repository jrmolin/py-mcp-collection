from typing import ClassVar, override

from llama_index.core.bridge.pydantic import Field
from llama_index.core.postprocessor.types import BaseNodePostprocessor
from llama_index.core.schema import NodeWithScore, QueryBundle
from pydantic import ConfigDict


class RemoveDuplicateNodesPostprocessor(BaseNodePostprocessor):
    """Remove duplicate nodes."""

    model_config: ClassVar[ConfigDict] = ConfigDict(use_attribute_docstrings=True)
    """The model config."""

    by_id: bool = Field(default=True)
    """Whether to remove duplicate nodes by their id."""

    by_hash: bool = Field(default=True)
    """Whether to remove duplicate nodes by their hash."""

    by_metadata_key: str | None = Field(default=None)
    """Whether to remove duplicate nodes by a metadata key."""

    # by_embeddings: bool = Field(default=True)
    # """Whether to remove duplicate nodes by their embeddings."""

    @classmethod
    @override
    def class_name(cls) -> str:
        return "RemoveDuplicateNodesPostprocessor"

    @override
    def _postprocess_nodes(
        self,
        nodes: list[NodeWithScore],
        query_bundle: QueryBundle | None = None,
    ) -> list[NodeWithScore]:
        """Postprocess nodes."""

        ids: set[str] = set()
        hashes: set[str] = set()
        metadata_values: set[str] = set()
        # embeddings: set[list[float]] = set()

        new_nodes: list[NodeWithScore] = []

        for node in nodes:
            if self.by_id:
                if node.node_id in ids:
                    continue

                ids.add(node.node_id)

            if self.by_hash:
                if node.node.hash in hashes:
                    continue

                hashes.add(node.node.hash)

            if self.by_metadata_key:
                if str(node.node.metadata.get(self.by_metadata_key)) in metadata_values:
                    continue

                metadata_values.add(str(node.node.metadata.get(self.by_metadata_key)))

            # if self.by_embeddings:
            #     if not node.embedding or node.embedding in embeddings:
            #         continue

            #     embeddings.add(node.embedding)

            new_nodes.append(node)

        return new_nodes
