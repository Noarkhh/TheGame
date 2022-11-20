from __future__ import annotations
import pygame as pg
from src.core_classes import *
from src.game_mechanics.structures import Wall, Road, Bridge, Farmland
from enum import Enum, auto
from typing import Type
from random import randrange

if TYPE_CHECKING:
    from src.graphics.scene import Scene
    from src.game_mechanics.structures import Structure


class Mode(Enum):
    NORMAL = auto()
    DEMOLISH = auto()
    DRAG = auto()


class Cursor(pg.sprite.Sprite):
    def __init__(self) -> None:
        super().__init__()
        self.mode: Mode = Mode.NORMAL
        self.image: pg.Surface = pg.transform.scale(pg.image.load("../assets/cursor2.png").convert(),
                                                    (Tile.size, Tile.size))
        self.image.set_colorkey("white")
        self.image_demolish: pg.Surface = pg.transform.scale(pg.image.load("../assets/cursor_demolish.png").convert(),
                                                             (Tile.size, Tile.size))
        self.image_demolish.set_colorkey("white")
        self.image_demolish.set_alpha(128)
        self.rect: pg.Rect = self.image.get_rect()

        self.pos: Vector[int] = Vector(0, 0)
        self.previous_pos: Vector[int] = Vector(0, 0)
        self.pos_difference: Vector[int] = Vector(0, 0)

        self.pos_px: Vector[int] = Vector(pg.mouse.get_pos())
        self.previous_pos_px: Vector[int] = Vector(pg.mouse.get_pos())
        self.pos_px_difference: Vector[int] = Vector(0, 0)

        self.held_structure: Optional[Structure] = None

    def update(self, scene: Scene):
        self.previous_pos = self.pos
        self.previous_pos_px = self.pos_px

        self.pos = (Vector(pg.mouse.get_pos()) + Vector(scene.rect.topleft)) // Tile.size
        self.pos_px = Vector(pg.mouse.get_pos())
        self.pos_difference = self.pos - self.previous_pos
        self.pos_px_difference = self.pos_px - self.previous_pos_px
        self.rect.topleft = (self.pos * Tile.size).to_tuple()
        if self.held_structure is not None:
            self.held_structure.pos = self.pos
            self.held_structure.update_rect()

    def assign_struct_class(self, struct_class: Type[Structure]):
        if self.held_structure is not None:
            self.held_structure.kill()
        self.held_structure = struct_class(self.pos, image_variant=randrange(struct_class.image_variants),
                                           is_ghost=True)
        if type(struct_class) in (Wall, Road, Bridge, Farmland):
            self.mode = Mode.DRAG
        else:
            self.mode = Mode.NORMAL

    def unassign(self):
        self.held_structure.kill()
        self.held_structure = None

    def draw(self, surf: pg.Surface):
        surf.blit(self.image, self.rect)
