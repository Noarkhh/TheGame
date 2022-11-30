from __future__ import annotations
import pygame as pg
from typing import TYPE_CHECKING, ClassVar, Any
from abc import ABC, abstractmethod
from src.ui.button import Button

if TYPE_CHECKING:
    from src.ui.button_manager import ButtonManager
    from src.graphics.spritesheet import Spritesheet
    from src.ui.ui import UI


class UIElement(ABC, pg.sprite.Sprite):
    ui: ClassVar[UI]

    def __init__(self, image: pg.Surface, rect: pg.Rect, spritesheet: Spritesheet,
                 button_manager: ButtonManager, button_specs: dict[str, list]) -> None:
        self.image: pg.Surface = image
        self.rect: pg.Rect = rect
        self.button_manager: ButtonManager = button_manager
        self.spritesheet: Spritesheet = spritesheet
        self.button_specs: dict[str, list] = button_specs

        self.buttons: pg.sprite.Group[Button] = pg.sprite.Group()
        super().__init__()
        self.ui.elements.add(self)

    @abstractmethod
    def load(self) -> None: ...

    def draw(self, image: pg.Surface) -> None:
        self.buttons.draw(self.image)
        image.blit(self.image, self.rect)

    def load_button(self, name: str, shape: str, position: list[int], scale: int):
        image = self.spritesheet.get_ui_image("Buttons", shape)
        contents_image = self.spritesheet.get_ui_image("Icons", name, scale=scale)
        hover_image = self.spritesheet.get_ui_image("Buttons", shape + "_hover")
        rect = image.get_rect(topleft=position)
        self.buttons.add(Button(rect, image, hover_image, print_button_name, self.rect,
                                function_args=[name], contents_image=contents_image))


def print_button_name(button_name: str) -> None:
    print(button_name)
