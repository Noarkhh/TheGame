from __future__ import annotations
from src.core.enums import *
from src.game_mechanics.structure import Structure
from src.game_mechanics.snapper import Snapper


class StructureSnapper(Structure, Snapper):
    def can_be_snapped(self, curr_pos: Vector[int], prev_pos: Vector[int]) -> Message:
        snap_direction = (curr_pos - prev_pos).to_dir()
        struct_map = self.manager.map_manager.struct_map
        curr_struct = struct_map[curr_pos]
        prev_struct = struct_map[prev_pos]

        if not issubclass(curr_struct.__class__, self.__class__) and \
                not issubclass(prev_struct.__class__, self.__class__):
            return Message.BAD_CONNECTOR

        if snap_direction is None:
            return Message.NOT_ADJACENT

        if not isinstance(curr_struct, StructureSnapper) or not isinstance(prev_struct, StructureSnapper):
            return Message.ONE_CANT_SNAP

        if curr_struct.snaps_to[snap_direction.opposite()] != prev_struct.snaps_to[snap_direction]:
            return Message.BAD_MATCH

        if snap_direction.opposite() in curr_struct.neighbours:
            return Message.ALREADY_SNAPPED

        return Message.SNAPPED

    def to_json(self) -> dict:
        return {
            **super().to_json(),
            "neighbours": tuple(self.neighbours)
        }

    def from_json(self, y: dict) -> None:
        super().from_json(y)
        self.add_neighbours(DirectionSet(y["neighbours"]))
