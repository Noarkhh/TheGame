from __future__ import annotations
import pygame as pg
from src.ui.ui_element import UIElement
from typing import TYPE_CHECKING, Type
from enum import Enum, auto

if TYPE_CHECKING:
    from src.graphics.spritesheet import Spritesheet
    from src.ui.button_manager import ButtonManager
    from src.config import Config
    from src.game_mechanics.structures import Structure


class Category(Enum):
    HOUSING = auto()
    MILITARY = auto()
    TRANSPORT = auto()
    MANUFACTURING = auto()
    AGRICULTURE = auto()
    RELIGION = auto()


class BuildMenu(UIElement):
    def __init__(self, config: Config, spritesheet: Spritesheet, button_manager: ButtonManager,
                 button_specs: dict[str, list]):
        self.image: pg.Surface = spritesheet.get_ui_image("Decorative", "build_menu")
        self.rect: pg.Rect = self.image.get_rect(centerx=self.ui.window_size.x // 2, top=44)
        self.categories: dict[Category, list[Type[Structure]]] = config.get_structure_categories()

        super().__init__(self.image, self.rect, spritesheet, button_manager, button_specs)
        self.load()

    def load(self) -> None:
        for name, (shape, position, scale) in self.button_specs.items():
            self.load_button(name, shape, position, scale, function_args=[name], hover_sound="metrollover")
