from __future__ import annotations
import pygame as pg
from typing import TYPE_CHECKING
from src.ui.toolbar import Toolbar
from src.ui.ui_element import UIElement
import json

if TYPE_CHECKING:
    from src.ui.button_manager import ButtonManager
    from src.graphics.spritesheet import Spritesheet
    from src.core_classes import Vector


class UI:
    def __init__(self, button_manager: ButtonManager, spritesheet: Spritesheet, window_size: Vector[int]) -> None:
        UIElement.ui = self
        self.button_manager: ButtonManager = button_manager
        self.spritesheet: Spritesheet = spritesheet
        self.window_size: Vector[int] = window_size
        with open("../config/button_specs.json", "r") as f:
            self.button_specs: dict = json.load(f)
        self.toolbar: Toolbar = Toolbar(button_manager, spritesheet, self.button_specs["Toolbar"])

    def draw_elements(self, screen: pg.Surface) -> None:
        screen.blit(self.toolbar.image, self.toolbar.rect)
