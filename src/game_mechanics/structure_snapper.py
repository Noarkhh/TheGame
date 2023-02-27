from __future__ import annotations

from typing import Type

from src.core.enums import *
from src.game_mechanics.structure import Structure
from src.game_mechanics.snapper import Snapper


class StructureSnapper(Structure, Snapper):
    def can_be_snapped(self, other_pos: Vector[int], connector: Type[Structure]) -> Message:
        snap_direction = (self.pos - other_pos).to_dir()
        struct_map = self.manager.map_manager.struct_map
        other_struct = struct_map[other_pos]

        if not issubclass(self.__class__, connector) and not issubclass(other_struct.__class__, connector):
            return Message.BAD_CONNECTOR

        if snap_direction is None:
            return Message.NOT_ADJACENT

        if other_struct is None:
            return Message.OTHER_IS_NONE

        if not isinstance(other_struct, StructureSnapper):
            return Message.OTHER_CANT_SNAP

        if self.snaps_to[snap_direction.opposite()] != other_struct.snaps_to[snap_direction]:
            return Message.BAD_MATCH

        if snap_direction.opposite() in self.neighbours:
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