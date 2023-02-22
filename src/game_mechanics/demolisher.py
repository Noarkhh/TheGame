from __future__ import annotations
from src.graphics.tile_entity import TileEntity, DragShape
from typing import TYPE_CHECKING
from src.core.vector import Vector


class Demolisher(TileEntity):
    is_draggable = True
    drag_shape = DragShape.RECTANGLE

    def __init__(self, pos: Vector[int], image_variant: int, is_ghost: bool):
        super().__init__(pos, image_variant, is_ghost)

