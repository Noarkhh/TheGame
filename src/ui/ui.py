from __future__ import annotations
import pygame as pg
from typing import TYPE_CHECKING, Any
from src.ui.toolbar import Toolbar
from src.ui.minimap import Minimap
from src.ui.top_bar import TopBar
from src.ui.build_menu import BuildMenu
from src.ui.pause_menu import PauseMenu
from src.ui.ui_element import UIElement

if TYPE_CHECKING:
    from src.ui.button_manager import ButtonManager
    from src.graphics.spritesheet import Spritesheet
    from src.graphics.scene import Scene
    from src.core_classes import Vector
    from src.config import Config
    from src.cursor import Cursor
    from src.game_mechanics.map_manager import MapManager


class UI:
    def __init__(self, config: Config, button_manager: ButtonManager, spritesheet: Spritesheet,
                 map_manager: MapManager, scene: Scene, cursor: Cursor, screen: pg.Surface) -> None:
        UIElement.ui = self
        self.button_manager: ButtonManager = button_manager
        self.spritesheet: Spritesheet = spritesheet
        self.cursor: Cursor = cursor
        self.screen: pg.Surface = screen

        self.window_size: Vector[int] = config.window_size
        self.button_specs: dict[str, dict[str, list]] = config.get_button_specs()

        self.elements: pg.sprite.Group[UIElement] = pg.sprite.Group()

        self.build_menu: BuildMenu = BuildMenu(config, spritesheet, button_manager, self.button_specs["BuildMenu"])
        self.minimap: Minimap = Minimap(map_manager, spritesheet, scene, button_manager, {})
        self.top_bar: TopBar = TopBar(spritesheet, button_manager, {})
        self.toolbar: Toolbar = Toolbar(spritesheet, button_manager, self.button_specs["Toolbar"])
        self.pause_menu: PauseMenu = PauseMenu(spritesheet, button_manager, self.button_specs["PauseMenu"])

    def draw_elements(self) -> None:
        for element in self.elements:
            if element.is_loaded:
                element.draw(self.screen)
