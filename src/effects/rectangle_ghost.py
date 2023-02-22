from src.effects.area_ghost import AreaGhost, T
from abc import ABC, abstractmethod, ABCMeta
from typing import TYPE_CHECKING, Generic
if TYPE_CHECKING:
    from src.core.vector import Vector


class RectangleGhost(AreaGhost, Generic[T], metaclass=ABCMeta):

    def update_segments(self) -> None:
        top_left: Vector[int] = Vector(min(self.origin.x, self.cursor.pos.x), min(self.origin.y, self.cursor.pos.y))
        bottom_right: Vector[int] = Vector(max(self.origin.x, self.cursor.pos.x), max(self.origin.y, self.cursor.pos.y))
        updated_segments_positions: set = {(x, y) for x in range(top_left.x, bottom_right.x)
                                           for y in range(top_left.y, bottom_right.y)}

        print(updated_segments_positions)

    def resolve(self) -> None:
        self.area_effect.resolve(list(self.segments))
