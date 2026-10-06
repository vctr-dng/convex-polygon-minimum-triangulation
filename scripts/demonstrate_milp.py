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

polygon = Polygon.random(5, 5)
polygon.draw()

# %%

costs = [[0.0] * len(polygon) for _ in range(len(polygon))]

# print_costs(costs)

chords = valid_chords(polygon)
for chord in chords:
    i = chord.first
    j = chord.second
    cost = chord.length
    costs[i][j] = cost
    costs[j][i] = cost

print_costs(costs)

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
