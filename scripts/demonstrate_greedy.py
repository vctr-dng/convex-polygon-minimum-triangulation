# %%
from polygon_triangulation.algorithms import greedy_triangulation
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
    greedy = greedy_triangulation(polygon)

    print(f"Sample {index}")
    print(f"Optimal cost: {reference.total_cost():.6f}")
    print(f"Greedy cost:  {greedy.total_cost():.6f}")
    print(f"Greedy chords: {greedy.dump()}")
    print()

    if SHOW_PLOTS:
        reference.draw()
        greedy.draw()
