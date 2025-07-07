import asyncio
from asyncio import TaskGroup
from asyncio.queues import QueueEmpty, QueueShutDown
from collections.abc import AsyncIterator, Callable, Coroutine, Sequence
from contextlib import asynccontextmanager
from logging import Logger
from typing import Any

from pydantic import BaseModel

from knowledge_base_mcp.utils.logging import BASE_LOGGER

logger: Logger = BASE_LOGGER.getChild(__name__)


@asynccontextmanager
async def worker_pool[WorkType: BaseModel | Sequence[BaseModel], ResultType: BaseModel | Sequence[BaseModel] | None = None](
    work_function: Callable[[WorkType], Coroutine[Any, Any, ResultType | None]],
    result_queue: asyncio.Queue[ResultType] | None = None,
    work_queue: asyncio.Queue[WorkType] | None = None,
    error_queue: asyncio.Queue[tuple[WorkType, Exception]] | None = None,
    workers: int = 4,
    work_type: type[WorkType] | None = None,  # noqa: ARG001  # pyright: ignore[reportUnusedParameter]
    result_type: type[ResultType] | None = None,  # noqa: ARG001  # pyright: ignore[reportUnusedParameter]
) -> AsyncIterator[tuple[asyncio.Queue[WorkType], asyncio.Queue[tuple[WorkType, Exception]]]]:
    """Run a worker pool that performs work that is pushed to it.

    Args:
        work_function: A function that performs work on a work item. The function must take a work item and optionally return a result.
        result_queue: An optional queue to put results into. If you need the results, you must provide a queue.
        work_queue: An optional queue to put work items into. If you need to push work items to the worker pool, you must provide a queue.
        error_queue: An optional queue to put errors into. If you need the errors, you must provide a queue.
        workers: The number of workers to run. Defaults to 4.

    Returns:
        A queue that work items can be added to.
    """

    if work_queue is None:
        work_queue = asyncio.Queue()

    if error_queue is None:
        error_queue = asyncio.Queue()

    async def _worker() -> None:
        """A worker function that processes work items from the queue."""

        try:
            while work_item := await work_queue.get():
                result: ResultType | None = await work_function(work_item)

                if result_queue is not None and result is not None:
                    await result_queue.put(item=result)

                    work_queue.task_done()
        except QueueShutDown:
            pass

    async with TaskGroup() as task_group:
        for _ in range(workers):
            _ = task_group.create_task(coro=_worker())

        yield work_queue, error_queue

        await work_queue.join()


@asynccontextmanager
async def batch_worker_pool[WorkType, ResultType](
    work_function: Callable[[list[WorkType]], Coroutine[Any, Any, ResultType | None]],
    work_type: type[WorkType] | None = None,  # noqa: ARG001  # pyright: ignore[reportUnusedParameter]
    result_type: type[ResultType] | None = None,  # noqa: ARG001  # pyright: ignore[reportUnusedParameter]
    workers: int = 4,
    minimum_cost: float = 0.0,
    cost_function: Callable[[WorkType], float] | None = None,
    result_queue: asyncio.Queue[ResultType] | None = None,
    error_queue: asyncio.Queue[tuple[list[WorkType], Exception]] | None = None,
    work_queue: asyncio.Queue[WorkType] | None = None,
) -> AsyncIterator[tuple[asyncio.Queue[WorkType], asyncio.Queue[tuple[list[WorkType], Exception]]]]:
    """Run a worker pool that performs work that is pushed to it. It will try to merge batches of work together until each batch
    reaches a minimum cost. Once the cost of a batch reaches the minimum cost, the batch will be processed.

    Args:
        work_function: A function that performs work on a work item. The function must take a work item and optionally return a result.
        cost_function: A function that calculates the cost of a work item. The function must take a work item and return a float.
        minimum_cost: The minimum cost of a batch before it is processed.
        result_queue: An optional queue to put results into. If you need the results, you must provide a queue.
        workers: The number of workers to run. Defaults to 4.
        work_type: The type of work to perform. Defaults to None.
        result_type: The type of result to return. Defaults to None.

    Returns:
        A queue that work items can be added to.
    """

    if work_queue is None:
        work_queue = asyncio.Queue()

    if error_queue is None:
        error_queue = asyncio.Queue()

    def _default_cost_function(work_item: WorkType) -> float:  # noqa: ARG001  # pyright: ignore[reportUnusedParameter]
        """A default cost function that returns 1.0 for each work item. This is useful for cases where the cost is not known."""
        return 1.0

    if cost_function is None:
        cost_function = _default_cost_function

    async def _worker() -> None:
        """A worker function that processes work items from the queue."""

        batch: list[WorkType] = []

        async def process_batch() -> None:
            """Process a batch of work items."""
            result: ResultType | None = None
            try:
                result = await work_function(batch)
            except Exception as e:
                logger.exception("Error processing batch")
                await error_queue.put(item=(batch, e))

            if result_queue is not None and result is not None:
                await result_queue.put(item=result)

        try:
            while work_item := await work_queue.get():
                batch.append(work_item)

                cost: float = cost_function(work_item)

                if cost < minimum_cost:
                    # We have queued the work to be processed, and we aren't going to process it now,
                    # so we'll tell the queue it doesn't need to track the item anymore.
                    work_queue.task_done()
                    continue

                await process_batch()

                work_queue.task_done()

        except QueueShutDown:
            if batch:
                await process_batch()

    async with TaskGroup() as task_group:
        for _ in range(workers):
            _ = task_group.create_task(coro=_worker())

        yield work_queue, error_queue

        # Our caller is trying to exit the context manager, so we need to shutdown the queue
        # so that the workers can flush their queues.
        work_queue.shutdown()

        await work_queue.join()



async def gather_results_from_queue[ResultType](queue: asyncio.Queue[ResultType]) -> list[ResultType]:
    """Gather results from a queue."""
    results: list[ResultType] = []

    try:
        while result := queue.get_nowait():
            results.append(result)

    except QueueEmpty:
        pass

    return results
