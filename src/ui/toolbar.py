from __future__ import annotations
import pygame as pg
from src.ui.ui_element import UIElement
from typing import TYPE_CHECKING
from src.ui.button import Button

if TYPE_CHECKING:
    from src.ui.button_manager import ButtonManager
    from src.graphics.spritesheet import Spritesheet


class Toolbar(UIElement):
    def __init__(self, button_manager: ButtonManager, spritesheet: Spritesheet,
                 button_specs: dict):
        self.image: pg.Surface = spritesheet.get_ui_image("Decorative", "toolbar")
        self.rect: pg.Rect = self.image.get_rect(right=self.ui.window_size.x, top=184)
        self.button_specs: dict = button_specs
        self.buttons: pg.sprite.Group[Button] = pg.sprite.Group()

        super().__init__(button_manager, spritesheet)
        self.load()

    def load(self) -> None:
        for button_name, button_info in self.button_specs.items():
            button_type = button_info["type"]
            button_pos = button_info["position"]
            button_image = self.spritesheet.get_ui_image("Buttons", button_type)
            button_hover_image = self.spritesheet.get_ui_image("Buttons", button_type + "_hover")
            button_rect = button_image.get_rect(topleft=button_pos)
            self.buttons.add(Button(button_rect, button_image, button_hover_image, lambda: None, self.rect))

        for button in self.buttons:
            print(button.collision_rect)
        self.buttons.draw(self.image)



