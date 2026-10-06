# %%
from ortools.math_opt.python import mathopt

from polygon_triangulation.dataset import (
    load_dataset,
    polygon_from_entry,
    triangulation_from_entry,
)
from polygon_triangulation.geometry import Chord, Polygon
from polygon_triangulation.triangulation import Triangulation

# %%


def valid_chords(polygon: Polygon) -> list[Chord]:
    res: list[Chord] = []
    for i in range(len(polygon)):
        for j in range(i + 1, len(polygon)):
            if not polygon.is_edge(i, j):
                res.append(Chord(polygon, i, j))
    return res


def build_model(polygon: Polygon) -> mathopt.Model:
    model = mathopt.Model(name=f"min-length-triangulation-{len(polygon)}")


def milp_triangulation(polygon: Polygon) -> Triangulation:
    pass


def print_costs(costs: list[list[float]]):
    for row in costs:
        print([f"{cost:.2f}" for cost in row])


# %%
entry = load_dataset(6)[0]
polygon = polygon_from_entry(entry)
reference = triangulation_from_entry(entry, polygon)
print(f"Reference triangulation total cost: {reference.total_cost():.3f}")
reference.draw()

model = mathopt.Model(name=f"min-length-triangulation-{len(polygon)}")

n = len(polygon)

costs = [[0.0] * n for _ in range(n)]

chords = valid_chords(polygon)
for chord in chords:
    i = chord.first
    j = chord.second
    # print(i, j)
    cost = chord.length
    costs[i][j] = cost
    # only the upper triangle is used
    # costs[j][i] = cost 

# print_costs(costs)

control_variables = list()
for chord in chords:
    control_variables.append(model. add_binary_variable(name=f"{chord.first}_{chord.second}"))

for chord, var in zip(chords, control_variables):
    model.objective.add_linear(chord.length * var)

# model.set_linear_objective(model.objective, is_maximize=False)

print("f = " + " + ".join(f"{term.coefficient:.2f} * {term.variable.name}" for term in model.objective.linear_terms()))

# diagonals count
model.add_linear_constraint(
    sum(var for var in control_variables) == n-3,
    name="diagonals_count"
)

# no crossing
# TODO: optimize the parsing
for i, chord_1 in enumerate(chords):
    for j in range(i+1, len(chords)):
        chord_2 = chords[j]
        if Triangulation._crosses(chord_1, chord_2):
            model.add_linear_constraint(
                control_variables[i] + control_variables[j] <= 1,
                name=f"no_crossing_{(chord_1.first, chord_1.second)}_{(chord_2.first, chord_2.second)}"
            )

params = mathopt.SolveParameters(enable_output=True)
result = mathopt.solve(opt_model=model, solver_type=mathopt.SolverType.HIGHS, params=params)
# print(result)

if result.termination.reason != mathopt.TerminationReason.OPTIMAL:
    raise RuntimeError(f"model failed to solve: {result.termination}")

print("MathOpt solve succeeded")
print("Objective value:", result.objective_value())

selected_chords: list[Chord] = []
for var, value in result.variable_values().items():
    if value == 1.0:
        chord = chords[var.id]
        selected_chords.append(chord)
        # print(chord.first, chord.second)
proposed_triangulation = Triangulation(polygon, selected_chords)
print(f"Proposed triangulation total cost: {proposed_triangulation.total_cost():.3f}")
proposed_triangulation.draw()
# %%

VERTEX_COUNT = 7
SHOW_PLOTS = True

for index, entry in enumerate(load_dataset(VERTEX_COUNT)):
    polygon = polygon_from_entry(entry)
    reference = triangulation_from_entry(entry, polygon)
    result = milp_triangulation(polygon)

    print(f"Sample {index}")
    print(f"Saved optimal cost:   {reference.total_cost():.3f}")
    print(f"MILP optimal cost: {result.triangulation.total_cost():.3f}")
    print(f"Dynamic chords: {result.triangulation.dump()}")
    print()

    if SHOW_PLOTS:
        reference.draw()
        result.triangulation.draw()
