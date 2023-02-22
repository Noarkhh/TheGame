from __future__ import annotations
import pygame as pg
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Generic, TypeVar
from src.graphics.tile_entity import TileEntity

if TYPE_CHECKING:
    from src.game_mechanics.struct_manager import StructManager
    from src.core.cursor import Cursor
    from src.core.vector import Vector
    from src.effects.area_effect import AreaEffect

T = TypeVar("T", bound=TileEntity)


class AreaGhost(ABC, Generic[T]):
    struct_manager: StructManager
    cursor: Cursor
    segments: pg.sprite.Group[T]
    origin: Vector[int]
    area_effect: AreaEffect

    def __init__(self, cursor: Cursor, origin: Vector[int], area_effect: AreaEffect) -> None:
        self.cursor = cursor
        self.segments = pg.sprite.Group()
        self.origin = origin
        self.area_effect = area_effect

    @abstractmethod
    def update_segments(self) -> None: ...

    @abstractmethod
    def resolve(self) -> None: ...

