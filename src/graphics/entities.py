from __future__ import annotations
import pygame as pg
from typing import ClassVar
from abc import ABC
from src.core_classes import *
if TYPE_CHECKING:
    from src.graphics.spritesheet import Spritesheet


class Entity(ABC, pg.sprite.Sprite):
    image_aspect_ratio: ClassVar[Vector[float]] = Vector[float](1, 1)
    covered_tiles: ClassVar[list[Vector[int]]] = [Vector[int](0, 0)]
    image_variants: int = 1

    entities: ClassVar[Entities]

    def __init__(self, pos: Vector[int], image_variant: int, is_ghost: bool) -> None:
        super().__init__()
        self.pos: Vector[int] = pos
        self.is_ghost: bool = is_ghost

        self.image_variant: int = image_variant
        self.image: pg.Surface = self.get_image()
        self.rect: pg.Rect = self.image.get_rect(bottomright=((self.pos + (1, 1)) * Tile.size).to_tuple())
        self.entities.add(self)

    def get_image(self) -> pg.Surface:
        image: pg.Surface = self.entities.spritesheet.get_image(self)
        if self.is_ghost:
            image.set_alpha(128)
        return image

    def update_zoom(self) -> None:
        self.image = pg.transform.scale(self.image, (self.image_aspect_ratio * Tile.size).to_tuple())
        self.update_rect()

    def update_rect(self) -> None:
        self.rect = self.image.get_rect(bottomright=((self.pos + (1, 1)) * Tile.size).to_tuple())


class Entities(pg.sprite.Group):
    def __init__(self, spritesheet: Spritesheet):
        Entity.entities = self
        self.spritesheet: Spritesheet = spritesheet
        super().__init__()

    def draw(self, surface: pg.Surface) -> list[pg.Rect]:
        sprites = self.sprites()
        for spr in sorted(sprites, key=lambda spr: spr.pos.y):
            self.spritedict[spr] = surface.blit(spr.image, spr.rect)
        self.lostsprites = []
        dirty = self.lostsprites

        return dirty

    def update_zoom(self):
        for spr in self.sprites():
            spr.update_zoom()
