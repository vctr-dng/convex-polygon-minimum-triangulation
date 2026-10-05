# %%
from polygon_triangulation.algorithms import dynamic_triangulation
from polygon_triangulation.dataset import (
    load_dataset,
    polygon_from_entry,
    triangulation_from_entry,
)

# %%
VERTEX_COUNT = 7
SHOW_PLOTS = True

for index, entry in enumerate(load_dataset(VERTEX_COUNT)):
    polygon = polygon_from_entry(entry)
    reference = triangulation_from_entry(entry, polygon)
    result = dynamic_triangulation(polygon)

    print(f"Sample {index}")
    print(f"Saved optimal cost:   {reference.total_cost():.3f}")
    print(f"Dynamic optimal cost: {result.triangulation.total_cost():.3f}")
    print(f"Dynamic chords: {result.triangulation.dump()}")
    print(f"Cost table: {result.cost_table}")
    print()

    if SHOW_PLOTS:
        reference.draw()
        result.triangulation.draw()
