from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from src.game_mechanics.snapper import Snapper
from src.game_mechanics.structures import Structure
from src.effects.area_ghost_factory import area_ghost_factory

if TYPE_CHECKING:
    from src.core.cursor import Cursor
    from src.ui.ui import UI
    from src.game_mechanics.struct_manager import StructManager
    from src.graphics.scene import Scene
    from src.effects.area_ghost import AreaGhost


class MouseHandler:
    def __init__(self, cursor: Cursor, ui: UI, struct_manager: StructManager, scene: Scene) -> None:
        self.cursor: Cursor = cursor
        self.ui: UI = ui
        self.struct_manager: StructManager = struct_manager
        self.scene = scene
        self.area_ghost: Optional[AreaGhost] = None
        self.is_lmb_pressed: bool = False
        self.is_rmb_pressed: bool = False
        self.was_lmb_pressed_last_tick: bool = False
        self.was_rmb_pressed_last_tick: bool = False

    def lmb_press(self) -> None:
        self.ui.button_manager.lmb_press()
        self.is_lmb_pressed = True
        self.was_lmb_pressed_last_tick = False
        if isinstance(self.cursor.held_entity, Snapper) and self.cursor.held_entity.is_draggable:
            self.area_ghost = area_ghost_factory(self.struct_manager, self.cursor, self.cursor.held_entity.__class__)

    def lmb_release(self) -> None:
        self.scene.set_decrement()
        self.ui.button_manager.lmb_release()
        self.is_lmb_pressed = False
        if self.area_ghost is not None:
            self.area_ghost.resolve()
            self.area_ghost = None

    def lmb_pressed(self) -> None:

        if self.ui.button_manager.held_button is not None:
            self.was_lmb_pressed_last_tick = True
            return

        if self.area_ghost is not None:
            self.area_ghost.find_new_segments()
        elif self.cursor.held_entity is not None and isinstance(self.cursor.held_entity, Structure):
            self.struct_manager.build(self.cursor.held_entity, failure_sound=not self.was_lmb_pressed_last_tick)
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
