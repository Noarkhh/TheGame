from __future__ import annotations
from typing import TYPE_CHECKING
from src.effects.area_action import AreaAction

if TYPE_CHECKING:
    from src.game_mechanics.struct_manager import StructManager
    from src.core.vector import Vector


class AreaDemolisher(AreaAction):

    def __init__(self, struct_manager: StructManager) -> None:
        super().__init__(struct_manager)

    def resolve(self, tiles_to_affect: list[Vector[int]]) -> None:
        pass

