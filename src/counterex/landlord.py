"""Implementations of variations of landlord."""

from .item import Item, Trace
from .replacement import ReplacementPolicy


class EagerLandlord:
    """The eager optional cost model version of landlord."""

    def __init__(self, k: int):
        self._capacity = k
        self._cache: set[Item] = set()
        self._credits: dict[Item, int] = {}
        self._lru: list[Item] = []

    @staticmethod
    def _initial_credit(item: Item) -> int:
        return item.cost

    def _used_capacity(self) -> int:
        return len(self._cache)

    def _delta(self) -> int:
        if not self._cache:
            return 0
        return min(map(lambda i: self._credits[i], self._cache))

    def _victims(self) -> Item:
        return min(
            filter(lambda i: self._credits[i] == 0, self._cache),
            key=self._lru.index,
        )

    def _access(self, item: Item) -> None:
        """Take a step through the trace."""
        delta = self._delta()
        for i in self._cache:
            self._credits[i] -= delta

        if item in self._lru:
            self._lru.remove(item)
        self._lru.append(item)

        if item not in self._cache and self._used_capacity() + 1 > self._capacity:
            self._cache.remove(self._victims())

        self._cache.add(item)
        self._credits[item] = self._initial_credit(item)

        assert self._used_capacity() <= self._capacity

    def run(self, trace: Trace) -> None:
        """Run LL on the trace."""
        for item in trace:
            self._access(item)

    def set(self) -> set[Item]:
        """Get the cache set."""
        return self._cache


class Landlord(ReplacementPolicy):
    """The forced cost model version of landlord."""

    def __init__(self, k: int):
        self._capacity = k
        self._cache: set[Item] = set()
        self._credits: dict[Item, int] = {}

    @staticmethod
    def _initial_credit(item: Item) -> int:
        return item.cost

    def _used_capacity(self) -> int:
        return len(self._cache)

    def _delta(self) -> int:
        return min(map(lambda i: self._credits[i], self._cache))

    def _victims(self) -> list[Item]:
        return [*filter(lambda i: self._credits[i] == 0, self._cache)]

    def _access(self, item: Item) -> bool:
        """Take a step through the trace."""
        hit = item in self._cache

        if item not in self._cache and self._used_capacity() + 1 > self._capacity:
            delta = self._delta()
            for i in self._cache:
                self._credits[i] -= delta

            self._cache.difference_update(self._victims())

        self._cache.add(item)
        self._credits[item] = self._initial_credit(item)

        return hit

    def run(self, trace: Trace) -> int:
        """Run LL on the trace."""
        cost = 0

        for item in trace:
            if not self._access(item):
                cost += item.cost

        return cost

    def set(self) -> set[Item]:
        """Get the cache set."""
        return self._cache
