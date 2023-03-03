from __future__ import annotations

from typing import Type

from src.entities.demolisher import Demolisher
from src.entities.structures import *

if TYPE_CHECKING:
    from src.core.cursor import Cursor
    from src.graphics.scene import Scene
    from src.ui.ui import UI
    from src.game_mechanics.struct_manager import StructManager
    from src.sound.soundtrack import Soundtrack
    from src.graphics.zoomer import Zoomer


class KeyboardHandler:
    def __init__(self, cursor: Cursor, ui: UI, struct_manager: StructManager, soundtrack: Soundtrack,
                 zoomer: Zoomer, scene: Scene) -> None:
        self.cursor: Cursor = cursor
        self.ui: UI = ui
        self.struct_manager: StructManager = struct_manager
        self.soundtrack: Soundtrack = soundtrack
        self.zoomer: Zoomer = zoomer
        self.scene: Scene = scene
        self.key_class_dict: dict[int, Type[Structure]] = {pg.K_h: House, pg.K_t: Tower, pg.K_u: Road, pg.K_w: Wall,
                                                           pg.K_g: Gate, pg.K_m: Mine, pg.K_f: Farmland, pg.K_b: Bridge}
        self.pressed_keys_time: dict[int, int] = {}

    def key_pressed(self, key: int) -> None:
        self.pressed_keys_time[key] = 0

        if key in self.key_class_dict:
            self.cursor.assign_entity_class(self.key_class_dict[key])
        elif key == pg.K_n:
            self.cursor.unassign()
        elif key == pg.K_r:
            if isinstance(self.cursor.held_entity, Gate):
                self.cursor.held_entity.rotate()
        elif key == pg.K_COMMA:
            self.soundtrack.change_volume(-0.01)
        elif key == pg.K_PERIOD:
            self.soundtrack.change_volume(0.01)
        elif key == pg.K_ESCAPE:
            self.ui.pause_menu.load()
        elif key == pg.K_d:
            self.cursor.assign_entity_class(Demolisher)
        elif key == pg.K_v:
            self.ui.build_menu.toggle()
        elif key == pg.K_MINUS:
            self.zoomer.change_zoom(0.5)
        elif key == pg.K_EQUALS:
            self.zoomer.change_zoom(2)

    def key_released(self, key: int) -> None:
        if key in self.pressed_keys_time:
            self.pressed_keys_time.pop(key)

    def handle_pressed(self) -> None:
        for key, time in self.pressed_keys_time.items():
            if key == pg.K_COMMA and time >= 30:
                self.soundtrack.change_volume(-0.005)
            elif key == pg.K_PERIOD and time >= 30:
                self.soundtrack.change_volume(0.005)
            elif key == pg.K_UP:
                self.scene.move_direction(Direction.N)
            elif key == pg.K_RIGHT:
                self.scene.move_direction(Direction.E)
            elif key == pg.K_DOWN:
                self.scene.move_direction(Direction.S)
            elif key == pg.K_LEFT:
                self.scene.move_direction(Direction.W)

            self.pressed_keys_time[key] += 1
