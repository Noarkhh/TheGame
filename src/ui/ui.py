from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

from src.ui.elements.build_menu import BuildMenu
from src.ui.elements.minimap import Minimap
from src.ui.elements.pause_menu import PauseMenu
from src.ui.elements.toolbar import Toolbar
from src.ui.elements.top_bar import TopBar
from src.ui.elements.ui_element import UIElement

if TYPE_CHECKING:
    from src.ui.button_manager import ButtonManager
    from src.graphics.spritesheet import Spritesheet
    from src.graphics.scene import Scene
    from src.core.enums import Vector
    from src.core.config import Config
    from src.core.cursor import Cursor
    from src.game_mechanics.map_manager import MapManager


class UI:
    toolbar: Toolbar
    build_menu: BuildMenu
    minimap: Minimap
    top_bar: TopBar
    pause_menu: PauseMenu

    def __init__(self, config: Config, button_manager: ButtonManager, spritesheet: Spritesheet,
                 map_manager: MapManager, scene: Scene, cursor: Cursor, screen: pg.Surface) -> None:
        UIElement.ui = self
        self.button_manager: ButtonManager = button_manager
        self.spritesheet: Spritesheet = spritesheet
        self.cursor: Cursor = cursor
        self.screen: pg.Surface = screen

        self.cursor.ui = self

        self.window_size: Vector[int] = config.window_size
        self.button_specs: dict[str, dict[str, list]] = config.get_button_specs()

        self.elements: pg.sprite.Group[UIElement] = pg.sprite.Group()

        self.toolbar = Toolbar(spritesheet, button_manager, self.button_specs["Toolbar"])
        self.build_menu = BuildMenu(config, spritesheet, button_manager, self.button_specs["BuildMenu"])
        self.minimap = Minimap(map_manager, spritesheet, scene, button_manager, {})
        self.top_bar = TopBar(spritesheet, button_manager, {})
        self.pause_menu = PauseMenu(spritesheet, button_manager, self.button_specs["PauseMenu"])

    def draw_elements(self) -> None:
        for element in self.elements:
            if element.is_loaded:
                element.draw(self.screen)
