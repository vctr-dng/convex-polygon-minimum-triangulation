"""Dataset loading and generation helpers."""

from __future__ import annotations

import json
from pathlib import Path

from .geometry import Polygon, Vertex
from .marimo.exhaustive import minimum_exhaustive_triangulation
from .triangulation import Triangulation

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATASET_DIRECTORY = PROJECT_ROOT / "dataset"


def load_dataset(
    vertex_count: int, directory: Path = DEFAULT_DATASET_DIRECTORY
) -> list[dict]:
    path = directory / f"{vertex_count}.json"
    entries = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(entries, list):
        raise TypeError(f"Dataset {path} must contain a JSON list.")
    return entries


def polygon_from_entry(entry: dict) -> Polygon:
    try:
        return Polygon(Vertex(point[0], point[1]) for point in entry["polygon"])
    except (KeyError, IndexError, TypeError) as error:
        raise ValueError("Dataset entry has an invalid polygon.") from error


def triangulation_from_entry(entry: dict, polygon: Polygon) -> Triangulation:
    try:
        return Triangulation.from_json(json.dumps(entry["triangulation"]), polygon)
    except KeyError as error:
        raise ValueError("Dataset entry has no triangulation.") from error


def generate_entry(vertex_count: int, radius: float = 5.0) -> dict:
    polygon = Polygon.random(radius, vertex_count)
    triangulation = minimum_exhaustive_triangulation(polygon)
    return {
        "polygon": polygon.dump(),
        "triangulation": triangulation.dump(),
        "cost": triangulation.total_cost(),
    }


def append_entry(entry: dict, directory: Path = DEFAULT_DATASET_DIRECTORY) -> int:
    polygon = polygon_from_entry(entry)
    triangulation = triangulation_from_entry(entry, polygon)
    expected_cost = entry.get("cost")
    if (
        expected_cost is not None
        and abs(float(expected_cost) - triangulation.total_cost()) > 1e-9
    ):
        raise ValueError("Dataset entry cost does not match its triangulation.")

    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{len(polygon)}.json"
    entries = load_dataset(len(polygon), directory) if path.exists() else []
    entries.append(entry)
    path.write_text(json.dumps(entries, indent=4), encoding="utf-8")
    return len(entries)


def extend_dataset(
    vertex_count: int,
    samples: int,
    radius: float = 5.0,
    directory: Path = DEFAULT_DATASET_DIRECTORY,
) -> int:
    """Top up the file for ``vertex_count`` to ``samples`` entries, writing once."""

    path = directory / f"{vertex_count}.json"
    entries = load_dataset(vertex_count, directory) if path.exists() else []
    while len(entries) < samples:
        entries.append(generate_entry(vertex_count, radius))
    directory.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(entries, indent=4), encoding="utf-8")
    return len(entries)
