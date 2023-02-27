from __future__ import annotations

from src.core.vector import Vector
from src.effects.rectangle_ghost import RectangleGhost
from src.game_mechanics.demolisher import Demolisher


class RectangleGhostDemolish(RectangleGhost[Demolisher]):

    def resolve(self) -> None:
        demolish_sound: bool = False
        for segment_pos in self.segments:
            if self.struct_manager.demolish(Vector(segment_pos)):
                demolish_sound = True
        if demolish_sound:
            self.struct_manager.sound_manager.play_sound("buildingwreck")
        self.kill_segments()

