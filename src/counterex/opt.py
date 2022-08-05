"""Contains optimal solutions to caching problems."""

from copy import deepcopy

from hypothesis import note
from ortools.graph import pywrapgraph

from .item import Item, Trace
from .replacement import ReplacementPolicy


class Opt(ReplacementPolicy):
    """A brute-force optimal solution to variable-cost caching."""

    def _access(self, item: Item) -> bool:
        """Shouldn't be used."""
        return True

    def _run(self, trace: Trace, i: int) -> int:
        if i >= len(trace):
            return 0

        cost = 0
        if trace[i] not in self._cache:
            cost += trace[i].cost
            self._cache.add(trace[i])

            if self._overfull():
                min_cost = None
                for j in deepcopy(self._cache):
                    if j != trace[i]:
                        self._cache.remove(j)

                        recursive_cost = self._run(trace, i + 1)
                        if not min_cost or min_cost > recursive_cost:
                            min_cost = recursive_cost

                        self._cache.add(j)

                assert min_cost is not None
                if trace[i] in self._cache:
                    self._cache.remove(trace[i])
                return cost + min_cost

            self._cache.remove(trace[i])

        self._cache.add(trace[i])
        return cost + self._run(trace, i + 1)

    def run(self, trace: Trace) -> int:
        """Run the algorithm on the trace."""
        return self._run(trace, 0)


class McfOpt(ReplacementPolicy):
    """A min cost flow optimal solution to variable-cost caching.

    For every access, edge to next access with infinite capacity and zero cost, and an
    edge to the same access to the next variable with one capacity and $-k$ cost, where
    $k$ is the cost of an access to that variable.
    """

    def __init__(self, k: int):
        super().__init__(k)
        self._start_nodes: list[int] = []
        self._end_nodes: list[int] = []
        self._capacities: list[int] = []
        self._unit_costs: list[int] = []
        self._last_accesses: dict[Item, int] = {}
        self._next_index = 0

    def _access(self, item: Item) -> bool:
        if (last := self._last_accesses.get(item)) is not None:
            self._start_nodes.append(last)
            self._end_nodes.append(self._next_index)
            self._capacities.append(1)
            self._unit_costs.append(-item.cost)

        if self._next_index != 0:
            self._start_nodes.append(self._next_index - 1)
            self._end_nodes.append(self._next_index)
            self._capacities.append(self._capacity)
            self._unit_costs.append(0)

        self._last_accesses[item] = self._next_index
        self._next_index += 1

        return False

    def _gen_demand(self) -> list[int]:
        out = []
        uniques = len({*self._start_nodes})

        if uniques == 0:
            return []

        uniques += 1

        for i in range(uniques):
            if i == 0:
                out.append(self._capacity)
            elif i == uniques - 1:
                out.append(-self._capacity)
            else:
                out.append(0)

        return out

    def _gen_min_cost_flow(self, demand: list[int]) -> pywrapgraph.SimpleMinCostFlow:
        """Generate the minimum cost flow problem.

        Docs: https://developers.google.com/optimization/flow/mincostflow#python.
        """
        min_cost_flow = pywrapgraph.SimpleMinCostFlow()
        for arc in zip(
            self._start_nodes, self._end_nodes, self._capacities, self._unit_costs
        ):
            min_cost_flow.AddArcWithCapacityAndUnitCost(arc[0], arc[1], arc[2], arc[3])

        for i, dmd in enumerate(demand):
            min_cost_flow.SetNodeSupply(i, dmd)

        return min_cost_flow

    def run(self, trace: Trace) -> int:
        """Run the algorithm on the trace."""
        total_cost = 0

        for item in trace:
            total_cost += item.cost
            self._access(item)

        note(f"START NODES: {self._start_nodes}")
        note(f"END NODES: {self._end_nodes}")
        note(f"CAPACITIES: {self._capacities}")
        note(f"COSTS: {self._unit_costs}")

        demand = self._gen_demand()
        note(f"DEMANDS: {demand}")

        min_cost_flow = self._gen_min_cost_flow(demand)
        status = min_cost_flow.Solve()
        assert (
            status == min_cost_flow.OPTIMAL
        ), f"There was an issue with the min cost flow input: {status}."

        # mcf will return a negative number, to get the cost paid we do this
        return total_cost + min_cost_flow.OptimalCost()  # type: ignore
