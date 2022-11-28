from __future__ import annotations
import pygame as pg
from src.ui.ui_element import UIElement
from typing import TYPE_CHECKING
from src.ui.button import Button

if TYPE_CHECKING:
    from src.ui.button_manager import ButtonManager
    from src.graphics.spritesheet import Spritesheet


def print_button_name(button_name: str) -> None:
    print(button_name)


class Toolbar(UIElement):
    def __init__(self, button_manager: ButtonManager, spritesheet: Spritesheet,
                 button_specs: dict):
        self.image: pg.Surface = spritesheet.get_ui_image("Decorative", "toolbar")
        self.rect: pg.Rect = self.image.get_rect(right=self.ui.window_size.x, top=184)

        super().__init__(self.image, self.rect, button_manager, spritesheet, button_specs)
        self.load()

    def load(self) -> None:
        for name, specs in self.button_specs.items():
            shape = specs["shape"]
            image = self.spritesheet.get_ui_image("Buttons", shape)
            if shape == "small_round":
                contents_image = self.spritesheet.get_ui_image("Icons", name, scale=2)
            else:
                contents_image = self.spritesheet.get_ui_image("Icons", name)
            hover_image = self.spritesheet.get_ui_image("Buttons", shape + "_hover")
            rect = image.get_rect(topleft=specs["position"])
            self.buttons.add(Button(rect, image, hover_image, print_button_name, self.rect,
                                    function_args=[name], contents_image=contents_image))



