from collections.abc import Sequence
from logging import Logger
from typing import Any, ClassVar, override

from llama_index.core.schema import (
    BaseNode,
    TransformComponent,
)
from llama_index.core.storage.docstore import BaseDocumentStore
from pydantic import ConfigDict

from knowledge_base_mcp.utils.logging import BASE_LOGGER

logger: Logger = BASE_LOGGER.getChild(__name__)


class WriteToDocstore(TransformComponent):
    """Write documents and nodes to the doc store."""

    docstore: BaseDocumentStore

    model_config: ClassVar[ConfigDict] = ConfigDict(use_attribute_docstrings=True, arbitrary_types_allowed=True)

    @override
    def __call__(self, nodes: Sequence[BaseNode], **kwargs: Any) -> Sequence[BaseNode]:  # pyright: ignore[reportAny]
        """Embed the leaf nodes."""

        self.docstore.add_documents(docs=nodes, allow_update=True)

        return nodes

    @override
    async def acall(self, nodes: Sequence[BaseNode], **kwargs: Any) -> Sequence[BaseNode]:  # pyright: ignore[reportAny]
        """Async embed the leaf nodes."""

        await self.docstore.async_add_documents(docs=nodes, allow_update=True)

        return nodes
