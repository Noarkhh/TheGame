from abc import ABCMeta
from enum import Enum, auto
from typing import ClassVar, Optional, TYPE_CHECKING

from src.core.enums import Tile
from src.core.vector import Vector
from src.entities.entity import Entity

if TYPE_CHECKING:
    pass


class DragShape(Enum):
    RECTANGLE = auto()
    LINE = auto()


class TileEntity(Entity, metaclass=ABCMeta):
    image_aspect_ratio: ClassVar[Vector[float]] = Vector[float](1, 1)
    covered_tiles: ClassVar[list[Vector[int]]] = [Vector[int](0, 0)]
    is_draggable: ClassVar[bool] = False
    drag_shape: ClassVar[Optional[DragShape]] = None

    def __init__(self, pos: Vector[int], image_variant: int, is_ghost: bool) -> None:
        self.pos: Vector[int] = pos
        self.is_ghost: bool = is_ghost

        super().__init__((self.pos + (1, 1)) * Tile.size, image_variant, 128 if is_ghost else 255)

    def update_rect(self) -> None:
        self.rect = self.image.get_rect(bottomright=((self.pos + (1, 1)) * Tile.size).to_tuple())
