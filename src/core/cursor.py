from __future__ import annotations
import pygame as pg
from src.core.enums import *
from src.game_mechanics.demolisher import Demolisher
from enum import Enum, auto
from typing import Type
from random import randrange
from src.ui.button import Button

if TYPE_CHECKING:
    from src.graphics.scene import Scene
    from src.graphics.tile_entity import TileEntity
    from src.ui.ui import UI


class Mode(Enum):
    NORMAL = auto()
    DRAG = auto()


class Cursor(pg.sprite.Sprite):
    def __init__(self) -> None:
        super().__init__()
        self.ui: Optional[UI] = None
        self.mode: Mode = Mode.NORMAL
        self.image: pg.Surface = pg.transform.scale(pg.image.load("../assets/cursor2.png").convert(),
                                                    (Tile.size, Tile.size))
        self.image.set_colorkey("white")
        self.show_image: bool = True
        self.rect: pg.Rect = self.image.get_rect()

        self.pos: Vector[int] = Vector(0, 0)
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
        if issubclass(entity_class, Demolisher) and self.ui.toolbar.demolish_button is not None:
            self.ui.toolbar.demolish_button.lock(in_pressed_state=True)

    def unassign(self) -> None:
        if self.held_entity is not None:
            assert self.ui is not None
            if isinstance(self.held_entity, Demolisher) and self.ui.toolbar.demolish_button is not None:
                self.ui.toolbar.demolish_button.unlock()
            self.held_entity.kill()
            self.held_entity = None
            self.mode = Mode.NORMAL
            self.show_image = True

    def draw(self, surf: pg.Surface) -> None:
        if self.show_image:
            surf.blit(self.image, self.rect)
