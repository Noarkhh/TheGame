from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

from src.game_mechanics.time_manager import TimeManager
from src.ui.elements.ui_element import UIElement

if TYPE_CHECKING:
    from src.graphics.spritesheet import Spritesheet
    from src.ui.button_manager import ButtonManager


class TopBar(UIElement):
    def __init__(self, spritesheet: Spritesheet, button_manager: ButtonManager, time_manager: TimeManager, button_specs: dict[str, list]):
        self.image: pg.Surface = pg.Surface((self.ui.window_size.x, 44))
        self.rect: pg.Rect = self.image.get_rect()

        self.time_manager: TimeManager = time_manager
        self.font = pg.font.Font('../assets/Minecraft.otf', 20)

        bar_segment: pg.Surface = spritesheet.get_ui_image("Decorative", "top_bar_segment")
        next_bar_segment_x = 0
        while next_bar_segment_x < self.ui.window_size.x:
            self.image.blit(bar_segment, (next_bar_segment_x, 0))
            next_bar_segment_x += bar_segment.get_width()

        super().__init__(self.image, self.rect, spritesheet, button_manager, button_specs)

        self.image_raw = self.image.copy()

    def load(self) -> None:
        self.image.blit(self.image_raw, (0, 0))
        date_text = self.font.render(self.time_manager.game_time_clock.get_date_string(), False, (62, 61, 58), "black")
        date_text.set_colorkey("black")

        tick_stats_text = self.font.render(self.time_manager.get_tick_statistics_string(), False, (62, 61, 58), "black")
        tick_stats_text.set_colorkey("black")

        self.image.blit(date_text, date_text.get_rect(topright=(self.ui.window_size.x - 5, 12)))
        self.image.blit(tick_stats_text, date_text.get_rect(topleft=(5, 12)))

    def draw(self, image: pg.Surface) -> None:
        if self.time_manager.game_time_clock.display_state_changed:
            self.load()
            self.time_manager.game_time_clock.display_state_changed = False
        super().draw(image)
