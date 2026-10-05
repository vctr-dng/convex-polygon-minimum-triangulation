# Convex Polygon Minimum Triangulation

Advanced algorithms class project (S2 2023).

Compares exhaustive search (naive), greedy selection, and dynamic programming for minimum-length triangulation of convex polygons.

## Requirements

- [uv](https://docs.astral.sh/uv/)

## Setup

```bash
uv sync
```

## Usage

Run the `# %%` scripts directly or open them in an editor with Python cell support.

The scripts are designed to be launched as a python script or through the [VSCode Interactive window](https://code.visualstudio.com/docs/python/jupyter-support-py) feature.

### Generate the dataset

```bash
uv run python scripts/generate_dataset.py
```

### Run the algorithms

```bash
uv run python scripts/demonstrate_greedy.py
uv run python scripts/demonstrate_exhaustive.py
uv run python scripts/demonstrate_dynamic.py
```

The greedy algorithm produces a valid triangulation but is not guaranteed to be optimal.

The exhaustive algorithm is naive and slow for large polygons.

The dynamic programming algorithm is faster and more efficient than the exhaustive algorithm.
