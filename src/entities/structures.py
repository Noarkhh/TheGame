from __future__ import annotations

from typing import ClassVar, Any, TYPE_CHECKING, Optional

import pygame as pg

from src.core.enums import Terrain, Direction, DirectionSet, Orientation, Message
from src.core.vector import Vector
from src.entities.structure import Structure
from src.entities.structure_snapper import StructureSnapper
from src.entities.tile_entity import DragShape

if TYPE_CHECKING:
    pass


class House(Structure):
    image_aspect_ratio = Vector[float](1, 21 / 15)
    image_variants = 2


class Mine(Structure):
    image_aspect_ratio = Vector[float](1, 2)


class Sawmill(Structure):
    image_aspect_ratio = Vector[float](2, 1)
    covered_tiles = [Vector[int](0, 0), Vector[int](-1, 0)]


class Tower(Structure):
    image_aspect_ratio = Vector[float](1, 2)


class Wall(StructureSnapper):
    is_draggable = True
    drag_shape: ClassVar[Optional[DragShape]] = DragShape.LINE


class Road(StructureSnapper):
    is_draggable = True
    drag_shape: ClassVar[Optional[DragShape]] = DragShape.LINE


class Farmland(StructureSnapper):
    is_draggable = True
    drag_shape: ClassVar[Optional[DragShape]] = DragShape.RECTANGLE


class Bridge(Road):
    unsuitable_terrain = [Terrain.GRASSLAND, Terrain.DESERT]

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.snaps_to = {direction: Road for direction in Direction}


class Gate(Wall, Road):
    image_aspect_ratio = Vector[float](1, 20 / 15)
    overrider = True

    is_draggable = False
    drag_shape = None

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        # print(self.__class__.__mro__)
        if self.orientation == Orientation.VERTICAL:
            self.snaps_to = {Direction.N: Road, Direction.E: Wall, Direction.S: Road, Direction.W: Wall}
        elif self.orientation == Orientation.HORIZONTAL:
            self.snaps_to = {Direction.N: Wall, Direction.E: Road, Direction.S: Wall, Direction.W: Road}
        self.directions_to_connect_to: DirectionSet = DirectionSet()

    def can_override(self) -> bool:
        struct_map = self.manager.map_manager.struct_map
        self.directions_to_connect_to.clear()

        if not type(struct_map[self.pos]) in (Wall, Road):
            return False

        for direction_to_neighbour in Direction:
            neighbour_pos = self.pos + direction_to_neighbour.to_vector()
            neighbour = struct_map[neighbour_pos]
            if isinstance(neighbour, StructureSnapper) and direction_to_neighbour.opposite() in neighbour.neighbours:
                if self.snaps_to[direction_to_neighbour] != neighbour.snaps_to[direction_to_neighbour.opposite()]:
                    return False
                self.directions_to_connect_to.add(direction_to_neighbour)

        return True

    def can_be_placed(self) -> Message:
        message = super().can_be_placed()
        if message == Message.BAD_LOCATION_STRUCT and self.can_override():
            message = Message.OVERRODE
        return message

    def rotate(self) -> None:
        if self.orientation == Orientation.VERTICAL:
            self.orientation = Orientation.HORIZONTAL
            self.snaps_to = {Direction.N: Wall, Direction.E: Road, Direction.S: Wall, Direction.W: Road}
        elif self.orientation == Orientation.HORIZONTAL:
            self.orientation = Orientation.VERTICAL
            self.snaps_to = {Direction.N: Road, Direction.E: Wall, Direction.S: Road, Direction.W: Wall}

        self.image_variant = self.orientation
        self.image: pg.Surface = self.get_image()
