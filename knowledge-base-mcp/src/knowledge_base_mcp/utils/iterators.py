from ast import TypeVar
from collections.abc import AsyncIterable, AsyncIterator, Iterable, Iterator
from typing import Any

T: TypeVar = TypeVar(name="T")


async def achunk[T: Any](async_iterable: AsyncIterable[T], size: int) -> AsyncIterator[list[T]]:
    """Chunk an async iterable into chunks of a given size."""

    buffer: list[T] = []

    async for item in async_iterable:
        buffer.append(item)  # pyright: ignore[reportAny]

        if len(buffer) >= size:
            yield buffer
            buffer = []

    yield buffer


def chunk[T: Any](iterable: Iterable[T], size: int) -> Iterator[list[T]]:
    """Chunk an iterable into chunks of a given size."""

    buffer: list[T] = []

    for item in iterable:
        buffer.append(item)  # pyright: ignore[reportAny]

        if len(buffer) >= size:
            yield buffer
            buffer = []

    yield buffer
