from __future__ import annotations
from src.game_mechanics.structures import *
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.cursor import Cursor
    from src.ui.ui import UI


class KeyboardHandler:
    def __init__(self, cursor: Cursor, ui: UI):
        self.cursor: Cursor = cursor
        self.ui: UI = ui
        self.key_class_dict = {pg.K_h: House, pg.K_t: Tower, pg.K_u: Road, pg.K_w: Wall, pg.K_g: Gate,
                               pg.K_m: Mine, pg.K_f: Farmland, pg.K_b: Bridge}

    def handle_key_press(self, key: int):
        if key in self.key_class_dict:
            self.cursor.assign_struct_class(self.key_class_dict[key])
        elif key == pg.K_n:
            self.cursor.unassign()
        elif key == pg.K_r:
            if hasattr(self.cursor.held_structure, "rotate"):
                self.cursor.held_structure.rotate()

