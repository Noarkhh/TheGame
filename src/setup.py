from __future__ import annotations
import pygame as pg
from typing import TYPE_CHECKING
from src.cursor import Cursor
from src.config import Config
from src.game_mechanics.struct_manager import StructManager
from src.game_mechanics.treasury import Treasury
from src.game_mechanics.map import MapManager
from src.main_loop.keyboard_handler import KeyboardHandler
from src.main_loop.mouse_handler import MouseHandler
from src.main_loop.event_handler import EventHandler
from src.main_loop.main_loop import MainLoop
from src.ui.ui import UI
from src.ui.button_manager import ButtonManager
from src.graphics.renderer import Renderer
from src.graphics.entities import Entities
from src.graphics.spritesheet import Spritesheet
from src.graphics.scene import Scene

if TYPE_CHECKING:
    pass


class Setup:
    def __init__(self) -> None:
        pg.init()
        pg.mixer.init()
        config: Config = Config()
        screen = pg.display.set_mode(config.window_size.to_tuple())

        cursor: Cursor = Cursor()
        spritesheet: Spritesheet = Spritesheet()
        button_manager: ButtonManager = ButtonManager(cursor)
        ui: UI = UI(button_manager, spritesheet, config.window_size)
        treasury: Treasury = Treasury(config)

        entities: Entities = Entities(spritesheet)
        map_manager: MapManager = MapManager(config)

        scene: Scene = Scene(config, spritesheet, map_manager)
        renderer: Renderer = Renderer(scene, screen, entities, cursor, ui)
        struct_manager: StructManager = StructManager(config, map_manager, treasury)
        keyboard_handler: KeyboardHandler = KeyboardHandler(cursor, ui, struct_manager)
        mouse_handler: MouseHandler = MouseHandler(cursor, ui, struct_manager, scene)
        event_handler: EventHandler = EventHandler(mouse_handler, keyboard_handler)
        print("initialization complete.")

        self.main_loop: MainLoop = MainLoop(event_handler, renderer, scene, ui, config.frame_rate)

