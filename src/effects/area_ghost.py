import pygame as pg
from abc import ABC
from typing import TYPE_CHECKING, Generic, TypeVar
if TYPE_CHECKING:
    from src.game_mechanics.struct_manager import StructManager
    from src.core.cursor import Cursor
    from src.graphics.entity import Entity

T = TypeVar("T", bound=Entity)


class AreaGhost(ABC, Generic[T]):
    struct_manager: StructManager
    cursor: Cursor
    segments: pg.sprite.Group[T]

    def __init__(self, struct_manager: StructManager, cursor: Cursor) -> None:
        self.struct_manager = struct_manager
        self.cursor = cursor
        self.segments = pg.sprite.Group()
