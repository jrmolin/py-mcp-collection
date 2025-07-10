from knowledge_base_mcp.utils.window import PeekableIterator


def test_peekable_window() -> None:
    window: PeekableIterator[int] = PeekableIterator(items=[1, 2, 3, 4, 5])
    assert next(window) == 1
    assert window.peek() == 2
    assert window.peek(sneak=True) == 3
    assert window.peek() == 3
    assert window.peek(sneak=True) == 4
    assert window.peek() == 4
    assert window.peek(sneak=True) == 5
    assert window.peek() == 5
    assert window.peek(sneak=True) is None
    assert window.peek() is None
    assert window.peek(sneak=True) is None


def test_peekable_window_commit_to_peek() -> None:
    window: PeekableIterator[int] = PeekableIterator(items=[1, 2, 3, 4, 5])
    assert next(window) == 1
    assert window.peek() == 2
    window.commit_to_peek()
    assert window.peek() == 3
    assert next(window) == 3


def test_peekable_window_commit_to_peek_except_last() -> None:
    window: PeekableIterator[int] = PeekableIterator(items=[1, 2, 3, 4, 5])
    assert next(window) == 1
    assert window.peek() == 2
    window.commit_to_peek(except_last=True)
    assert window.peek() == 2
    assert next(window) == 2
    assert window.peek() == 3
    assert next(window) == 3
