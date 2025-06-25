import pytest

from knowledge_base_mcp.utils.window import PeekableWindow, Window


class TestWindow:
    @pytest.fixture
    def window(self) -> Window[int]:
        return Window[int](items=[1, 2, 3, 4, 5])

    def test_window(self, window: Window[int]) -> None:
        assert window.look() == [1]
        assert window.look_one() == 1
        assert window.size == 1
        assert len(window) == 5

    def test_window_open(self, window: Window[int]) -> None:
        window.open()
        assert window.look() == [1, 2, 3, 4, 5]
        assert window.look_one() == 1
        assert window.size == 5
        assert len(window) == 5

    def test_window_close(self, window: Window[int]) -> None:
        window.close()
        assert window.look() == []

        with pytest.raises(ValueError):  # noqa: PT011
            assert window.look_one()

        assert window.size == 0
        assert len(window) == 5

    def test_window_expand(self, window: Window[int]) -> None:
        window.grow_right()
        assert window.look() == [1, 2]

        window.grow_right(2)
        assert window.look() == [1, 2, 3, 4]

        window.grow_right(1000)
        assert window.look() == [1, 2, 3, 4, 5]

    def test_window_shrink(self, window: Window[int]) -> None:
        window.open()
        assert window.look() == [1, 2, 3, 4, 5]

        window.shrink_right()
        assert window.look() == [1, 2, 3, 4]

        window.shrink_right(3)
        assert window.look() == [1]

        window.shrink_right(1000)
        assert window.look() == []

    def test_window_iteration(self, window: Window[int]) -> None:
        assert window.look() == [1]

        window.__next__()

        assert window.look() == [2]
        window.grow_right()
        assert window.look() == [2, 3]

        window.__next__()
        assert window.look() == [4]


class TestPeekableWindow:
    @pytest.fixture
    def peekable_window(self) -> PeekableWindow[int]:
        return PeekableWindow[int](items=[1, 2, 3, 4, 5])

    def test_peekable_window(self, peekable_window: PeekableWindow[int]) -> None:
        assert peekable_window.look() == [1]

        assert peekable_window.peek_left() is None

        assert peekable_window.peek_right() == 2

        assert peekable_window.peek_right() == 3

        assert peekable_window.peek_right() == 4

        assert peekable_window.peek_right() == 5

    def test_peekable_window_moving_right(self, peekable_window: PeekableWindow[int]) -> None:
        assert peekable_window.look() == [1]

        assert peekable_window.peek_left() is None

        assert peekable_window.peek_right() == 2

        assert peekable_window.peek_right() == 3

        assert peekable_window.grow_right() == 2

        assert peekable_window.peek_right() == 3

    def test_peekable_window_growing_to_peek(self, peekable_window: PeekableWindow[int]) -> None:
        assert peekable_window.look() == [1]

        assert peekable_window.peek_left() is None

        assert peekable_window.peek_right() == 2

        assert peekable_window.peek_right() == 3

        peekable_window.grow_to_peek()

        assert peekable_window.look() == [1, 2, 3]

        assert peekable_window.peek_right() == 4

        assert peekable_window.peek_right() == 5

        assert peekable_window.peek_right() is None

    def test_peekable_window_peek_look(self, peekable_window: PeekableWindow[int]) -> None:
        assert peekable_window.peek()[0] == []

        assert peekable_window.peek()[1] == []

        assert peekable_window.peek_left() is None

        assert peekable_window.peek_right() == 2

        assert peekable_window.peek()[1] == [2]

        peekable_window.slide()

        assert peekable_window.peek()[0] == []

        assert peekable_window.peek()[1] == []

        assert peekable_window.peek_left() == 1

        assert peekable_window.peek_right() == 3

        assert peekable_window.peek() == ([1], [3])
