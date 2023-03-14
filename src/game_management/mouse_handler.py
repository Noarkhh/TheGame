from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from src.entities.snapper import Snapper
from src.entities.structures import Structure
from src.game_management.area_actions.area_action_factory import area_action_factory

if TYPE_CHECKING:
    from src.core.cursor import Cursor
    from src.ui.ui import UI
    from src.game_mechanics.struct_manager import StructManager
    from src.graphics.scene import Scene
    from src.game_management.area_actions.area_action import AreaAction


class MouseHandler:
    def __init__(self, cursor: Cursor, ui: UI, struct_manager: StructManager, scene: Scene) -> None:
        self.cursor: Cursor = cursor
        self.ui: UI = ui
        self.struct_manager: StructManager = struct_manager
        self.scene = scene
        self.area_action: Optional[AreaAction] = None
        self.is_lmb_pressed: bool = False
        self.is_rmb_pressed: bool = False
        self.was_lmb_pressed_last_tick: bool = False
        self.was_rmb_pressed_last_tick: bool = False

    def lmb_press(self) -> None:
        self.ui.button_manager.lmb_press()
        self.is_lmb_pressed = True
        self.was_lmb_pressed_last_tick = False
        if isinstance(self.cursor.held_entity, Snapper) and self.cursor.held_entity.is_draggable and \
                self.ui.button_manager.held_button is None:
            self.area_action = area_action_factory(self.struct_manager, self.cursor, self.cursor.held_entity.__class__)

    def lmb_release(self) -> None:
        self.scene.set_decrement()
        self.ui.button_manager.lmb_release()
        self.is_lmb_pressed = False
        if self.area_action is not None:
            self.area_action.resolve()
            self.area_action = None

    def lmb_pressed(self) -> None:

        if self.ui.button_manager.held_button is not None:
            self.was_lmb_pressed_last_tick = True
            return

        if self.area_action is not None:
            self.area_action.find_current_segments()
        elif isinstance(self.cursor.held_entity, Structure):
            self.struct_manager.build(self.cursor.held_entity, failure_sound=not self.was_lmb_pressed_last_tick)
        else:
            self.scene.update_velocity(-self.cursor.pos_px_difference.to_float(), slow_down=False)

        self.was_lmb_pressed_last_tick = True

    def rmb_press(self) -> None:
        self.is_rmb_pressed = True
        self.was_rmb_pressed_last_tick = False
        if self.area_action is not None:
            self.area_action.kill_segments()
            self.area_action = None
            self.lmb_release()

    def rmb_release(self) -> None:
        self.scene.set_decrement()
        self.is_rmb_pressed = False

    def rmb_pressed(self) -> None:
        self.scene.update_velocity(-self.cursor.pos_px_difference.to_float(), slow_down=False)
        self.was_rmb_pressed_last_tick = True

    def mmb_press(self) -> None:
        selected_struct = self.struct_manager.map_container.struct_map[self.cursor.pos]
        if selected_struct is not None:
            self.cursor.unassign()
            self.cursor.assign_entity_class(selected_struct.__class__)

    def handle_pressed(self) -> None:
        if self.is_lmb_pressed:
            self.lmb_pressed()
        if self.is_rmb_pressed:
            self.rmb_pressed()
