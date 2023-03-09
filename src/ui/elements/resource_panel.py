from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

from src.ui.elements.ui_element import UIElement

if TYPE_CHECKING:
    from src.game_mechanics.treasury import Treasury
    from src.graphics.spritesheet import Spritesheet
    from src.ui.button_manager import ButtonManager


class ResourcePanel(UIElement):
    treasury: Treasury

    def __init__(self, spritesheet: Spritesheet, button_manager: ButtonManager,
                 treasury: Treasury, button_specs: dict[str, list]):
        self.image: pg.Surface = spritesheet.get_ui_image("Decorative", "resource_panel")
        self.rect: pg.Rect = self.image.get_rect(topleft=(0, 44))

        super().__init__(self.image, self.rect, spritesheet, button_manager, button_specs)

        self.treasury = treasury
        self.font = pg.font.Font('assets/Minecraft.otf', 20)
        for i, resource in enumerate(self.treasury.resources):
            text_string = resource.name.title() + ": "
            text = self.font.render(text_string, False, (62, 61, 58), "black")
            text.set_colorkey("black")
            self.image.blit(text, text.get_rect(topright=(85, 10 + 22 * i)))

        self.image_raw: pg.Surface = self.image.copy()
        self.load()

    def load(self) -> None:
        self.image.blit(self.image_raw, (0, 0))
        for i, amount in enumerate(self.treasury.resources.values()):
            text = self.font.render(str(amount), False, (62, 61, 58), "black")
            text.set_colorkey("black")
            self.image.blit(text, text.get_rect(topleft=(85, 10 + 22 * i)))

    def draw(self, image: pg.Surface) -> None:
        if self.treasury.display_state_changed:
            self.load()
            self.treasury.display_state_changed = False
        super().draw(image)
