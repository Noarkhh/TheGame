from src.graphics.entity import Entity
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.core.vector import Vector


class Demolisher(Entity):
    def __init__(self, pos: Vector[int], image_variant: int, is_ghost: bool):
        super().__init__(pos, image_variant, is_ghost)

