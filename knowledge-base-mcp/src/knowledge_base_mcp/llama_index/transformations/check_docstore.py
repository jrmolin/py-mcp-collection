from collections.abc import Sequence
from logging import Logger
from typing import Any, ClassVar, override

from llama_index.core.schema import (
    BaseNode,
    TransformComponent,
)
from llama_index.core.storage.docstore import BaseDocumentStore
from pydantic import ConfigDict, PrivateAttr

from knowledge_base_mcp.utils.logging import BASE_LOGGER

logger: Logger = BASE_LOGGER.getChild(__name__)


class CheckDocstore(TransformComponent):
    """Write documents and nodes to the doc store."""

    docstore: BaseDocumentStore

    model_config: ClassVar[ConfigDict] = ConfigDict(use_attribute_docstrings=True, arbitrary_types_allowed=True)

    _doc_hash_to_id: dict[str, str] = PrivateAttr(default_factory=dict)

    def load_hashes(self) -> None:
        """Load the hashes from the docstore."""
        self._doc_hash_to_id = self.docstore.get_all_document_hashes()

    async def aload_hashes(self) -> None:
        """Load the hashes from the docstore."""
        self._doc_hash_to_id = await self.docstore.aget_all_document_hashes()

    def check_doc_hash(self, doc_hash: str) -> bool:
        """Check if the hash is in the docstore."""

        return doc_hash in self._doc_hash_to_id

    def check_nodes(self, nodes: Sequence[BaseNode]) -> Sequence[BaseNode]:
        """Check if the nodes are in the docstore."""

        _skipped_node_hashes: set[str] = set()
        _skipped_source_node_hashes: set[str] = set()

        list_of_nodes: list[BaseNode] = []

        for node in nodes:
            # Check the source node's (origin document) hash
            if node.source_node and node.source_node.hash:  # noqa: SIM102
                if self.check_doc_hash(doc_hash=node.source_node.hash):
                    if node.source_node.hash not in _skipped_source_node_hashes:
                        _skipped_source_node_hashes.add(node.source_node.hash)
                        logger.warning(f"Source document {node.source_node.hash} already exists in docstore, skipping")

                    continue

            # Check the hash of the node itself
            if self.check_doc_hash(doc_hash=node.hash):
                if node.hash not in _skipped_node_hashes:
                    _skipped_node_hashes.add(node.hash)
                    logger.warning(f"Node {node.hash} already exists in docstore, skipping")

                continue

            list_of_nodes.append(node)

        return list_of_nodes

    @override
    def __call__(self, nodes: Sequence[BaseNode], **kwargs: Any) -> Sequence[BaseNode]:  # pyright: ignore[reportAny]
        """Embed the leaf nodes."""

        if not self._doc_hash_to_id:
            self.load_hashes()

        return self.check_nodes(nodes=nodes)

    @override
    async def acall(self, nodes: Sequence[BaseNode], **kwargs: Any) -> Sequence[BaseNode]:  # pyright: ignore[reportAny]
        """Async embed the leaf nodes."""

        if not self._doc_hash_to_id:
            await self.aload_hashes()

        return self.check_nodes(nodes=nodes)
