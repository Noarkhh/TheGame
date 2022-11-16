from __future__ import annotations
import pygame as pg


class Entities(pg.sprite.Group):
    def draw(self, surface: pg.Surface) -> list[pg.Rect]:
        sprites = self.sprites()
        for spr in sorted(sprites, key=lambda spr: spr.pos.x):
            self.spritedict[spr] = surface.blit(spr.image, spr.rect)
        self.lostsprites = []
        dirty = self.lostsprites

        return dirty
