from typing import Generic
from abc import ABCMeta

from src.core.enums import Orientation
from src.core.vector import Vector
from src.effects.area_ghost import AreaGhost, T


class LineGhost(AreaGhost[T], metaclass=ABCMeta):
    main_axis: Orientation = Orientation.VERTICAL
    listening_for_main_axis: bool = True

    def update_main_axis(self) -> None:
        if not self.listening_for_main_axis:
            return

        if abs(self.cursor.pos_difference.x) > abs(self.cursor.pos_difference.y):
            self.main_axis = Orientation.HORIZONTAL
        else:
            self.main_axis = Orientation.VERTICAL

        self.listening_for_main_axis = False

    def find_new_segments(self, initial: bool = False) -> None:
        if self.origin == self.cursor.pos:
            self.listening_for_main_axis = True
        if self.cursor.pos_difference == Vector(0, 0) and not initial:
            return
        self.update_main_axis()

        top_left: Vector[int] = Vector(min(self.origin.x, self.cursor.pos.x), min(self.origin.y, self.cursor.pos.y))
        bottom_right: Vector[int] = Vector(max(self.origin.x, self.cursor.pos.x), max(self.origin.y, self.cursor.pos.y))
        updated_segments_positions: set[tuple[int, int]] = set()

        if self.main_axis == Orientation.HORIZONTAL:
            for x in range(top_left.x, bottom_right.x + 1):
                updated_segments_positions.add((x, self.origin.y))
            x_const = top_left.x if top_left.x != self.origin.x else bottom_right.x
            for y in range(top_left.y, bottom_right.y + 1):
                updated_segments_positions.add((x_const, y))
        else:
            for y in range(top_left.y, bottom_right.y + 1):
                updated_segments_positions.add((self.origin.x, y))
            y_const = top_left.y if top_left.y != self.origin.y else bottom_right.y
            for x in range(top_left.x, bottom_right.x + 1):
                updated_segments_positions.add((x, y_const))

        self.update_segments(updated_segments_positions)

