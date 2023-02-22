from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.core.vector import Vector
    from src.game_mechanics.struct_manager import StructManager


class AreaEffect(ABC):
    struct_manager: StructManager
    vector: Vector

    def __init__(self, struct_manager: StructManager):
        self.struct_manager = struct_manager

    @abstractmethod
    def resolve(self, tiles_to_affect: list[Vector[int]]) -> None: ...

