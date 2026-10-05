# %%
from polygon_triangulation.algorithms import (
    exhaustive_triangulations,
    minimum_exhaustive_triangulation,
)
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
    triangulations = exhaustive_triangulations(polygon)
    minimum = minimum_exhaustive_triangulation(polygon)

    print(f"Sample {index}")
    print(f"Valid triangulations: {len(triangulations)}")
    print(f"Saved optimal cost:      {reference.total_cost():.3f}")
    print(f"Exhaustive optimal cost: {minimum.total_cost():.3f}")
    print(f"Exhaustive chords: {minimum.dump()}")

    if SHOW_PLOTS:
        reference.draw()
        minimum.draw()
