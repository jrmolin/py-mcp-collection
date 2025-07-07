import asyncio
from asyncio import TaskGroup
from asyncio.queues import QueueEmpty, QueueShutDown
from collections.abc import AsyncIterator, Callable, Coroutine
from contextlib import asynccontextmanager
from logging import Logger
from typing import Any

from filesystem_operations_mcp.logging import BASE_LOGGER

logger: Logger = BASE_LOGGER.getChild(__name__)


@asynccontextmanager
async def worker_pool[WorkType: Any, ResultType: Any | None](
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

    async def _worker(worker_id: int) -> None:
        """A worker function that processes work items from the queue."""

        try:
            while work_item := await work_queue.get():
                result: ResultType | None = None
                try:
                    result = await work_function(work_item)

                except (asyncio.CancelledError, QueueShutDown):
                    return
                except Exception as e:
                    logger.exception(f"{worker_id}: Error processing work item")
                    await error_queue.put(item=(work_item, e))

                if result_queue is not None and result is not None:
                    await result_queue.put(item=result)

                work_queue.task_done()

        except QueueShutDown:
            return

    async with TaskGroup() as task_group:
        for i in range(workers):
            _ = task_group.create_task(coro=_worker(worker_id=i))

        yield work_queue, error_queue

        await work_queue.join()

        work_queue.shutdown()


async def gather_results_from_queue[ResultType](queue: asyncio.Queue[ResultType]) -> list[ResultType]:
    """Gather results from a queue."""
    results: list[ResultType] = []

    try:
        while result := queue.get_nowait():
            results.append(result)

    except QueueEmpty:
        pass

    return results
