from __future__ import annotations
import pygame as pg
from typing import TYPE_CHECKING, ClassVar, Callable, Optional, Any
from random import randint
if TYPE_CHECKING:
    from src.ui.button_manager import ButtonManager


class Button(pg.sprite.Sprite):
    button_manager: ClassVar[ButtonManager]

    def __init__(self, rect: pg.Rect, base_image: pg.Surface, hover_image: pg.Surface,
                 function: Callable, ui_rect: pg.Rect, function_args: Optional[list[Any]] = None,
                 sound: str = "woodrollover", contents_image: Optional[pg.Surface] = None,
                 contents_height: int = 4) -> None:

        self.rect: pg.Rect = rect
        self.collision_rect: pg.Rect = self.rect.move(ui_rect.x, ui_rect.y)
        self.base_image: pg.Surface = base_image
        self.hover_image: pg.Surface = hover_image
        if contents_image is not None:
            contents_rect = contents_image.get_rect(centerx=self.base_image.get_width() / 2, top=contents_height)
            self.base_image.blit(contents_image, contents_rect)
            self.hover_image.blit(contents_image, contents_rect.move(0, 4))
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
