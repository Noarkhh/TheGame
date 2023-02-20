from __future__ import annotations
import pygame as pg
from src.graphics.entity import Entity
from src.core.enums import *
if TYPE_CHECKING:
    from src.graphics.spritesheet import Spritesheet


class Entities(pg.sprite.Group):
    def __init__(self, spritesheet: Spritesheet):
        Entity.entities = self
        self.spritesheet: Spritesheet = spritesheet
        super().__init__()

    def draw(self, surface: pg.Surface) -> list[pg.Rect]:
        sprites = self.sprites()
        for spr in sorted(sprites, key=lambda spr: (spr.pos.y, spr.is_ghost)):
            self.spritedict[spr] = surface.blit(spr.image, spr.rect)
        self.lostsprites = []
        dirty = self.lostsprites

        return dirty

    def update_zoom(self) -> None:
        for spr in self.sprites():
            spr.update_zoom()
