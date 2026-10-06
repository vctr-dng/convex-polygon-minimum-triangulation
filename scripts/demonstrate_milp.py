# %%
from ortools.math_opt.python import mathopt

from polygon_triangulation.algorithms import candidate_chords
from polygon_triangulation.dataset import (
    load_dataset,
    polygon_from_entry,
    triangulation_from_entry,
)
from polygon_triangulation.geometry import Chord, Polygon
from polygon_triangulation.triangulation import Triangulation

# %%


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


# %%

VERTEX_COUNT = 4
SHOW_PLOTS = True

for index, entry in enumerate(load_dataset(VERTEX_COUNT)):
    polygon = polygon_from_entry(entry)
    reference = triangulation_from_entry(entry, polygon)
    result = milp_triangulation(polygon)

    print(f"Sample {index}")
    print(f"Saved optimal cost:   {reference.total_cost():.3f}")
    print(f"MILP optimal cost: {result.total_cost():.3f}")
    print(f"MILP chords: {result.dump()}")
    print()

    if SHOW_PLOTS:
        reference.draw()
        result.draw()
