from __future__ import annotations
from typing import TYPE_CHECKING
from src.core.cursor import Mode

if TYPE_CHECKING:
    from src.core.cursor import Cursor
    from src.ui.ui import UI
    from src.game_mechanics.struct_manager import StructManager
    from src.game_mechanics.structures import Structure
    from src.graphics.scene import Scene


class MouseHandler:
    def __init__(self, cursor: Cursor, ui: UI, struct_manager: StructManager, scene: Scene) -> None:
        self.cursor: Cursor = cursor
        self.ui: UI = ui
        self.struct_manager: StructManager = struct_manager
        self.scene = scene
        self.is_lmb_pressed: bool = False
        self.is_rmb_pressed: bool = False
        self.was_lmb_pressed_last_tick: bool = False
        self.was_rmb_pressed_last_tick: bool = False

    def lmb_press(self) -> None:
        self.ui.button_manager.lmb_press()
        self.is_lmb_pressed = True
        self.was_lmb_pressed_last_tick = False

    def lmb_release(self) -> None:
        self.scene.set_decrement()
        self.ui.button_manager.lmb_release()
        self.is_lmb_pressed = False

    def lmb_pressed(self) -> None:

        if self.ui.button_manager.held_button is None and self.cursor.mode == Mode.NORMAL:
            if isinstance(self.cursor.held_entity, Structure):
                self.struct_manager.place(self.cursor.held_entity, self.cursor.previous_pos,
                                          play_failure_sounds=not self.was_lmb_pressed_last_tick)
            else:
                self.scene.update_velocity(-self.cursor.pos_px_difference.to_float(), slow_down=False)

        self.was_lmb_pressed_last_tick = True

    def rmb_press(self) -> None:
        self.is_rmb_pressed = True
        self.was_rmb_pressed_last_tick = False

    def rmb_release(self) -> None:
        self.is_rmb_pressed = False

    def rmb_pressed(self) -> None:
        self.was_rmb_pressed_last_tick = True

    def mmb_press(self) -> None:
        selected_struct = self.struct_manager.map_manager.struct_map[self.cursor.pos]
        if selected_struct is not None:
            self.cursor.held_entity = selected_struct.copy()

    def handle_pressed(self) -> None:
        if self.is_lmb_pressed:
            self.lmb_pressed()
        if self.is_rmb_pressed:
            self.rmb_pressed()
