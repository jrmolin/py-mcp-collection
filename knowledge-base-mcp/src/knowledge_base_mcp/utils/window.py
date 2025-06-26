from collections.abc import Sequence, Sized
from typing import Self, override

# Window iterator example
# # data: [1, 2, 3, 4, 5]

# # First window: (1), 2, 3, 4, 5
# # look returns 1
# # peek_right returns 2
# # grow_right() and then look returns 1, 2
# # Second Window: (3), 4, 5
# # look returns 3
# # peek_right returns 4
# # grow_right() and then look returns 3, 4

# # Get a new window from the iterator
# for window in PeekableWindow[BaseNode](items=nodes):

#     # Get the first node in the window
#     node = window.look_one()

#     # Keep peeking to the right until we break
#     while peek_node := window.peek_right():

#         # Stop peeking, note: the window has not changed
#         if some_condition:
#             break

#         # Go through another iteration to peek another node before growing the window
#         if peek_another_node:
#             continue
#         # ...

#         # Grow the window to what we're peeking
#         window.grow_to_peek()


class Window[N](Sized):
    """A window over items in a sequence. Iterating over a window will slide the window to wherever
    the rightmost item is. The window will be closed when the left and right indices are equal.
    """

    items: Sequence[N]
    """The items in the window."""

    _left: int = 0
    """The index of the leftmost item in the window."""

    _right: int = 1
    """The index of the rightmost item in the window."""

    @property
    def left(self) -> int:
        """The index of the leftmost item in the window."""
        return self._left

    @left.setter
    def left(self, value: int) -> None:
        self._left = max(min(value, self.right), 0)

    @property
    def right(self) -> int:
        """The index of the rightmost item in the window."""
        return self._right

    @right.setter
    def right(self, value: int) -> None:
        self._right = max(min(value, len(self)), 0)

    def __init__(self, items: Sequence[N]) -> None:
        """Initialize the window."""
        self.items = items

    def __len__(self) -> int:
        """Get the length of the window."""
        return len(self.items)

    def __iter__(self) -> Self:
        """Iterate over the items in the window."""
        self.left = 0
        self.right = 0
        return self

    def __next__(self) -> Self:
        """Iterate the window by moving the left side to where the right side is and shrinking the window to be
        one item wide."""
        self.left = self.right
        self.right += 1

        if self.is_closed:
            raise StopIteration

        return self

    def look(self) -> Sequence[N]:
        """Look at the items in the window."""
        if self.is_closed:
            return []

        return self.items[self.left : self.right]

    def look_one(self) -> N:
        """Look at the next item in the window. Will raise an error if the window is closed."""
        if self.is_closed:
            msg = "Window is closed"
            raise ValueError(msg)

        return self.items[self.left]

    @property
    def size(self) -> int:
        """Get the size of the window."""
        return self.right - self.left

    def close(self) -> None:
        """Fully close the window from the right."""
        self.right = self.left

    @property
    def is_closed(self) -> bool:
        """Check if the window is closed."""
        return self.left == self.right

    def open(self) -> None:
        """Fully open the window to the right."""
        self.right = len(self.items)

    @property
    def is_open(self) -> bool:
        """Check if the window is open."""
        return self.right == len(self.items)

    # def peek_left(self, skip: int = 1) -> N | None:
    #     """Peek at the item to the left of the window."""
    #     if self.left - skip < 0:
    #         return None
    #     return self.items[self.left - skip]

    # def peek_right(self, skip: int = 0) -> N | None:
    #     """Peek at the item to the right of the window."""
    #     if self.right + skip > len(self.items):
    #         return None
    #     return self.items[self.left + skip]

    def grow_left(self, amount: int = 1) -> N:
        """Grow the window to the left by the given amount, returning the item that is now the leftmost item."""
        self.left -= amount
        return self.look_one()

    def grow_right(self, amount: int = 1) -> N:
        """Grow the window to the right by the given amount, returning the item that is now the rightmost item."""
        self.right += amount
        return self.items[self.right - 1]

    def shrink_left(self, amount: int = 1) -> None:
        """Shrink the window to the left by the given amount."""
        self.left += amount

    def shrink_right(self, amount: int = 1) -> None:
        """Shrink the window to the right by the given amount."""
        self.right -= amount

    def slide(self, amount: int = 1) -> None:
        """Slide the window."""
        self.left += amount
        self.right += amount


class PeekableWindow[N](Window[N]):
    """A peekable window over items in a sequence. A peekable window has two additional indices for
    the peek left and peek right. Peeking will not impact the window and will not impact window iteration."""

    _pleft: int = 0
    """The amount beyond the left bound of the window that is being peeked."""

    _pright: int = 0
    """The amount beyond the right bound of the window that is being peeked."""

    @property
    @override
    def left(self) -> int:
        """The index of the leftmost item in the window."""
        return self._left

    @left.setter
    @override
    def left(self, value: int) -> None:
        self._left = max(min(value, self.right), 0)
        self.pleft = 0

    @property
    @override
    def right(self) -> int:
        """The index of the rightmost item in the window."""
        return self._right

    @right.setter
    @override
    def right(self, value: int) -> None:
        self._right = max(min(value, len(self)), 0)
        self.pright = 0

    @property
    def pleft(self) -> int:
        """The amount beyond the left bound of the window that is being peeked."""
        return self._pleft

    @pleft.setter
    def pleft(self, value: int) -> None:
        # Pleft cannot be less than 0
        value = max(value, 0)

        # Pleft cannot be greater than the left bound of the window
        if self.left - value < 0:
            value = self.left

        self._pleft = value

    @property
    def pright(self) -> int:
        """The amount beyond the right bound of the window that is being peeked."""
        return self._pright

    @pright.setter
    def pright(self, value: int) -> None:
        # Pright cannot be less than 0
        value = max(value, 0)

        # Pright cannot be greater than the right bound of the window
        right_max = len(self.items) - self.right
        value = min(value, right_max)

        self._pright = value

    # @property
    # def peek_look(self, only_peek: bool = False) -> Sequence[N]:
    #     """Look at the items in the peek window."""
    #     left_bound = self.left - self.pleft
    #     right_bound = self.right + self.pright

    #     return self.items[left_bound:right_bound]

    def peek(self) -> tuple[Sequence[N], Sequence[N]]:
        """Peek at the items in the window."""

        left_peek: Sequence[N] = self.items[self.left - self.pleft : self.left]
        right_peek: Sequence[N] = self.items[self.right : self.right + self.pright]

        return left_peek, right_peek

    # def peek_look_left(self, include_window: bool = False) -> Sequence[N]:
    #     """Look at the items in the peek window to the left."""
    #     left_bound = self.left - self.pleft
    #     right_bound = self.right if include_window else self.left

    #     return self.items[left_bound:right_bound]

    # def peek_look_right(self, include_window: bool = False) -> Sequence[N]:
    #     """Look at the items in the peek window to the right."""
    #     left_bound = self.left if include_window else self.right
    #     right_bound = self.right + self.pright

    #     return self.items[left_bound:right_bound]

    def peek_left(self) -> N | None:
        """Peek an additional item to the left of the window."""
        if self.pleft + 1 > self.left:
            return None

        self.pleft = self.pleft + 1
        return self.items[self.left - self.pleft]

    def peek_right(self) -> N | None:
        """Peek an additional item to the right of the window."""
        if self.pright + 1 > len(self.items) - self.right:
            return None

        self.pright = self.pright + 1
        return self.items[self.right + self.pright - 1]

    def grow_to_peek(self) -> None:
        """Grow the window to the peek bounds."""
        self.right = self.right + self.pright
        self.left = self.left - self.pleft
