"""Implementation of LRU."""

from .item import Item
from .replacement import ReplacementPolicy


class Lru(ReplacementPolicy):
    """A LRU replacement policy."""

    def __init__(self, k: int):
        super().__init__(k)
        self._stack: list[Item] = []

    def _access(self, item: Item) -> bool:
        """Take a step through the trace."""
        hit = item in self._cache

        if item in self._stack:
            self._stack.remove(item)

        self._stack.append(item)
        self._cache.add(item)

        if self._overfull():
            self._cache.remove(self._stack[0])
            self._stack.remove(self._stack[0])

        return hit


class Mru(ReplacementPolicy):
    """A MRU replacement policy."""

    def __init__(self, k: int):
        super().__init__(k)
        self._stack: list[Item] = []

    def _access(self, item: Item) -> bool:
        """Take a step through the trace."""
        hit = item in self._cache

        if item in self._stack:
            self._stack.remove(item)

        self._cache.add(item)

        if self._overfull():
            self._cache.remove(self._stack.pop())

        self._stack.append(item)

        return hit
