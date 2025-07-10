from logging import Logger
from typing import override

from llama_index.core.query_engine.retriever_query_engine import RetrieverQueryEngine
from llama_index.core.schema import NodeWithScore, QueryBundle

from knowledge_base_mcp.utils.logging import BASE_LOGGER
from knowledge_base_mcp.utils.patches import TimerGroup

logger: Logger = BASE_LOGGER.getChild(suffix=__name__)


class TimingRetrieverQueryEngine(RetrieverQueryEngine):
    """A retriever query engine that times the retrieval process."""

    @override
    def _apply_node_postprocessors(self, nodes: list[NodeWithScore], query_bundle: QueryBundle) -> list[NodeWithScore]:
        timer_group = TimerGroup(name="apply_node_postprocessors")
        for node_postprocessor in self._node_postprocessors:
            _ = timer_group.start_timer(f"{node_postprocessor.class_name()}: {len(nodes)}")
            nodes = node_postprocessor.postprocess_nodes(nodes, query_bundle=query_bundle)
            _ = timer_group.stop_timer()

        logger.info(f"Running apply_node_postprocessors took {timer_group.model_dump()}")

        return nodes

    @override
    def retrieve(self, query_bundle: QueryBundle) -> list[NodeWithScore]:
        timer_group = TimerGroup(name="retrieve")
        _ = timer_group.start_timer("retrieve")

        nodes = self._retriever.retrieve(query_bundle)
        _ = timer_group.stop_timer()

        _ = timer_group.start_timer("apply_node_postprocessors")
        nodes_with_scores = self._apply_node_postprocessors(nodes, query_bundle=query_bundle)
        _ = timer_group.stop_timer()

        logger.info(f"Running query '{query_bundle.query_str}' took {timer_group.model_dump()}")

        return nodes_with_scores

    @override
    async def aretrieve(self, query_bundle: QueryBundle) -> list[NodeWithScore]:
        timer_group = TimerGroup(name="aretrieve")
        _ = timer_group.start_timer("aretrieve")

        nodes = await self._retriever.aretrieve(query_bundle)
        _ = timer_group.stop_timer()

        _ = timer_group.start_timer("apply_node_postprocessors")
        nodes_with_scores = self._apply_node_postprocessors(nodes, query_bundle=query_bundle)
        _ = timer_group.stop_timer()

        logger.info(f"Running async query '{query_bundle.query_str}' took {timer_group.model_dump()}")

        return nodes_with_scores
