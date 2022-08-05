"""Implementation of the Priority Landlord algorithm."""

from .item import Item
from .replacement import ReplacementPolicy


class PriorityLandlord(ReplacementPolicy):
    """The optional cost model version of landlord."""

    def __init__(self, k: int):
        super().__init__(k)
        self._priorities: dict[Item, int] = {}
        self._stack: list[Item] = []

    @staticmethod
    def _initial_priority(item: Item) -> int:
        return item.cost

    def _used_capacity(self) -> int:
        return len(self._cache)

    def _victims(self) -> Item:
        min_prio = min(map(lambda i: self._priorities[i], self._cache))
        return min(
            filter(lambda i: self._priorities[i] == min_prio, self._cache),
            key=self._stack.index,
        )

    def _access(self, item: Item) -> bool:
        """Take a step through the trace."""
        hit = item in self._cache
        initial_prio = self._initial_priority(item)

        if item in self._stack:
            self._stack.remove(item)
        self._stack.append(item)

        for i in self._cache:
            self._priorities[i] -= initial_prio

        if (item not in self._cache) and (self._used_capacity() + 1 > self._capacity):
            self._cache.remove(self._victims())

        self._cache.add(item)
        self._priorities[item] = initial_prio

        return hit


class PriorityLandlordUnique(ReplacementPolicy):
    """The optional cost model version of landlord."""

    def __init__(self, k: int):
        super().__init__(k)
        self._priorities: dict[Item, int] = {}
        self._stack: list[Item] = []

    @staticmethod
    def _initial_priority(item: Item) -> int:
        return item.cost

    def _used_capacity(self) -> int:
        return len(self._cache)

    def _victims(self) -> Item:
        min_prio = min(map(lambda i: self._priorities[i], self._cache))
        return min(
            filter(lambda i: self._priorities[i] == min_prio, self._cache),
            key=self._stack.index,
        )

    def _access(self, item: Item) -> bool:
        """Take a step through the trace."""
        hit = item in self._cache
        initial_prio = self._initial_priority(item)

        index = -1
        if item in self._stack:
            index = self._stack.index(item)
            self._stack.remove(item)

        self._stack.append(item)

        for i in self._cache:
            if self._stack.index(i) > index:
                # i was accessed more recently than index
                self._priorities[i] -= initial_prio

        if (item not in self._cache) and (self._used_capacity() + 1 > self._capacity):
            self._cache.remove(self._victims())

        self._cache.add(item)
        self._priorities[item] = initial_prio

        return hit
