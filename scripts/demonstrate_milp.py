# %%

from polygon_triangulation.algorithms import milp_triangulation
from polygon_triangulation.dataset import (
    load_dataset,
    polygon_from_entry,
    triangulation_from_entry,
)

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
