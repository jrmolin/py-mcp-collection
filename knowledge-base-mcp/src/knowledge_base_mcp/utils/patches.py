import asyncio
import multiprocessing
import os
import re
from logging import Logger
import warnings
from concurrent.futures import ProcessPoolExecutor
from enum import Enum
from functools import partial, reduce
from hashlib import sha256
from itertools import repeat
from pathlib import Path
from typing import Any, Generator, List, Optional, Sequence, Union

from fsspec import AbstractFileSystem

import llama_index.core.ingestion.pipeline as pipeline
from llama_index.core.constants import (
    DEFAULT_PIPELINE_NAME,
    DEFAULT_PROJECT_NAME,
)
from llama_index.core.bridge.pydantic import BaseModel, Field, ConfigDict
from llama_index.core.ingestion.cache import DEFAULT_CACHE_NAME, IngestionCache
from llama_index.core.instrumentation import get_dispatcher
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.readers.base import ReaderConfig
from llama_index.core.schema import (
    BaseNode,
    Document,
    MetadataMode,
    TransformComponent,
)
from llama_index.core.settings import Settings
from llama_index.core.storage.docstore import (
    BaseDocumentStore,
    SimpleDocumentStore,
)
from llama_index.core.storage.storage_context import DOCSTORE_FNAME
from llama_index.core.utils import concat_dirs
from llama_index.core.vector_stores.types import BasePydanticVectorStore
from knowledge_base_mcp.utils.timer import TimerGroup
from knowledge_base_mcp.utils.logging import BASE_LOGGER

logger: Logger = BASE_LOGGER.getChild(__name__)

def remove_unstable_values(s: str) -> str:
    """
    Remove unstable key/value pairs.

    Examples include:
    - <__main__.Test object at 0x7fb9f3793f50>
    - <function test_fn at 0x7fb9f37a8900>
    """
    pattern = r"<[\w\s_\. ]+ at 0x[a-z0-9]+>"
    return re.sub(pattern, "", s)


def get_transformation_hash(nodes: Sequence[BaseNode], transformation: TransformComponent) -> str:
    """Get the hash of a transformation."""
    nodes_str = "".join([str(node.get_content(metadata_mode=MetadataMode.ALL)) for node in nodes])

    transformation_dict = transformation.to_dict()
    transform_string = remove_unstable_values(str(transformation_dict))

    return sha256((nodes_str + transform_string).encode("utf-8")).hexdigest()


async def arun_transformations(
    nodes: Sequence[BaseNode],
    transformations: Sequence[TransformComponent],
    in_place: bool = True,
    cache: Optional[IngestionCache] = None,
    cache_collection: Optional[str] = None,
    **kwargs: Any,
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

    logger.info(f"Running {len(transformations)} transformations on {starting_nodes} nodes")

    for transform in transformations:
        _ = timer_group.start_timer(name=transform.__class__.__name__)

        if cache is not None:
            hash = get_transformation_hash(nodes, transform)

            cached_nodes = cache.get(hash, collection=cache_collection)
            if cached_nodes is not None:
                nodes = cached_nodes
            else:
                nodes = await transform.acall(nodes, **kwargs)
                cache.put(hash, nodes, collection=cache_collection)
        else:
            nodes = await transform.acall(nodes, **kwargs)

        timer_group.stop_timer()

    ending_nodes = len(nodes)

    logger.info(f"Completed arun_transformations {starting_nodes} -> {ending_nodes} nodes in {timer_group.model_dump()}")

    return nodes

def apply_patches() -> None:
    """Apply the patches to the pipeline."""
    pipeline.arun_transformations = arun_transformations
