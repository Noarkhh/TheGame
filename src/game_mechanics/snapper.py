from __future__ import annotations
from typing import Type, Any
from src.core.enums import *
from src.graphics.tile_entity import TileEntity


class Snapper(TileEntity):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.snaps_to: dict[Direction, Type[TileEntity]] = {direction: self.__class__ for direction in Direction}
        self.neighbours: DirectionSet = DirectionSet()
        super().__init__(*args, **kwargs)

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
