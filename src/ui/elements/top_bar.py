from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

from src.ui.elements.ui_element import UIElement

if TYPE_CHECKING:
    from src.graphics.spritesheet import Spritesheet
    from src.ui.button_manager import ButtonManager


class TopBar(UIElement):
    def __init__(self, spritesheet: Spritesheet, button_manager: ButtonManager, button_specs: dict[str, list]):
        self.image: pg.Surface = pg.Surface((self.ui.window_size.x, 44))
        self.rect: pg.Rect = self.image.get_rect()

        bar_segment: pg.Surface = spritesheet.get_ui_image("Decorative", "top_bar_segment")
        next_bar_segment_x = 0
        while next_bar_segment_x < self.ui.window_size.x:
            self.image.blit(bar_segment, (next_bar_segment_x, 0))
            next_bar_segment_x += bar_segment.get_width()

        super().__init__(self.image, self.rect, spritesheet, button_manager, button_specs)

    def load(self) -> None:
        pass
