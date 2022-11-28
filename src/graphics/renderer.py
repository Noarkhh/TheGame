from __future__ import annotations
import pygame as pg
from src.core_classes import Vector
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.graphics.entities import Entities
    from src.graphics.scene import Scene
    from src.cursor import Cursor
    from src.ui.ui import UI


class Renderer:
    def __init__(self, scene: Scene, screen: pg.Surface, entities: Entities, cursor: Cursor, ui: UI) -> None:
        self.scene: Scene = scene
        self.screen: pg.Surface = screen

        self.entities: Entities = entities
        self.cursor: Cursor = cursor
        self.ui: UI = ui

    def render(self) -> None:
        self.entities.draw(self.scene.map_image)
        self.cursor.update(self.scene)
        self.cursor.draw(self.scene.map_image)
        self.screen.blit(self.scene.image, (0, 0))
        self.scene.reset_image()

        self.ui.draw_elements(self.screen)

        pg.display.flip()
