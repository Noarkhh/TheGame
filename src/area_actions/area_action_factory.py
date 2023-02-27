from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Type

from src.area_actions.line_area_action_build import LineAreaActionBuild
from src.area_actions.rectangle_area_action_build import RectangleAreaActionBuild
from src.area_actions.rectangle_area_action_demolish import RectangleAreaActionDemolish
from src.entities.demolisher import Demolisher
from src.entities.structure_snapper import StructureSnapper
from src.entities.tile_entity import DragShape

if TYPE_CHECKING:
    from src.area_actions.area_action import AreaAction, T
    from src.game_mechanics.struct_manager import StructManager
    from src.core.cursor import Cursor


def area_action_factory(struct_manager: StructManager, cursor: Cursor,
                        tile_entity: Type[T]) -> Optional[AreaAction]:
    if not tile_entity.is_draggable:
        return None
    if issubclass(tile_entity, Demolisher):
        return RectangleAreaActionDemolish(cursor, struct_manager, cursor.pos, tile_entity)
    if issubclass(tile_entity, StructureSnapper):
        if tile_entity.drag_shape == DragShape.LINE:
            return LineAreaActionBuild(cursor, struct_manager, cursor.pos, tile_entity)
        if tile_entity.drag_shape == DragShape.RECTANGLE:
            return RectangleAreaActionBuild(cursor, struct_manager, cursor.pos, tile_entity)
    return None
