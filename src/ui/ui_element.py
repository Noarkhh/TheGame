from __future__ import annotations
import pygame as pg
from typing import TYPE_CHECKING, ClassVar, Optional, Callable, Any
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
        self.is_loaded: bool = True
        super().__init__()
        self.ui.elements.add(self)

    def load(self) -> None:
        self.is_loaded = True

    def unload(self) -> None:
        self.is_loaded = False
        for button in self.buttons:
            button.kill()

    def toggle(self) -> None:
        if self.is_loaded:
            self.unload()
        else:
            self.load()

    def draw(self, image: pg.Surface) -> None:
        image.blit(self.image, self.rect)
        self.buttons.draw(image)

    def create_icon_button(self, icon_name: str, shape: str, position: list[int], scale: int,
                           function: Optional[Callable] = None, **kwargs: Any) -> Button:
        contents_image = self.spritesheet.get_ui_image("Icons", icon_name, scale=scale)
        return self.create_image_button(contents_image, shape, position, function, **kwargs)

    def create_text_button(self, text: str, shape: str, position: list[int], scale: int,
                           function: Optional[Callable] = None, **kwargs: Any) -> Button:
        contents_image = pg.font.Font('../assets/Minecraft.otf', scale).render(text, False, (62, 61, 58), "black")
        contents_image.set_colorkey("black")
        return self.create_image_button(contents_image, shape, position, function, contents_height=8, **kwargs)

    def create_image_button(self, contents_image: pg.Surface, shape: str, position: list[int],
                            function: Optional[Callable] = None, **kwargs: Any) -> Button:
        image = self.spritesheet.get_ui_image("Buttons", shape)
        rect = image.get_rect(topleft=position)
        hover_image = self.spritesheet.get_ui_image("Buttons", shape + "_hover")
        if function is None:
            function = foo
        new_button: Button = Button(rect, image, hover_image, contents_image, function, self.rect, **kwargs)
        self.buttons.add(new_button)
        return new_button


def foo(button: Optional[Button] = None) -> None:
    print(button)
