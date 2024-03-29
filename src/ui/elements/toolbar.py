from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Optional

import pygame as pg

from src.entities.demolisher import Demolisher
from src.ui.button_dict import ButtonDict
from src.ui.elements.ui_element import UIElement

if TYPE_CHECKING:
    from src.ui.button_manager import ButtonManager
    from src.ui.button import Button
    from src.graphics.spritesheet import Spritesheet


class Toolbar(UIElement):
    def __init__(self, spritesheet: Spritesheet, button_manager: ButtonManager, button_specs: dict[str, list]) -> None:
        self.image: pg.Surface = spritesheet.get_ui_image("Decorative", "toolbar")
        self.rect: pg.Rect = self.image.get_rect(right=self.ui.window_size.x, top=184)

        super().__init__(self.image, self.rect, spritesheet, button_manager, button_specs)
        self.buttons_to_functions: dict[str, tuple[Optional[Callable], tuple]] = {
            "zoom_in": (None, ()),
            "zoom_out": (None, ()),
            "drag_mode": (None, ()),
            "debug": (None, ()),
            "build": (self.toggle_build_menu, ()),
            "demolish": (self.ui.cursor.assign_entity_class, (Demolisher,)),
            "pause": (self.pause, ())
        }

        self.named_buttons: ButtonDict = ButtonDict()

        self.load()

    def load(self) -> None:
        super().load()
        for name, (shape, position, scale) in self.button_specs.items():
            new_button = self.create_icon_button(name, shape, position, scale, self.buttons_to_functions[name][0],
                                                 function_args=self.buttons_to_functions[name][1], self_reference=True)

            self.named_buttons[name] = new_button

    def toggle_build_menu(self, button: Button) -> None:
        self.ui.build_menu.toggle()
        if self.ui.build_menu.is_loaded:
            button.lock(in_pressed_state=True)
        else:
            button.unlock()

    def pause(self, button: Button) -> None:
        self.ui.pause_menu.load()

    def assign_function(self, button_name: str, function: Callable, function_args: tuple = ()) -> None:
        button = self.named_buttons[button_name]
        button.function = function
        button.function_args = (*function_args, button) if button in button.function_args else function_args
