from collections.abc import Sequence
from logging import Logger
from typing import Any, ClassVar, override

from llama_index.core.schema import (
    BaseNode,
    Document,
    TransformComponent,
)
from llama_index.core.storage.docstore.types import BaseDocumentStore
from pydantic import ConfigDict

from knowledge_base_mcp.utils.logging import BASE_LOGGER

logger: Logger = BASE_LOGGER.getChild(__name__)


class AddToDocstore(TransformComponent):
    """Adds nodes to the docstore."""

    model_config: ClassVar[ConfigDict] = ConfigDict(use_attribute_docstrings=True, arbitrary_types_allowed=True)

    docstore: BaseDocumentStore
    """The docstore to add nodes to."""

    def _filter_for_documents(self, nodes: Sequence[BaseNode]) -> list[Document]:
        """Filter for documents."""
        return [node for node in nodes if isinstance(node, Document)]

    @override
    def __call__(self, nodes: Sequence[BaseNode], **kwargs: Any) -> Sequence[BaseNode]:  # pyright: ignore[reportAny]
        """Add documents to the docstore."""

        if documents := self._filter_for_documents(nodes=nodes):
            self.docstore.add_documents(docs=documents)

        return nodes

    @override
    async def acall(self, nodes: Sequence[BaseNode], **kwargs: Any) -> Sequence[BaseNode]:  # pyright: ignore[reportAny]
        """Add documents to the docstore."""

        if documents := self._filter_for_documents(nodes=nodes):
            await self.docstore.async_add_documents(docs=documents)

        return nodes
