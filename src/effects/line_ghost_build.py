from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

from src.core.vector import Vector
from src.effects.line_ghost import LineGhost
from src.game_mechanics.structure_snapper import StructureSnapper

if TYPE_CHECKING:
    pass

S = TypeVar("S", bound=StructureSnapper)


class LineGhostBuild(LineGhost[S]):

    def resolve(self) -> None:
        def dist_from_origin(segment: tuple[int, int]) -> int:
            return abs(segment[0] - self.origin.x) + abs(segment[1] - self.origin.y)

        segments_to_build: list[Vector] = [Vector(pos) for pos in sorted(self.segments, key=dist_from_origin)]

        self.kill_segments()
