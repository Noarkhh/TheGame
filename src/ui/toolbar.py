from __future__ import annotations
import pygame as pg
from src.ui.ui_element import UIElement
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.ui.button_manager import ButtonManager
    from src.graphics.spritesheet import Spritesheet


class Toolbar(UIElement):
    def __init__(self, spritesheet: Spritesheet, button_manager: ButtonManager, button_specs: dict[str, list]):
        self.image: pg.Surface = spritesheet.get_ui_image("Decorative", "toolbar")
        self.rect: pg.Rect = self.image.get_rect(right=self.ui.window_size.x, top=184)

        super().__init__(self.image, self.rect, spritesheet, button_manager, button_specs)
        self.load()

    def load(self) -> None:
        for name, (shape, position, scale) in self.button_specs.items():
            self.load_button(name, shape, position, scale, function_args=[name])



