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

if TYPE_CHECKING:
    pass


class Setup:
    def __init__(self) -> None:
        pg.init()
        pg.mixer.init()
        config: Config = Config()
        cursor: Cursor = Cursor()
        treasury: Treasury = Treasury(config)
        map_manager: MapManager = MapManager(config)
        struct_manager: StructManager = StructManager(config, map_manager, treasury)
        keyboard_handler: KeyboardHandler()
        mouse_handler: MouseHandler()
        self.event_handler: EventHandler = EventHandler()
        self.main_loop: MainLoop = MainLoop()

