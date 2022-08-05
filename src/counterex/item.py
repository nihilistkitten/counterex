"""Abstracted items and traces."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Item:
    """A cache item."""

    name: str
    cost: int
    size: int

    @classmethod
    def with_cost(cls, name: str, cost: int) -> "Item":
        """Make a new item with unit size."""
        return cls(name, cost, 1)

    def __repr__(self) -> str:
        """Represent the item."""
        return self.name


def make_items(costs: list[int]) -> list[Item]:
    """Make items with the defined costs."""
    return list(
        map(
            lambda val: Item.with_cost(chr(val[0] + ord("A")), val[1]), enumerate(costs)
        )
    )


class Trace:
    """A trace."""

    def __init__(self, trace: list[Item]):
        self._trace = trace
        self._current = 0

    def __iter__(self) -> "Trace":
        """Iterate self."""
        return self

    def __next__(self) -> Item:
        """Get the next item in the trace."""
        self._current += 1
        if self._current > len(self._trace):
            raise StopIteration
        return self._trace[self._current - 1]

    def __repr__(self) -> str:
        """Get a string representation of self."""
        return self._trace.__repr__()

    def __getitem__(self, i: int) -> Item:
        """Get the item at index i."""
        return self._trace[i]

    def __len__(self) -> int:
        """Get the trace's length."""
        return len(self._trace)
