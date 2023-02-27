from __future__ import annotations

from src.core.enums import Direction, DirectionSet
from src.core.vector import Vector
from src.entities.snapper import Snapper
from src.entities.tile_entity import DragShape


class Demolisher(Snapper):
    is_draggable = True
    drag_shape = DragShape.RECTANGLE
    neighbours: DirectionSet

    def __init__(self, pos: Vector[int], image_variant: int = 0, is_ghost: bool = True):
        self.neighbours = DirectionSet()
        super().__init__(pos, image_variant, is_ghost)

    def add_neighbours(self, neighbours: DirectionSet | set | Direction) -> None:
        if isinstance(neighbours, Direction):
            self.neighbours.add(neighbours)
        else:
            self.neighbours.update(neighbours)
        self.image = self.get_image()

    def remove_neighbours(self, neighbours: DirectionSet | set | Direction) -> None:
        if isinstance(neighbours, Direction):
            self.neighbours.remove(neighbours)
        else:
            self.neighbours.difference_update(neighbours)
        self.image = self.get_image()
