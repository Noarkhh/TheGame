from __future__ import annotations
from typing import TYPE_CHECKING
from src.effects.rectangle_ghost import RectangleGhost
from src.game_mechanics.demolisher import Demolisher

if TYPE_CHECKING:
    from src.game_mechanics.struct_manager import StructManager
    from src.core.vector import Vector


class RectangleGhostDemolish(RectangleGhost[Demolisher]):

    def resolve(self) -> None:
        self.kill_segments()

