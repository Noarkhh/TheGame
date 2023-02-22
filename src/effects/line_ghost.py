from src.effects.area_ghost import AreaGhost, T
from abc import ABC, abstractmethod, ABCMeta
from typing import TYPE_CHECKING, Generic
if TYPE_CHECKING:
    from src.core.vector import Vector


class LineGhost(AreaGhost, Generic[T], metaclass=ABCMeta):

    def update_segments(self) -> None:
        pass

    def resolve(self) -> None:
        def dist_from_origin(segment: T) -> int:
            return abs(segment.pos.x - self.origin.x) + abs(segment.pos.y - self.origin.y)

        tiles_to_affect: list[Vector[int]] = sorted(self.segments, key=dist_from_origin)
        self.area_effect.resolve(tiles_to_affect)

