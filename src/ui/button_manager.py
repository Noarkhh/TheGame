from __future__ import annotations
import pygame as pg
from typing import TYPE_CHECKING, Optional
from src.ui.button import Button
if TYPE_CHECKING:
    from src.cursor import Cursor


class ButtonManager:
    def __init__(self, cursor: Cursor):
        self.cursor: Cursor = cursor
        self.buttons: pg.sprite.Group = pg.sprite.Group()

        self.hovered_button: Optional[Button] = None
        self.held_button: Optional[Button] = None

    def button_pressed(self):
        self.hovered_button.is_held_down = True
        self.held_button = self.hovered_button
