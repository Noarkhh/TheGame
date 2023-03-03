from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

from src.core.config import Config
from src.core.cursor import Cursor
from src.core.vector import Vector
from src.entities.entities import Entities
from src.entities.save_manager import SaveManager
from src.game_mechanics.map_manager import MapManager
from src.game_mechanics.struct_manager import StructManager
from src.game_mechanics.treasury import Treasury
from src.graphics.renderer import Renderer
from src.graphics.scene import Scene
from src.graphics.spritesheet import Spritesheet
from src.main_loop.event_handler import EventHandler
from src.main_loop.keyboard_handler import KeyboardHandler
from src.main_loop.main_loop import MainLoop
from src.main_loop.mouse_handler import MouseHandler
from src.sound.sound_manager import SoundManager
from src.sound.soundtrack import Soundtrack
from src.ui.button_manager import ButtonManager
from src.ui.ui import UI
from src.graphics.zoomer import Zoomer

if TYPE_CHECKING:
    pass


class Setup:
    def __init__(self) -> None:
        pg.init()
        pg.mixer.init()
        config: Config = Config()
        if config.fullscreen:
            screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
            config.window_size = Vector(pg.display.get_window_size())
        else:
            screen = pg.display.set_mode(config.window_size.to_tuple())

        spritesheet: Spritesheet = Spritesheet(config)
        entities: Entities = Entities(spritesheet)

        sound_manager: SoundManager = SoundManager(config)
        soundtrack: Soundtrack = Soundtrack()

        cursor: Cursor = Cursor()
        treasury: Treasury = Treasury(config)

        map_manager: MapManager = MapManager(config)

        scene: Scene = Scene(config, spritesheet, map_manager)
        button_manager: ButtonManager = ButtonManager(cursor, sound_manager, scene)
        struct_manager: StructManager = StructManager(config, map_manager, treasury, sound_manager)
        save_manager: SaveManager = SaveManager(config, map_manager, struct_manager, treasury, scene, spritesheet,
                                                entities, cursor)
        ui: UI = UI(config, button_manager, spritesheet, map_manager, scene, cursor, save_manager, screen)

        zoomer: Zoomer = Zoomer(entities, scene, map_manager, cursor, ui)
        renderer: Renderer = Renderer(scene, screen, entities, cursor, ui)
        keyboard_handler: KeyboardHandler = KeyboardHandler(cursor, ui, struct_manager, soundtrack, zoomer)
        mouse_handler: MouseHandler = MouseHandler(cursor, ui, struct_manager, scene)
        event_handler: EventHandler = EventHandler(mouse_handler, keyboard_handler, soundtrack)
        print("initialization complete.")

        self.main_loop: MainLoop = MainLoop(event_handler, renderer, scene, ui, soundtrack, config.frame_rate)

