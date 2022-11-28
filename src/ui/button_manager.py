from __future__ import annotations
import pygame as pg
from typing import TYPE_CHECKING, Optional
from src.ui.button import Button
if TYPE_CHECKING:
    from src.cursor import Cursor


class ButtonManager:
    def __init__(self, cursor: Cursor) -> None:
        Button.button_manager = self

        self.cursor: Cursor = cursor
        self.buttons: pg.sprite.Group[Button] = pg.sprite.Group()

        self.hovered_button: Optional[Button] = None
        self.previous_hovered_button: Optional[Button] = None

        self.held_button: Optional[Button] = None

    def button_pressed(self) -> None:
        if isinstance(self.hovered_button, Button):
            self.hovered_button.is_held_down = True
            self.held_button = self.hovered_button

    def check_for_hovers(self) -> None:
        self.hovered_button = None
        for button in self.buttons:
            if button.rect.collidepoint(pg.mouse.get_pos()):
                self.hovered_button = button
                button.hover()
            else:
                button.unhover()

        if self.hovered_button is not None and self.hovered_button is not self.previous_hovered_button:
            self.hovered_button.play_hover_sound()

        self.previous_hovered_button = self.hovered_button


