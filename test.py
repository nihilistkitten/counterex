"""Tests for counterex."""

from copy import deepcopy
from typing import Any, Callable

import hypothesis.strategies as st
import pytest
from hypothesis import assume, given, note, settings

from counterex import (
    Item,
    McfOpt,
    Opt,
    PriorityLandlord,
    PriorityLandlordUnique,
    ReplacementPolicy,
    Trace,
    make_items,
)

ITEMS = make_items([1, 1, 1, 2, 2, 50, 90, 100, 100])


@st.composite
def traces(draw: Callable[..., Any], max_size: int = 10) -> Trace:
    """Generate a trace."""
    return Trace(draw(st.lists(st.sampled_from(ITEMS), min_size=1, max_size=max_size)))


# def test_landlord_a() -> None:
#     """Test landlord on A."""
#     cache = EagerLandlord(3)
#     trace = Trace([ITEMS[0]])
#     cache.run(trace)
#     assert cache.set() == {ITEMS[0]}


# def test_landlord_two() -> None:
#     """Test landlord on AB."""
#     cache = EagerLandlord(1)
#     trace = Trace([ITEMS[0], ITEMS[1]])
#     cache.run(trace)
#     assert not cache.set()


def comp_ratio_on(
    trace: Trace, k: int, h: int, algorithm: type[ReplacementPolicy]
) -> float:
    """Determine the competitive ratio of algorithm on trace."""
    online = algorithm(k)
    offline = Opt(h)

    cost_online = online.run(deepcopy(trace))
    cost_offline = offline.run(deepcopy(trace))

    note(f"online: {cost_online}")
    note(f"offline: {cost_offline}")

    if cost_offline == 0:
        assert cost_online == 0
        return 0
    return cost_online / cost_offline


def is_comp_on(
    trace: Trace, k: int, h: int, algorithm: type[ReplacementPolicy]
) -> bool:
    """Check whther the algorithm is optimally competitive on trace."""
    return comp_ratio_on(trace, k, h, algorithm) <= k / (k - h + 1)


@given(traces(max_size=20), st.integers(1, 4), st.integers(1, 4))
@settings(deadline=5000)
# @example(
#     Trace(
#         [
#             ITEMS[12],
#             ITEMS[1],
#             ITEMS[0],
#             ITEMS[12],
#             ITEMS[1],
#             ITEMS[0],
#             ITEMS[12],
#             ITEMS[1],
#             ITEMS[0],
#             ITEMS[12],
#             ITEMS[1],
#             ITEMS[0],
#             ITEMS[12],
#         ]
#     ),
#     2,
# )
def test_is_comp(trace: Trace, k: int, h: int) -> None:
    """Test that the algorithm is competitive on trace at sizes (k, h)."""
    assume(k >= h)
    assert is_comp_on(trace, k, h, PriorityLandlordUnique)


def is_sa_on(trace: Trace, k: int, algorithm: type) -> bool:
    """Return whether the algorithm is a stack algorithm at size k on trace."""
    small = algorithm(k)
    large = algorithm(k + 1)

    small.run(deepcopy(trace))
    large.run(deepcopy(trace))

    small_set = small.set()
    large_set = large.set()

    note(f"small: {small_set!r}")
    note(f"large: {large_set!r}")

    return small_set.issubset(large_set)  # type: ignore


@given(traces(max_size=15), st.integers(1, 4))
def test_is_sa(trace: Trace, k: int) -> None:
    """Test that the algorithm is a SA on trace at size (k, k+1)."""
    assert is_sa_on(trace, k, PriorityLandlordUnique)


@pytest.mark.parametrize(
    "k,trace,out",
    [
        (1, [ITEMS[0]], 1),
        (2, [ITEMS[0], ITEMS[4]], 3),
        (2, [ITEMS[0], ITEMS[4], ITEMS[4]], 3),
        (2, [ITEMS[0], ITEMS[1], ITEMS[2], ITEMS[4]], 5),
    ],
)
def test_opt(k: int, trace: list[Item], out: int) -> None:
    """Test that opt gives the desired cost."""
    assert Opt(k).run(Trace(trace)) == out


# @given(traces(), st.integers(1, 4))
# def test_opt_cold_start(trace: Trace, k: int) -> None:
#     assert Opt(k).run(deepcopy(trace)) >= sum(map(lambda i: i.cost, {*trace}))


# @given(traces(), st.integers(1, 4))
# def test_mcf(trace: Trace, k: int) -> None:
#     TODO: stop bypassing for MCF
#     """Test that the cost of the mcf opt equals the cost of the naive opt."""
#     assert Opt(k).run(trace) == McfOpt(k).run(trace)
