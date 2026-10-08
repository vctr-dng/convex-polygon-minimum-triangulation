# %%
from polygon_triangulation.dataset import extend_dataset

# %%
MIN_VERTEX_COUNT = 4
MAX_VERTEX_COUNT = 30
SAMPLES_PER_SIZE = 100
RADIUS = 5.0

for vertex_count in range(MIN_VERTEX_COUNT, MAX_VERTEX_COUNT + 1):
    total = extend_dataset(vertex_count, SAMPLES_PER_SIZE, RADIUS)
    print(f"{vertex_count}-vertex polygons: {total} entries.")
