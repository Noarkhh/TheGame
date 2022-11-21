from __future__ import annotations
from typing import TYPE_CHECKING
from src.cursor import Mode

if TYPE_CHECKING:
    from src.cursor import Cursor
    from src.ui.ui import UI
    from src.game_mechanics.struct_manager import StructManager


class MouseHandler:
    def __init__(self, cursor: Cursor, ui: UI, struct_manager: StructManager) -> None:
        self.cursor: Cursor = cursor
        self.ui: UI = ui
        self.struct_manager: StructManager = struct_manager
        self.is_lmb_pressed: bool = False
        self.is_rmb_pressed: bool = False
        self.was_lmb_pressed_last_tick: bool = False
        self.was_rmb_pressed_last_tick: bool = False

    def lmb_press(self) -> None:
        self.is_lmb_pressed = True
        self.was_lmb_pressed_last_tick = False

    def lmb_release(self) -> None:
        self.is_lmb_pressed = False

    def lmb_pressed(self) -> None:
        if self.ui.button_manager.hovered_button is not None:
            self.ui.button_manager.button_pressed()
        if self.cursor.mode == Mode.NORMAL:
            if self.cursor.held_structure is not None:
                self.struct_manager.place(self.cursor.held_structure, self.cursor.previous_pos,
                                          play_failure_sounds=not self.was_lmb_pressed_last_tick)

        self.was_lmb_pressed_last_tick = True

    def rmb_press(self) -> None:
        self.is_rmb_pressed = True
        self.was_rmb_pressed_last_tick = False

    def rmb_release(self) -> None:
        self.is_rmb_pressed = False

    def rmb_pressed(self) -> None:
        # ...
        self.was_rmb_pressed_last_tick = True

    def mmb_press(self) -> None:
        selected_struct = self.struct_manager.map_manager.struct_map[self.cursor.pos]
        if selected_struct is not None:
            self.cursor.held_structure = selected_struct.copy()

    def handle_pressed(self) -> None:
        if self.is_lmb_pressed:
            self.lmb_pressed()
        if self.is_rmb_pressed:
            self.rmb_pressed()
