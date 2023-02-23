from __future__ import annotations
from typing import Type, TYPE_CHECKING
from src.effects.area_action import AreaAction
if TYPE_CHECKING:
    from src.game_mechanics.structures import Structure
    from src.game_mechanics.struct_manager import StructManager
    from src.core.vector import Vector


class AreaBuilder(AreaAction):
    class_to_build: Type[Structure]

    def __init__(self, struct_manager: StructManager, class_to_build: Type[Structure]) -> None:
        super().__init__(struct_manager)
        self.class_to_build = class_to_build

    def resolve(self, tiles_to_affect: list[Vector[int]]) -> None:
        pass

