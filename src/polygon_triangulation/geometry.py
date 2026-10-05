from __future__ import annotations

from dataclasses import dataclass
import json
from math import cos, pi, sin
from typing import Iterable, Sequence
import random


@dataclass(frozen=True)
class Vertex:
    x: float
    y: float

    def distance_to(self, other: "Vertex", p: int = 2) -> float:
        if p <= 0:
            raise ValueError("The Minkowski norm must be positive.")
        return (abs(self.x - other.x) ** p + abs(self.y - other.y) ** p) ** (1 / p)

    def dump(self) -> list[float]:
        return [self.x, self.y]

    def to_json(self) -> str:
        return json.dumps(self.dump(), indent=4)

    @classmethod
    def from_json(cls, value: str) -> "Vertex":
        point = json.loads(value)
        if not isinstance(point, list) or len(point) != 2:
            raise ValueError("A vertex must be a two-value JSON list.")
        return cls(point[0], point[1])


@dataclass(frozen=True)
class Polygon:
    vertices: tuple[Vertex, ...]

    def __init__(self, vertices: Iterable[Vertex]):
        points = tuple(vertices)
        if len(points) < 3:
            raise ValueError("A polygon requires at least three vertices.")
        if len(set(points)) != len(points):
            raise ValueError("A polygon cannot contain duplicate vertices.")
        if not self._is_strictly_convex(points):
            raise ValueError(
                "Vertices must describe a strictly convex polygon in boundary order."
            )
        object.__setattr__(self, "vertices", points)

    @staticmethod
    def _is_strictly_convex(vertices: Sequence[Vertex]) -> bool:
        signs: list[bool] = []
        count = len(vertices)
        for index in range(count):
            first = vertices[index]
            second = vertices[(index + 1) % count]
            third = vertices[(index + 2) % count]
            cross = (second.x - first.x) * (third.y - second.y) - (
                second.y - first.y
            ) * (third.x - second.x)
            if cross == 0:
                return False
            signs.append(cross > 0)
        return all(signs) or not any(signs)

    def __len__(self) -> int:
        return len(self.vertices)

    def validate_index(self, index: int) -> None:
        if not isinstance(index, int) or isinstance(index, bool):
            raise TypeError("A vertex index must be an integer.")
        if not 0 <= index < len(self):
            raise IndexError(f"Vertex index {index} is outside the polygon.")

    def vertex(self, index: int) -> Vertex:
        self.validate_index(index)
        return self.vertices[index]

    def is_edge(self, first: int, second: int) -> bool:
        self.validate_index(first)
        self.validate_index(second)
        return abs(first - second) in (1, len(self) - 1)

    def dump(self) -> list[list[float]]:
        return [vertex.dump() for vertex in self.vertices]

    def to_json(self) -> str:
        return json.dumps(self.dump(), indent=4)

    @classmethod
    def from_json(cls, value: str) -> "Polygon":
        points = json.loads(value)
        if not isinstance(points, list):
            raise ValueError("A polygon must be a JSON list of vertices.")
        return cls(Vertex(point[0], point[1]) for point in points)

    @classmethod
    def regular(cls, radius: float, vertex_count: int) -> "Polygon":
        if radius <= 0:
            raise ValueError("The radius must be positive.")
        return cls(
            Vertex(
                radius * cos(2 * pi * index / vertex_count),
                radius * sin(2 * pi * index / vertex_count),
            )
            for index in range(vertex_count)
        )

    @classmethod
    def random(cls, radius: float, vertex_count: int) -> "Polygon":
        if radius <= 0:
            raise ValueError("The radius must be positive.")
        angles = sorted(random.uniform(0, 2 * pi) for _ in range(vertex_count))
        return cls(Vertex(radius * cos(angle), radius * sin(angle)) for angle in angles)

    def draw(self, show: bool = True):
        import matplotlib.pyplot as plt
        from matplotlib.patches import Polygon as MatplotlibPolygon

        figure, axis = plt.subplots()
        axis.add_patch(
            MatplotlibPolygon(
                [(vertex.x, vertex.y) for vertex in self.vertices],
                edgecolor="black",
                facecolor="white",
            )
        )
        for index, vertex in enumerate(self.vertices):
            axis.plot(vertex.x, vertex.y, "bo")
            axis.annotate(
                str(index),
                (vertex.x, vertex.y),
                xytext=(5, 5),
                textcoords="offset points",
                color="green",
            )
        axis.set_aspect("equal", adjustable="box")
        axis.autoscale_view()
        axis.axis("off")
        if show:
            plt.show()
        return figure, axis


@dataclass(frozen=True)
class Chord:
    polygon: Polygon
    first: int
    second: int

    def __init__(self, polygon: Polygon, first: int, second: int):
        polygon.validate_index(first)
        polygon.validate_index(second)
        if first == second:
            raise ValueError("A chord requires two distinct vertices.")
        object.__setattr__(self, "polygon", polygon)
        object.__setattr__(self, "first", min(first, second))
        object.__setattr__(self, "second", max(first, second))

    @property
    def is_diagonal(self) -> bool:
        return not self.polygon.is_edge(self.first, self.second)

    @property
    def length(self) -> float:
        return self.polygon.vertex(self.first).distance_to(
            self.polygon.vertex(self.second)
        )

    def dump(self) -> list[int]:
        return [self.first, self.second]

    def to_json(self) -> str:
        return json.dumps(self.dump(), indent=4)

    @classmethod
    def from_json(cls, value: str, polygon: Polygon) -> "Chord":
        indices = json.loads(value)
        if not isinstance(indices, list) or len(indices) != 2:
            raise ValueError("A chord must be a two-index JSON list.")
        return cls(polygon, indices[0], indices[1])
