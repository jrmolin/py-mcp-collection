from collections.abc import Sequence
from typing import Self

# class BaseWindow[N]:
#     """A base class for windows over items in a sequence."""

#     _items: Sequence[N]
#     """The items in the window."""

#     _left: int
#     """The index of the leftmost item in the window."""

#     _width: int
#     """The width of the window."""


# class Window[N]:
#     """A set of items."""

#     _items: Sequence[N]
#     """The items in the window."""

#     def __iter__(self) -> "WindowIterator[N]":
#         """Iterate over the items in the window."""
#         return WindowIterator(self)

#     def __len__(self) -> int:
#         """Returns the number of items in the window."""
#         return len(self._items)

# class WindowIterator[N]:
#     _window: Window[N]
#     """The window."""

#     _left: int
#     """The index of the leftmost item in the window."""

#     def __init__(self, window: Window[N]) -> None:
#         """Initialize the window."""
#         self._window = window
#         self._left = 0

#     def _get_item(self) -> N:
#         """Returns the item at the left index."""

#         return self._window._items[self._left]

#     def __next__(self) -> N:
#         """Returns an element from the window."""

#         if self._left >= len(self._window._items):
#             raise StopIteration

#         self._left += 1
#         return self._get_item()


class SlidingWindowIterator[N]:
    """A sliding window over items in a sequence. Iterating over a window will slide the window to wherever
    the rightmost item is and return the number of items in the window as specified by the default size.
    The iterator will be closed when the left and right indices are equal.
    """

    _items: Sequence[N]
    """The items in the window."""

    _width: int
    """The number of items returned each time the window is iterated over."""

    def __init__(self, items: Sequence[N], width: int = 1) -> None:
        """Initialize the window."""
        self._items = items
        self._width = width

    @property
    def width(self) -> int:
        """The number of items returned each time the window is iterated over."""
        return self._width

    def _pop(self) -> Sequence[N]:
        """Removes `width` items from the left of the window."""
        return self._pop_n(self._width)

    def _pop_n(self, n: int) -> Sequence[N]:
        """Removes `n` items from the left of the window."""
        popped: Sequence[N] = self._items[:n]
        self._items = self._items[n:]
        return popped

    def __iter__(self) -> Self:
        """Iterate over the items in the window."""
        return self

    def __next__(self) -> Sequence[N]:
        """Returns a Window of the default size."""
        return self._pop()


# class PeekableSlidingWindowIterator[N](SlidingWindowIterator[N]):
#     """A peekable sliding window over items in a sequence. Iterating over a window will slide the window to wherever
#     the rightmost item is and return the number of items in the window as specified by the default size.
#     The iterator will be closed when the left and right indices are equal.
#     """

#     _peek_index: int | None = None
#     """The index of the last peeked item."""

#     def peek(self) -> N:
#         """Returns the next item in the window without removing it. Calling this method will not advance the window.
#         but will advance the peek index allowing you to peek multiple items ahead."""
#         self._peek_index = (self._peek_index or 0) + 1

#         peeked: N = self._items[self._peek_index]

#         return peeked

#     def commit_to_peek(self) -> None:
#         """Commits the peeked items to the window. This will advance the window by the number of items peeked."""
#         if self._peek_index is None:
#             msg = "No peeked items to commit. Call `peek` first."
#             raise ValueError(msg)

#         self._pop_n(self._peek_index)
#         self._peek_index = None

#     def __next__(self) -> Sequence[N]:
#         """Returns a Window of the default size."""
#         self._peek_index = 0

#         return super().__next__()


class PeekableIterator[N]:
    """A peekable iterator over items in a sequence. Iterating over an iterator will return the next item in the sequence.
    Calling the `peek` method will return the next item in the sequence without removing it from the iterator.
    """

    _items: Sequence[N]
    """The iterator."""

    _peek_index: int | None = None
    """The index of the last peeked item."""

    def __init__(self, items: Sequence[N]) -> None:
        """Initialize the iterator."""
        self._items = items

    def _next_peek_index(self) -> int:
        """Returns the next peek index."""
        return 0 if self._peek_index is None else self._peek_index + 1

    def can_peek(self) -> bool:
        """Returns True if the iterator can be peeked."""
        return self._next_peek_index() < len(self._items)

    def _unpeek(self) -> None:
        """Unpeeks the iterator."""
        if self._peek_index is None:
            return

        if self._peek_index == 0:
            self._peek_index = None
        else:
            self._peek_index -= 1

    def peek(self, sneak: bool = False) -> N | None:
        """Returns the next item in the iterator without removing it."""
        if not self.can_peek():
            return None

        self._peek_index = self._next_peek_index()

        peeked: N = self._items[self._peek_index]

        if sneak:
            self._unpeek()

        return peeked

    def repeek(self) -> list[N]:
        """Repeeks the iterator."""

        if self._peek_index is None:
            return []

        return [self._items[i] for i in range(self._peek_index + 1)]

    def _can_pop(self) -> bool:
        """Returns True if the iterator can be popped."""
        return len(self._items) > 0

    def _pop(self) -> N:
        """Removes the next item from the iterator."""
        if not self._can_pop():
            msg = "No items to pop."
            raise IndexError(msg)

        popped: N = self._items[0]
        self._items = self._items[1:]
        return popped

    def commit_to_peek(self, except_last: bool = False) -> list[N]:
        """Advance the iterator by the number of items peeked.

        Args:
            except_last: If True, the very last item peeked will not be popped.
        """

        if except_last:
            self._unpeek()

        if self._peek_index is None:
            return []

        popped: list[N] = [self._pop() for _ in range(self._peek_index + 1)]
        self._peek_index = None

        return popped

    def __iter__(self) -> Self:
        """Iterate over the items in the iterator."""
        return self

    def __next__(self) -> N:
        """Returns the next item in the iterator."""
        if not self._can_pop():
            raise StopIteration

        self._peek_index = None

        return self._pop()
