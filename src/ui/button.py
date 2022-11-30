from __future__ import annotations
import pygame as pg
from typing import TYPE_CHECKING, ClassVar, Callable, Optional, Any
from random import randint
if TYPE_CHECKING:
    from src.ui.button_manager import ButtonManager


class Button(pg.sprite.Sprite):
    manager: ClassVar[ButtonManager]

    def __init__(self, rect: pg.Rect, base_image: pg.Surface, hover_image: pg.Surface, contents_image: pg.Surface,
                 function: Callable, ui_rect: pg.Rect, function_args: Optional[list[Any]] = None,
                 hover_sound: str = "woodrollover", press_sound: str = "woodpush2", contents_height: int = 4) -> None:

        self.rect: pg.Rect = rect
        self.collision_rect: pg.Rect = self.rect.move(ui_rect.x, ui_rect.y)
        self.base_image: pg.Surface = base_image
        self.hover_image: pg.Surface = hover_image
        contents_rect = contents_image.get_rect(centerx=self.base_image.get_width() / 2, top=contents_height)
        self.base_image.blit(contents_image, contents_rect)
        self.hover_image.blit(contents_image, contents_rect.move(0, 4))

        self.image: pg.Surface = self.base_image

        self.function: Callable = function
        if function_args is None:
            self.function_args: list = []
        else:
            self.function_args = function_args
        self.hover_sound: str = hover_sound
        self.press_sound: str = press_sound

        self.is_locked: bool = False
        self.is_held_down: bool = False

        super().__init__()
        self.manager.buttons.add(self)

    def hover(self) -> None:
        if not self.is_locked:
            self.image = self.hover_image

    def unhover(self) -> None:
        if not self.is_locked:
            self.image = self.base_image

    def play_hover_sound(self) -> None:
        self.manager.sound_manager.play_sound(self.hover_sound)

    def press(self) -> Any:
        if not self.is_locked:
            return self.function(*self.function_args)
        return None

    def play_press_sound(self) -> None:
        self.manager.sound_manager.play_sound(self.press_sound)

    def draw(self, image: pg.Surface) -> None:
        image.blit(self.image, self.rect)

    def lock(self) -> None:
        self.is_locked = True

    def unlock(self) -> None:
        self.is_locked = False
