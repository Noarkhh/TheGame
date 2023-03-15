from __future__ import annotations

from src.core.vector import Vector
from src.entities.demolisher import Demolisher
from src.game_management.area_actions.rectangle_area_action import RectangleAreaAction


class RectangleAreaActionDemolish(RectangleAreaAction[Demolisher]):

    def resolve(self) -> None:
        demolish_sound: bool = False
        for segment_pos in self.segments:
            if self.struct_manager.demolish(Vector(segment_pos)):
                demolish_sound = True
        if demolish_sound:
            self.struct_manager.sound_player.play_fx("buildingwreck")
        self.kill_segments()
