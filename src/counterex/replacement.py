"""Contains an ABC for replacement."""

from abc import ABC, abstractmethod

from .item import Item, Trace


class ReplacementPolicy(ABC):
    """An abstract replacement policy."""

    def __init__(self, k: int):
        self._capacity = k
        self._cache: set[Item] = set()

    @abstractmethod
    def _access(self, item: Item) -> bool:
        """Access the item, returning whether it hit."""

    def _used_capacity(self) -> int:
        return len(self._cache)

    def _overfull(self) -> bool:
        """Return whether the cache is full."""
        return self._used_capacity() > self._capacity

    def run(self, trace: Trace) -> int:
        """Run the replacement algorithm on the trace, returning the cost paid.."""
        cost = 0

        for item in trace:
            if not self._access(item):
                cost += item.cost

        return cost

    def set(self) -> set[Item]:
        """Get the cache set."""
        return self._cache
