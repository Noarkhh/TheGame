from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Type

from src.effects.line_ghost_build import LineGhostBuild
from src.effects.rectangle_ghost_build import RectangleGhostBuild
from src.effects.rectangle_ghost_demolish import RectangleGhostDemolish
from src.game_mechanics.demolisher import Demolisher
from src.game_mechanics.structure_snapper import StructureSnapper
from src.graphics.tile_entity import DragShape

if TYPE_CHECKING:
    from src.effects.area_ghost import AreaGhost, T
    from src.game_mechanics.struct_manager import StructManager
    from src.core.cursor import Cursor


def area_ghost_factory(struct_manager: StructManager, cursor: Cursor,
                       tile_entity: Type[T]) -> Optional[AreaGhost]:
    if not tile_entity.is_draggable:
        return None
    if issubclass(tile_entity, Demolisher):
        return RectangleGhostDemolish(cursor, struct_manager, cursor.pos, tile_entity)
    if issubclass(tile_entity, StructureSnapper):
        if tile_entity.drag_shape == DragShape.LINE:
            return LineGhostBuild(cursor, struct_manager, cursor.pos, tile_entity)
        if tile_entity.drag_shape == DragShape.RECTANGLE:
            return RectangleGhostBuild(cursor, struct_manager, cursor.pos, tile_entity)
    return None
