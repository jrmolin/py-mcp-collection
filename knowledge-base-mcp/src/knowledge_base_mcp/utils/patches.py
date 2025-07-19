import json
from collections import defaultdict
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from datetime import UTC, datetime
from logging import Logger
from typing import Any, Self

from llama_index.core.indices.vector_store import retrievers
from llama_index.core.ingestion import pipeline
from llama_index.core.ingestion.cache import IngestionCache
from llama_index.core.ingestion.pipeline import get_transformation_hash
from llama_index.core.schema import (
    BaseNode,
    Document,
    TransformComponent,
)
from llama_index.core.vector_stores import utils
from pydantic import BaseModel, Field, PrivateAttr, computed_field

from knowledge_base_mcp.utils.logging import BASE_LOGGER
from knowledge_base_mcp.vendored.retrievers.retrieve import VectorIndexRetriever

logger: Logger = BASE_LOGGER.getChild(__name__)


class RunningTimer(BaseModel):
    name: str
    start_time: datetime = Field(default_factory=lambda: datetime.now(tz=UTC), exclude=True)

    def stop(self) -> "FinishedTimer":
        return FinishedTimer(name=self.name, start_time=self.start_time)


class Timer(RunningTimer):
    pass


class FinishedTimer(RunningTimer):
    end_time: datetime = Field(default_factory=lambda: datetime.now(tz=UTC), exclude=True)

    @computed_field()
    @property
    def duration(self) -> float:
        return (self.end_time - self.start_time).total_seconds()


class TimerGroup(BaseModel):
    name: str = Field(description="The name of the timer group")

    _running_timer: RunningTimer | None = PrivateAttr(default=None)
    _finished_timers: list[FinishedTimer] = PrivateAttr(default_factory=list)

    def start_timer(self, name: str) -> Self:
        if self._running_timer is not None:
            msg = f"A timer is already running for {name}"
            raise ValueError(msg)

        new_timer = RunningTimer(name=name)
        self._running_timer = new_timer

        return self

    @contextmanager
    def time(self, name: str) -> Iterator[None]:
        _ = self.start_timer(name)
        yield
        _ = self.stop_timer()

    def stop_timer(self) -> Self:
        if self._running_timer is None:
            msg = f"No running timer found for {self.name}"
            raise ValueError(msg)

        self._finished_timers.append(self._running_timer.stop())
        self._running_timer = None

        return self

    def merge(self, other: "TimerGroup") -> Self:
        """Merge another timer group into this one."""

        self._finished_timers.extend(other._finished_timers)
        return self

    @computed_field()
    @property
    def times(self) -> dict[str, float]:
        if not self._finished_timers:
            return {}

        timers_by_name: dict[str, float] = defaultdict(float)

        for timer in self._finished_timers:
            timers_by_name[timer.name] += timer.duration

        return timers_by_name

    @computed_field()
    @property
    def total_duration(self) -> float:
        return sum(self.times.values())

    def wall_clock_time(self) -> float:
        if not self._finished_timers:
            return 0

        minimum_start_time = min(timer.start_time for timer in self._finished_timers)
        maximum_end_time = max(timer.end_time for timer in self._finished_timers)

        return (maximum_end_time - minimum_start_time).total_seconds()


async def arun_transformations(
    nodes: Sequence[BaseNode],
    transformations: Sequence[TransformComponent],
    in_place: bool = True,
    cache: IngestionCache | None = None,
    cache_collection: str | None = None,
    **kwargs: Any,  # pyright: ignore[reportAny]
) -> Sequence[BaseNode]:
    """
    Run a series of transformations on a set of nodes.

    Args:
        nodes: The nodes to transform.
        transformations: The transformations to apply to the nodes.

    Returns:
        The transformed nodes.

    """
    if not in_place:
        nodes = list(nodes)

    starting_nodes = len(nodes)
    timer_group = TimerGroup(name="arun_transformations")

    starting_document_count = len([node for node in nodes if isinstance(node, Document)])
    starting_node_count = len([node for node in nodes if not isinstance(node, Document)])

    node_counts: list[int] = [starting_node_count]
    document_counts: list[int] = [starting_document_count]

    transform_type = "doc -> node" if starting_document_count > 0 else "node -> node"
    if len(nodes) > 1:
        suffix = f"({starting_document_count} documents and {starting_node_count} nodes)"
        logger.info(f"Running {len(transformations)} {transform_type} transformations on {starting_nodes} nodes {suffix}")

    for transform in transformations:
        _ = timer_group.start_timer(name=transform.__class__.__name__)

        if cache is not None:
            hash = get_transformation_hash(nodes, transform)  # noqa: A001

            cached_nodes = cache.get(hash, collection=cache_collection)
            if cached_nodes is not None:
                nodes = cached_nodes
            else:
                nodes = await transform.acall(nodes, **kwargs)
                cache.put(hash, nodes, collection=cache_collection)
        else:
            nodes = await transform.acall(nodes, **kwargs)

        node_counts.append(len([node for node in nodes if not isinstance(node, Document)]))

        _ = timer_group.stop_timer()

    node_str = "Nodes" + " -> ".join([f"({count})" for count in node_counts])
    document_str = "Documents" + " -> ".join([f"({count})" for count in document_counts])

    if len(nodes) > 1:
        logger.info(f"Completed {transform_type} transformations: {node_str} | {document_str} in {timer_group.model_dump()}")

    return nodes


def node_to_metadata_dict(
    node: BaseNode,
    remove_text: bool = False,
    text_field: str = utils.DEFAULT_TEXT_KEY,
    text_resource_field: str = utils.DEFAULT_TEXT_RESOURCE_KEY,
    flat_metadata: bool = False,
) -> dict[str, Any]:
    """Common logic for saving Node data into metadata dict."""
    # Using mode="json" here because BaseNode may have fields of type bytes (e.g. images in ImageBlock),
    # which would cause serialization issues.
    node_dict = node.model_dump(mode="json")
    metadata: dict[str, Any] = node_dict.get("metadata", {})  # pyright: ignore[reportAny]

    if flat_metadata:
        utils._validate_is_flat_dict(metadata)  # pyright: ignore[reportUnknownMemberType, reportPrivateUsage]

    # store entire node as json string - some minor text duplication
    if remove_text and text_field in node_dict:
        node_dict[text_field] = ""
    if remove_text and text_resource_field in node_dict:
        del node_dict[text_resource_field]

    # remove embedding from node_dict
    node_dict["embedding"] = None

    # dump remainder of node_dict to json string
    metadata["_node_content"] = json.dumps(node_dict)
    metadata["_node_type"] = node.class_name()

    # store ref doc id at top level to allow metadata filtering
    # kept for backwards compatibility, will consolidate in future
    metadata["document_id"] = node.ref_doc_id or "None"  # for Chroma
    metadata["doc_id"] = node.ref_doc_id or "None"  # for Pinecone, Qdrant, Redis
    metadata["ref_doc_id"] = node.ref_doc_id or "None"  # for Weaviate

    return metadata


def apply_patches() -> None:
    """Apply the patches to the pipeline."""
    pipeline.arun_transformations = arun_transformations

    # TODO: Remove this once https://github.com/run-llama/llama_index/pull/19388 is merged
    utils.node_to_metadata_dict = node_to_metadata_dict

    retrievers.VectorIndexRetriever = VectorIndexRetriever
