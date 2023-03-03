from __future__ import annotations

from typing import Type, TYPE_CHECKING

from src.core.enums import Message, Direction
from src.entities.snapper import Snapper
from src.entities.structure import Structure

if TYPE_CHECKING:
    from src.core.vector import Vector


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

    def save_to_json(self) -> dict:
        return {
            **super().save_to_json(),
            "neighbours": [direction.name for direction in self.neighbours]
        }

    def load_from_json(self, struct_dict: dict) -> None:
        super().load_from_json(struct_dict)
        self.add_neighbours({Direction[direction_name] for direction_name in struct_dict["neighbours"]})
