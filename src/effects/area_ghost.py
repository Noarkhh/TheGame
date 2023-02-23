from __future__ import annotations
import pygame as pg
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Generic, TypeVar, Type
from src.graphics.tile_entity import TileEntity
from src.core.enums import Direction
from src.game_mechanics.snapper import Snapper
from src.core.vector import Vector

if TYPE_CHECKING:
    from src.game_mechanics.struct_manager import StructManager
    from src.core.cursor import Cursor
    from src.effects.area_action import AreaAction

T = TypeVar("T", bound=Snapper)


class AreaGhost(ABC, Generic[T]):
    struct_manager: StructManager
    cursor: Cursor
    segments: dict[tuple[int, int], T]
    origin: Vector[int]
    tile_entity_class: Type[T]
    area_action: AreaAction

    def __init__(self, cursor: Cursor, origin: Vector[int],
                 tile_entity_class: Type[T], area_effect: AreaAction) -> None:
        self.cursor = cursor
        self.segments = {}
        self.origin = origin
        self.area_action = area_effect
        self.tile_entity_class = tile_entity_class

    @abstractmethod
    def find_new_segments(self) -> None: ...

    def update_segments(self, updated_segments_positions: set[tuple[int, int]]) -> None:
        for (position, segment) in list(self.segments.items()):
            if position not in updated_segments_positions:
                segment.kill()
                self.remove_all_neighbours_from(position)
                self.segments.pop(position)
            else:
                updated_segments_positions.remove(position)

        for position in updated_segments_positions:
            self.segments[position] = self.tile_entity_class(Vector(position), is_ghost=True)
            self.add_all_neighbours_to(position)

    def resolve(self) -> None:
        for segment in self.segments.values():
            segment.kill()
        print("resolved!")

    def add_all_neighbours_to(self, position: tuple[int, int]) -> None:
        for direction in Direction:
            neighbouring_pos = (position[0] + direction.to_tuple()[0], position[1] + direction.to_tuple()[1])
            if neighbouring_pos in self.segments:
                self.segments[position].add_neighbours(direction)
                self.segments[neighbouring_pos].add_neighbours(direction.opposite())

    def remove_all_neighbours_from(self, position: tuple[int, int]) -> None:
        for direction in Direction:
            neighbouring_pos = (position[0] + direction.to_tuple()[0], position[1] + direction.to_tuple()[1])
            if neighbouring_pos in self.segments:
                self.segments[neighbouring_pos].remove_neighbours(direction.opposite())
