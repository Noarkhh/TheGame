from __future__ import annotations
import pygame as pg
from typing import TYPE_CHECKING, ClassVar, Any
from abc import ABC, abstractmethod

if TYPE_CHECKING:
    from src.ui.button_manager import ButtonManager
    from src.graphics.spritesheet import Spritesheet
    from src.ui.ui import UI
    from src.ui.button import Button


class UIElement(ABC, pg.sprite.Sprite):
    ui: ClassVar[UI]

    def __init__(self, image: pg.Surface, rect: pg.Rect, button_manager: ButtonManager,
                 spritesheet: Spritesheet, button_specs: dict[str, dict[str, Any]]) -> None:
        self.image: pg.Surface = image
        self.rect: pg.Rect = rect
        self.button_manager: ButtonManager = button_manager
        self.spritesheet: Spritesheet = spritesheet
        self.button_specs: dict[str, dict[str, Any]] = button_specs

        self.buttons: pg.sprite.Group[Button] = pg.sprite.Group()
        super().__init__()
        self.ui.ui_elements.add(self)

    @abstractmethod
    def load(self) -> None: ...

    def draw(self, image: pg.Surface) -> None:
        self.buttons.draw(self.image)
        image.blit(self.image, self.rect)

