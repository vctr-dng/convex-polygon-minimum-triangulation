"""Triangulation algorithms with a shared cost definition."""

from __future__ import annotations

from dataclasses import dataclass

from ortools.math_opt.python import mathopt

from .geometry import Chord, Polygon
from .triangulation import Triangulation


def candidate_chords(polygon: Polygon) -> list[Chord]:
    return [
        Chord(polygon, first, second)
        for first in range(len(polygon))
        for second in range(first + 1, len(polygon))
        if not polygon.is_edge(first, second)
    ]


def exhaustive_triangulations(polygon: Polygon) -> list[Triangulation]:
    """Enumerate every non-crossing triangulation of a small convex polygon."""

    candidates = candidate_chords(polygon)
    results: list[Triangulation] = []
    required_chords = len(polygon) - 3

    def visit(start: int, current: Triangulation) -> None:
        if len(current.chords) == required_chords:
            results.append(current)
            return
        for index in range(start, len(candidates)):
            chord = candidates[index]
            next_triangulation = current.copy()
            if next_triangulation.add_chord(chord.first, chord.second):
                visit(index + 1, next_triangulation)

    visit(0, Triangulation(polygon))
    return results


def minimum_exhaustive_triangulation(polygon: Polygon) -> Triangulation:
    triangulations = exhaustive_triangulations(polygon)
    return min(triangulations, key=Triangulation.total_cost)


def greedy_triangulation(polygon: Polygon) -> Triangulation:
    """Add the shortest valid diagonal until the triangulation is complete."""

    triangulation = Triangulation(polygon)
    for chord in sorted(candidate_chords(polygon), key=lambda item: item.length):
        triangulation.add_chord(chord.first, chord.second)
        if triangulation.complete():
            break
    return triangulation


@dataclass(frozen=True)
class DynamicResult:
    triangulation: Triangulation
    cost_table: tuple[tuple[float, ...], ...]
    split_table: tuple[tuple[int | None, ...], ...]


def dynamic_triangulation(polygon: Polygon) -> DynamicResult:
    """Find a minimum-length triangulation with interval dynamic programming."""

    vertex_count = len(polygon)
    costs = [[0.0] * vertex_count for _ in range(vertex_count)]
    splits: list[list[int | None]] = [
        [None] * vertex_count for _ in range(vertex_count)
    ]

    def diagonal_cost(first: int, second: int) -> float:
        if polygon.is_edge(first, second):
            return 0.0
        return Chord(polygon, first, second).length

    for width in range(3, vertex_count):
        for first in range(vertex_count - width):
            second = first + width
            best_cost = float("inf")
            best_split: int | None = None
            for middle in range(first + 1, second):
                cost = (
                    costs[first][middle]
                    + costs[middle][second]
                    + diagonal_cost(first, middle)
                    + diagonal_cost(middle, second)
                )
                if cost < best_cost:
                    best_cost = cost
                    best_split = middle
            costs[first][second] = best_cost
            splits[first][second] = best_split

    triangulation = Triangulation(polygon)

    def reconstruct(first: int, second: int) -> None:
        if second - first <= 2:
            return
        middle = splits[first][second]
        if middle is None:
            raise RuntimeError("The dynamic-programming split table is incomplete.")
        if not polygon.is_edge(first, middle):
            triangulation.add_chord(first, middle)
        if not polygon.is_edge(middle, second):
            triangulation.add_chord(middle, second)
        reconstruct(first, middle)
        reconstruct(middle, second)

    reconstruct(0, vertex_count - 1)
    if not triangulation.complete():
        raise RuntimeError(
            "Dynamic programming did not reconstruct a complete triangulation."
        )
    return DynamicResult(
        triangulation=triangulation,
        cost_table=tuple(tuple(row) for row in costs),
        split_table=tuple(tuple(row) for row in splits),
    )


## MILP triangulation


def build_model(triangulation: Triangulation, chords: list[Chord]) -> mathopt.Model:
    n = len(triangulation.polygon)

    model = mathopt.Model(name=f"min-length-triangulation-{n}")

    # control variables
    for chord in chords:
        var = model.add_binary_variable(name=f"{chord.first}_{chord.second}")
        model.objective.add_linear(chord.length * var)

    # diagonals count equality constraint
    model.add_linear_constraint(
        sum(var for var in model.variables()) == n - 3, name="diagonals_count"
    )

    # no crossing inequality constraints
    for i, chord_i in enumerate(chords):
        for j in range(i + 1, len(chords)):
            chord_j = chords[j]
            if triangulation._crosses(chord_i, chord_j):
                model.add_linear_constraint(
                    model.get_variable(i) + model.get_variable(j) <= 1,
                    name=f"no_crossing_{(chord_i.first, chord_i.second)}_{(chord_j.first, chord_j.second)}",
                )

    return model


def milp_triangulation(polygon: Polygon) -> Triangulation:
    triangulation = Triangulation(polygon)
    chords = candidate_chords(polygon)
    model = build_model(triangulation, chords)

    params = mathopt.SolveParameters(enable_output=True)
    result = mathopt.solve(
        opt_model=model, solver_type=mathopt.SolverType.HIGHS, params=params
    )
    # print(result)

    if result.termination.reason != mathopt.TerminationReason.OPTIMAL:
        raise RuntimeError(f"model failed to solve: {result.termination}")

    for var, value in result.variable_values().items():
        if value == 1.0:
            chord = chords[var.id]
            triangulation.add_chord(chord.first, chord.second)

    return triangulation
