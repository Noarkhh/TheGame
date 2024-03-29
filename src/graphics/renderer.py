from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

if TYPE_CHECKING:
    from src.entities.entities import Entities
    from src.graphics.scene import Scene
    from src.core.cursor import Cursor
    from src.ui.ui import UI


class Renderer:
    def __init__(self, scene: Scene, screen: pg.Surface, entities: Entities, cursor: Cursor, ui: UI) -> None:
        self.scene: Scene = scene
        self.screen: pg.Surface = screen

        self.entities: Entities = entities
        self.cursor: Cursor = cursor
        self.ui: UI = ui

    def render(self) -> None:
        self.scene.reset_image()
        self.entities.draw(self.scene.map_image)
        self.cursor.update(self.scene)
        self.screen.blit(self.scene.image, (0, 0))

        self.ui.draw_elements()

        pg.display.flip()
