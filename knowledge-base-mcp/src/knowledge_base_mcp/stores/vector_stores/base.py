from typing import Protocol, runtime_checkable

from llama_index.core.schema import BaseNode
from llama_index.core.vector_stores.types import MetadataFilters, VectorStore


@runtime_checkable
class EnhancedBaseVectorStore(VectorStore, Protocol):
    """An enhanced vector store."""

    async def metadata_agg(self, key: str) -> dict[str, int]: ...

    def get_nodes(self, node_ids: list[str] | None = None, filters: MetadataFilters | None = None) -> list[BaseNode]: ...

    def clear(self) -> None: ...

    async def aclear(self) -> None: ...

    # def as_pydantic(self) -> BasePydanticVectorStore:
    #     if not isinstance(self, BasePydanticVectorStore):
    #         msg = "Vector store must be a BasePydanticVectorStore"
    #         raise TypeError(msg)

    #     return self
