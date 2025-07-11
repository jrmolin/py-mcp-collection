from typing import Any

from llama_index.vector_stores.duckdb import DuckDBVectorStore


class EnhancedDuckDBVectorStore(DuckDBVectorStore):
    def __init__(
        self,
        database_name: str = ":memory:",
        table_name: str = "documents",
        embed_dim: int = 384,
        text_search_config: dict[str, Any] | None = None,
        persist_dir: str = "./storage",
        **kwargs: Any,  # pyright: ignore[reportAny]
    ) -> None:
        super().__init__(  # pyright: ignore[reportUnknownMemberType]
            database_name=database_name,
            table_name=table_name,
            embed_dim=embed_dim,
            text_search_config=text_search_config,
            persist_dir=persist_dir,
            **kwargs,
        )

    async def metadata_agg(self, key: str) -> dict[str, int]:
        """
        Get the unique values for a metadata key in the index
        """

        # fetching the table description to ensure the table is initialized
        _ = self.table.description

        command = f"""
            SELECT json_extract_string(metadata_, '$.{key}') as kb, count(*) as count FROM documents
            WHERE metadata_.{key} IS NOT NULL
            GROUP BY json_extract_string(metadata_, '$.{key}')
            ORDER BY kb ASC;
            """  # noqa: S608

        results = self.client.execute(query=command).fetchall()

        return dict(results)
