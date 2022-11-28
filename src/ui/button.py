from __future__ import annotations
import pygame as pg
from typing import TYPE_CHECKING, ClassVar, Callable, Optional, Any
from random import randint
if TYPE_CHECKING:
    from src.ui.button_manager import ButtonManager


class Button(pg.sprite.Sprite):
    button_manager: ClassVar[ButtonManager]

    def __init__(self, rect: pg.Rect, base_image: pg.Surface, hover_image: pg.Surface,
                 function: Callable, function_args: Optional[list[Any]] = None, sound: str = "woodrollover") -> None:

        self.rect: pg.Rect = rect
        self.base_image: pg.Surface = base_image
        self.base_image.set_colorkey("white")
        self.hover_image: pg.Surface = hover_image
        self.hover_image.set_colorkey("white")
        self.image: pg.Surface = self.base_image

        self.function: Callable = function
        if function_args is None:
            self.function_args: list = []
        else:
            self.function_args = function_args
        self.sound: str = sound

        self.is_locked: bool = False
        self.is_held_down: bool = False

        super().__init__()
        self.button_manager.buttons.add(self)

    def hover(self) -> None:
        if not self.is_locked:
            self.image = self.hover_image

    def unhover(self) -> None:
        if not self.is_locked:
            self.image = self.base_image

    def play_hover_sound(self) -> None:
        if self.sound == "woodrollover":
            pass
        if self.sound == "metrollover":
            pass

    def press(self, *args, **kwargs) -> Any:
        if not self.is_locked:
            return self.function(*self.function_args, *args, **kwargs)
        return None

    def draw(self, image: pg.Surface):
        image.blit(self.image, self.rect)
