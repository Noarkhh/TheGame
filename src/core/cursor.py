from __future__ import annotations

from enum import Enum, auto
from random import randrange
from typing import Type, TYPE_CHECKING, Optional

import pygame as pg

from src.core.enums import Tile
from src.core.vector import Vector
from src.entities.demolisher import Demolisher
from src.entities.tile_entity import TileEntity
from src.ui.button import Button

if TYPE_CHECKING:
    from src.graphics.scene import Scene
    from src.entities.tile_entity import TileEntity
    from src.ui.ui import UI


class Mode(Enum):
    NORMAL = auto()
    DRAG = auto()


class Cursor(TileEntity):
    def __init__(self) -> None:
        super().__init__(Vector(0, 0), 1, False)
        self.ui: Optional[UI] = None
        self.mode: Mode = Mode.NORMAL

        self.show_image: bool = True

        self.previous_pos: Vector[int] = Vector(0, 0)
        self.pos_difference: Vector[int] = Vector(0, 0)

        self.pos_px: Vector[int] = Vector(pg.mouse.get_pos())
        self.previous_pos_px: Vector[int] = Vector(pg.mouse.get_pos())
        self.pos_px_difference: Vector[int] = Vector(0, 0)

        self.held_entity: Optional[TileEntity] = None

    def update(self, scene: Scene) -> None:
        self.previous_pos = self.pos
        self.previous_pos_px = self.pos_px

        self.pos = (Vector(pg.mouse.get_pos()) + Vector(scene.rect.topleft)) // Tile.size
        self.pos_px = Vector(pg.mouse.get_pos())
        self.pos_difference = self.pos - self.previous_pos
        self.pos_px_difference = self.pos_px - self.previous_pos_px
        self.rect.topleft = (self.pos * Tile.size).to_tuple()
        if self.held_entity is not None:
            self.held_entity.pos = self.pos
            self.held_entity.update_rect()

    def assign_entity_class(self, entity_class: Type[TileEntity], button: Optional[Button] = None) -> None:
        self.unassign()
        self.held_entity = entity_class(self.pos, image_variant=randrange(entity_class.image_variants), is_ghost=True)

        if entity_class.is_draggable:
            self.mode = Mode.DRAG
            self.show_image = False
        else:
            self.mode = Mode.NORMAL

        assert self.ui is not None
        if issubclass(entity_class, Demolisher) and self.ui.toolbar.named_buttons.demolish is not None:
            self.ui.toolbar.named_buttons.demolish.lock(in_pressed_state=True)

    def unassign(self) -> None:
        if self.held_entity is not None:
            assert self.ui is not None
            if isinstance(self.held_entity, Demolisher) and self.ui.toolbar.named_buttons.demolish is not None:
                self.ui.toolbar.named_buttons.demolish.unlock()
            self.held_entity.kill()
            self.held_entity = None
            self.mode = Mode.NORMAL
            self.show_image = True

    def draw(self, surf: pg.Surface) -> None:
        if self.held_entity is None or not self.held_entity.is_draggable:
            surf.blit(self.image, self.rect)
