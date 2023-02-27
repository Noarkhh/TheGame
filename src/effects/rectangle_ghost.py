from __future__ import annotations

from abc import ABCMeta
from typing import Generic

from src.core.vector import Vector
from src.effects.area_ghost import AreaGhost, T


class RectangleGhost(AreaGhost[T], metaclass=ABCMeta):
    def find_new_segments(self, initial: bool = False) -> None:
        if self.cursor.pos_difference == Vector(0, 0) and not initial:
            return

        top_left: Vector[int] = Vector(min(self.origin.x, self.cursor.pos.x), min(self.origin.y, self.cursor.pos.y))
        bottom_right: Vector[int] = Vector(max(self.origin.x, self.cursor.pos.x), max(self.origin.y, self.cursor.pos.y))
        updated_segments_positions: set[tuple[int, int]] = {(x, y) for x in range(top_left.x, bottom_right.x + 1)
                                                            for y in range(top_left.y, bottom_right.y + 1)}

        self.update_segments(updated_segments_positions)
