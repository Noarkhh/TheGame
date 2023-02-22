from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Type
from src.effects.area_demolisher import AreaDemolisher
from src.effects.area_builder import AreaBuilder

from src.effects.line_ghost import LineGhost
from src.effects.rectangle_ghost import RectangleGhost

from src.game_mechanics.structures import Structure
from src.game_mechanics.demolisher import Demolisher
from src.graphics.tile_entity import DragShape

if TYPE_CHECKING:
    from src.graphics.tile_entity import TileEntity
    from src.effects.area_effect import AreaEffect
    from src.effects.area_ghost import AreaGhost
    from src.game_mechanics.struct_manager import StructManager
    from src.core.cursor import Cursor


def area_ghost_factory(struct_manager: StructManager, cursor: Cursor,
                       tile_entity: Type[TileEntity]) -> Optional[AreaGhost]:
    if not tile_entity.is_draggable:
        return None
    if issubclass(tile_entity, Demolisher):
        return RectangleGhost(cursor, cursor.pos, AreaDemolisher(struct_manager))
    if issubclass(tile_entity, Structure):
        if tile_entity.drag_shape == DragShape.LINE:
            return LineGhost(cursor, cursor.pos, AreaBuilder(struct_manager, tile_entity))
        if tile_entity.drag_shape == DragShape.RECTANGLE:
            return RectangleGhost(cursor, cursor.pos, AreaBuilder(struct_manager, tile_entity))
