from __future__ import annotations
import pygame as pg
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.graphics.entities import Entities
    from src.graphics.scene import Scene


class Renderer:
    def __init__(self, entities: Entities, scene: Scene, screen: pg.Surface):
        self.entities: Entities = entities
        self.scene: Scene = scene
        self.screen: pg.Surface = screen

    def render(self):
        pass

