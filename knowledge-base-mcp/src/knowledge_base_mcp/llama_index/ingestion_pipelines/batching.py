from asyncio import Queue as AsyncQueue
from collections import defaultdict
from collections.abc import AsyncIterable, AsyncIterator, Sequence
from contextlib import asynccontextmanager

from fsspec.exceptions import asyncio
from llama_index.core.bridge.pydantic import BaseModel, ConfigDict, Field, PrivateAttr
from llama_index.core.constants import (
    DEFAULT_PIPELINE_NAME,
)
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.readers.base import ReaderConfig
from llama_index.core.schema import (
    BaseNode,
    Document,
)

from knowledge_base_mcp.utils.logging import BASE_LOGGER
from knowledge_base_mcp.utils.timer import Timer, TimerGroup

logger = BASE_LOGGER.getChild(__name__)


class LazyAsyncReaderConfig(ReaderConfig):
    async def aread(self) -> AsyncIterator[Document]:
        """Read the data lazily."""
        iterable: AsyncIterable[Document] = self.reader.alazy_load_data()  # type: ignore

        async for item in iterable:
            read_timer = Timer(name="read")
            yield item
            logger.info(f"Read a document: {read_timer.stop().model_dump()}")


class PipelineGroup(BaseModel):
    """A group of pipelines."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str = Field(default=DEFAULT_PIPELINE_NAME, description="Unique name of the ingestion pipeline")

    pipelines: list[IngestionPipeline]

    _total_times: dict[str, list[float]] = PrivateAttr(default_factory=lambda: defaultdict(list))

    def print_total_times(self):
        """Print the total times for each pipeline."""
        for name, times in self._total_times.items():
            logger.info(f"Group {self.name}: {name} took {sum(times)}s")

    def _record_times(self, timer_group: TimerGroup):
        """Record the times for each pipeline."""
        for name, time in timer_group.model_dump().get("times", {}).items():
            self._total_times[name].append(time)

    async def arun(
        self, documents: Sequence[Document] | None = None, nodes: Sequence[BaseNode] | None = None, in_place: bool = True
    ) -> Sequence[BaseNode]:
        """Run the pipelines."""
        nodes, _ = await self.arun_with_timers(documents=documents, nodes=nodes, in_place=in_place)
        return nodes

    async def arun_with_timers(
        self, documents: Sequence[Document] | None = None, nodes: Sequence[BaseNode] | None = None, in_place: bool = True
    ) -> tuple[Sequence[BaseNode], TimerGroup]:
        """Run the pipelines."""

        timer_group = TimerGroup(name=self.name)

        if not nodes:
            nodes = []

        if not documents:
            documents = []

        new_nodes = [*nodes, *documents]

        for i, pipeline in enumerate(self.pipelines):
            timer_group.start_timer(name=f"Step {i + 1}: {pipeline.name}")

            new_nodes = await pipeline.arun(nodes=new_nodes, in_place=in_place)

            timer_group.stop_timer()

        self._record_times(timer_group)

        logger.info(f"Pipeline group {self.name}: {len(documents)} docs + {len(nodes)} nodes -> {len(new_nodes)} nodes")

        return new_nodes, timer_group


class PipelineStats(BaseModel):
    """A model for pipeline statistics."""

    input_nodes: int = Field(default=0, description="The number of nodes received from the input queue")
    output_nodes: int = Field(default=0, description="The number of nodes sent to the output queue")


class QueuingPipelineGroup(PipelineGroup):
    """A pipeline group which takes nodes and"""

    workers: int = Field(default=2, description="The number of workers to use")
    batch_size: int = Field(default=96, description="The number of nodes to process at a time")
    stats: PipelineStats = Field(default_factory=PipelineStats, description="The statistics for the pipeline group")

    async def _run_batch(self, batch: Sequence[BaseNode]) -> Sequence[BaseNode]:
        """Run a batch of nodes through the pipelines."""
        return await self.arun(nodes=batch)

    async def _queue_worker(
        self,
        worker_id: int,
        input_queue: AsyncQueue[Sequence[BaseNode]],
        output_queue: AsyncQueue[Sequence[BaseNode]] | None,
    ):
        """A worker which takes nodes from the incoming queue and runs them through the pipelines."""

        batch: list[BaseNode] = []

        async def run_batch():
            if not batch:
                return

            nodes: Sequence[BaseNode] = []

            try:
                nodes = await self.arun(nodes=batch)

            except Exception:
                logger.exception(f"Worker {worker_id}: Error running batch.")

            if output_queue:
                await output_queue.put(nodes)

            self.stats.output_nodes += len(nodes)

            batch.clear()

        try:
            while nodes := await input_queue.get():
                batch.extend(nodes)

                self.stats.input_nodes += len(nodes)

                input_queue.task_done()

                if len(batch) < self.batch_size:
                    continue

                await run_batch()

        except asyncio.QueueShutDown:
            logger.info(f"Worker {worker_id}: Shutting down")
            await run_batch()

    @asynccontextmanager
    async def start(self, output_queue: AsyncQueue[Sequence[BaseNode]] | None = None) -> AsyncIterator[AsyncQueue[Sequence[BaseNode]]]:
        """Start the pipeline group."""

        incoming_queue: AsyncQueue[Sequence[BaseNode]] = AsyncQueue(maxsize=self.workers)

        async with asyncio.TaskGroup() as tg:
            for i in range(self.workers):
                tg.create_task(self._queue_worker(worker_id=i, input_queue=incoming_queue, output_queue=output_queue))

            yield incoming_queue

            # We're shutting down,, so wait for the input queue to be empty
            await incoming_queue.join()

            # Shut down the queue to trigger the workers to flush their internal buffers and exit
            incoming_queue.shutdown()
