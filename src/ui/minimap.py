from __future__ import annotations
import pygame as pg
from typing import TYPE_CHECKING, Any
from src.ui.ui_element import UIElement

if TYPE_CHECKING:
    from src.game_mechanics.map_manager import MapManager
    from src.graphics.spritesheet import Spritesheet
    from src.graphics.scene import Scene
    from src.ui.button_manager import ButtonManager


class Minimap(UIElement):
    def __init__(self, map_manager: MapManager, spritesheet: Spritesheet, scene: Scene,
                 button_manager: ButtonManager, button_specs: dict[str, list]) -> None:
        self.map_manager: MapManager = map_manager
        self.scene: Scene = scene

        self.map_image: pg.Surface = pg.transform.scale(map_manager.layout, (128, 128))
        self.map_image_raw: pg.Surface = self.map_image.copy()
        self.frame: pg.Surface = spritesheet.get_ui_image("Decorative", "map_frame")

        self.visible_rectangle: pg.Surface = pg.Surface(
            ((self.ui.window_size.x / map_manager.map_size_px.x) * 128,
             (self.ui.window_size.y / map_manager.map_size_px.y) * 128))
        self.visible_rectangle.fill((198, 15, 24))
        cutout = pg.surface.Surface((self.visible_rectangle.get_width() - 4, self.visible_rectangle.get_height() - 4))
        cutout.fill((0, 0, 0))
        self.visible_rectangle.blit(cutout, (2, 2))
        self.visible_rectangle.set_colorkey("black")

        self.image: pg.Surface = pg.Surface(self.frame.get_size())
        self.image.set_colorkey("black")
        self.rect: pg.Rect = self.image.get_rect(topright=(self.ui.window_size.x, 44))
        super().__init__(self.image, self.rect, spritesheet, button_manager, button_specs)

    def load(self) -> None:
        self.map_image.blit(self.map_image_raw, (0, 0))
        self.map_image.blit(self.visible_rectangle,
                            ((self.scene.rect.x / self.map_manager.map_size_px.x) * 128,
                             (self.scene.rect.y / self.map_manager.map_size_px.y) * 128))

        self.image.blit(self.map_image, (self.image.get_width() - self.map_image.get_width(), 0))
        self.image.blit(self.frame, (0, 0))

    def draw(self, image: pg.Surface) -> None:
        self.load()
        super().draw(image)
