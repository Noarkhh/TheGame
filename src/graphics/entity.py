from __future__ import annotations
import pygame as pg
from typing import ClassVar
from abc import ABC, abstractmethod
from src.core.enums import *
if TYPE_CHECKING:
    from src.graphics.entities import Entities


class Entity(ABC, pg.sprite.Sprite):
    image_aspect_ratio: ClassVar[Vector[float]] = Vector[float](1, 1)
    covered_tiles: ClassVar[list[Vector[int]]] = [Vector[int](0, 0)]
    image_variants: int = 1

    entities: ClassVar[Entities]

    def __init__(self, rect_bottom_right: Vector[int], image_variant: int, alpha: int) -> None:
        super().__init__()
        self.alpha: int = alpha

        self.image_variant: int = image_variant
        self.image: pg.Surface = self.get_image()
        self.rect: pg.Rect = self.image.get_rect(bottomright=rect_bottom_right.to_tuple())
        self.entities.add(self)

    def get_image(self) -> pg.Surface:
        image: pg.Surface = self.entities.spritesheet.get_image(self)
        if self.alpha < 255:
            image.set_alpha(self.alpha)
        return image

    def update_zoom(self) -> None:
        self.image = pg.transform.scale(self.image, (self.image_aspect_ratio * Tile.size).to_tuple())
        self.update_rect()

    @abstractmethod
    def update_rect(self) -> None: ...
