#%%
from polygon_triangulation.dataset import append_entry, generate_entry


#%%
MIN_VERTEX_COUNT = 4
MAX_VERTEX_COUNT = 9
SAMPLES_PER_SIZE = 10
RADIUS = 5.0

for vertex_count in range(MIN_VERTEX_COUNT, MAX_VERTEX_COUNT + 1):
    for sample in range(SAMPLES_PER_SIZE):
        entry = generate_entry(vertex_count, RADIUS)
        total = append_entry(entry)
        print(
            f"Saved {vertex_count}-vertex sample {sample + 1}/{SAMPLES_PER_SIZE} ({total} entries)."
        )
