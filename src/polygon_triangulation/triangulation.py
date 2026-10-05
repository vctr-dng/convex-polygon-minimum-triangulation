"""Validated triangulations of convex polygons."""

from __future__ import annotations

import json
from collections.abc import Iterable

from .geometry import Chord, Polygon


class Triangulation:
    def __init__(self, polygon: Polygon, chords: Iterable[Chord] = ()):
        self.polygon = polygon
        self.chords: list[Chord] = []
        for chord in chords:
            if chord.polygon != polygon or not self.add_chord(
                chord.first, chord.second
            ):
                raise ValueError(
                    "The supplied chords do not form a valid triangulation prefix."
                )

    def copy(self) -> Triangulation:
        return Triangulation(self.polygon, self.chords)

    @staticmethod
    def _crosses(first: Chord, second: Chord) -> bool:
        if {first.first, first.second} & {second.first, second.second}:
            return False
        return (first.first < second.first < first.second < second.second) or (
            second.first < first.first < second.second < first.second
        )

    def valid_chord(self, first: int, second: int) -> bool:
        try:
            candidate = Chord(self.polygon, first, second)
        except (IndexError, TypeError, ValueError):
            return False
        if not candidate.is_diagonal or candidate in self.chords:
            return False
        return not any(self._crosses(candidate, chord) for chord in self.chords)

    def add_chord(self, first: int, second: int) -> bool:
        if not self.valid_chord(first, second):
            return False
        self.chords.append(Chord(self.polygon, first, second))
        return True

    def complete(self) -> bool:
        return len(self.chords) == len(self.polygon) - 3

    def total_cost(self) -> float:
        return sum(chord.length for chord in self.chords)

    def dump(self) -> list[list[int]]:
        return [chord.dump() for chord in self.chords]

    def to_json(self) -> str:
        return json.dumps(self.dump(), indent=4)

    @classmethod
    def from_json(cls, value: str, polygon: Polygon) -> Triangulation:
        chords = json.loads(value)
        if not isinstance(chords, list):
            raise TypeError("A triangulation must be a JSON list of chords.")
        triangulation = cls(polygon)
        for indices in chords:
            if not isinstance(indices, list) or len(indices) != 2:
                raise ValueError("Each triangulation chord must contain two indices.")
            if not triangulation.add_chord(indices[0], indices[1]):
                raise ValueError("The saved triangulation contains an invalid chord.")
        if not triangulation.complete():
            raise ValueError("The saved triangulation is incomplete.")
        return triangulation

    def draw(self, show: bool = True):
        import matplotlib.pyplot as plt

        figure, axis = self.polygon.draw(show=False)
        for chord in self.chords:
            first = self.polygon.vertex(chord.first)
            second = self.polygon.vertex(chord.second)
            axis.plot([first.x, second.x], [first.y, second.y], color="tab:blue")
        if show:
            plt.show()
        return figure, axis
