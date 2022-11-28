from __future__ import annotations
import pygame as pg
from typing import TYPE_CHECKING, ClassVar
from abc import ABC, abstractmethod

if TYPE_CHECKING:
    from src.ui.button_manager import ButtonManager
    from src.graphics.spritesheet import Spritesheet
    from src.ui.ui import UI


class UIElement(ABC, pg.sprite.Group):
    ui: ClassVar[UI]
    buttons: pg.sprite.Group
    image: pg.Surface
    rect: pg.Rect

    def __init__(self, button_manager: ButtonManager, spritesheet: Spritesheet) -> None:
        super().__init__()
        self.button_manager: ButtonManager = button_manager
        self.spritesheet: Spritesheet = spritesheet

    @abstractmethod
    def load(self) -> None: ...

    def draw(self, image: pg.Surface):
        for button in self.buttons:
            button.draw(self.image)
        image.blit(self.image, self.rect)

