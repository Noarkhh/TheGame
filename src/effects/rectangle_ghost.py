from __future__ import annotations
from src.effects.area_ghost import AreaGhost, T
from src.core.enums import Direction
from typing import TYPE_CHECKING, Generic
from src.core.vector import Vector


class RectangleGhost(AreaGhost, Generic[T]):
    def find_new_segments(self) -> None:
        if self.cursor.pos_difference == Vector(0, 0):
            return

        top_left: Vector[int] = Vector(min(self.origin.x, self.cursor.pos.x), min(self.origin.y, self.cursor.pos.y))
        bottom_right: Vector[int] = Vector(max(self.origin.x, self.cursor.pos.x), max(self.origin.y, self.cursor.pos.y))
        updated_segments_positions: set[tuple[int, int]] = {(x, y) for x in range(top_left.x, bottom_right.x + 1)
                                                            for y in range(top_left.y, bottom_right.y + 1)}

        self.update_segments(updated_segments_positions)

    def resolve(self) -> None:
        self.area_action.resolve([Vector(pos) for pos in self.segments])
        super().resolve()
