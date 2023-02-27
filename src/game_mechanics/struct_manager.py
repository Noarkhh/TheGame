from __future__ import annotations
import pygame as pg
from typing import cast, Type
from src.core.enums import *
from src.game_mechanics.structures import Snapper, Gate
from src.game_mechanics.structure import Structure
from src.game_mechanics.structure_snapper import StructureSnapper

if TYPE_CHECKING:
    from src.core.config import Config
    from src.game_mechanics.map import Map
    from src.game_mechanics.map_manager import MapManager
    from src.game_mechanics.treasury import Treasury
    from src.sound.sound_manager import SoundManager


class StructManager:
    def __init__(self, config: Config, map_manager: MapManager, treasury: Treasury, sound_manager: SoundManager) -> None:
        Structure.manager = self
        config.set_structures_parameters()

        self.map_manager: MapManager = map_manager
        self.treasury: Treasury = treasury
        self.sound_manager: SoundManager = sound_manager

        self.structs: pg.sprite.Group[Structure] = pg.sprite.Group()

    def build(self, new_struct: Structure, failure_sound: bool = False, success_sound: bool = True) -> Message:
        struct_map: Map[Structure] = self.map_manager.struct_map

        build_message: Message = new_struct.can_be_placed()

        if build_message.success():
            if build_message == Message.BUILT:
                new_struct = new_struct.copy()
                for relative_pos in new_struct.covered_tiles:
                    struct_map[new_struct.pos + relative_pos] = new_struct

            elif build_message == Message.OVERRODE:
                new_struct = new_struct.copy(cast(Gate, new_struct).directions_to_connect_to)
                cast(Structure, struct_map[new_struct.pos]).kill()
                struct_map[new_struct.pos] = new_struct

            self.treasury.pay_for(new_struct)

        self.sound_manager.handle_placement_sounds(failure_sound, success_sound, build_message)

        return build_message

    def snap(self, position1: Vector[int], position2: Vector[int], connector: Type[Structure],
             failure_sound: bool = False, success_sound: bool = True) -> Message:
        struct1 = self.map_manager.struct_map[position1]
        struct2 = self.map_manager.struct_map[position2]

        if struct1 is None:
            return Message.NOT_A_SNAPPER

        snap_message: Message = struct1.can_be_snapped(position2, connector)

        if snap_message == Message.SNAPPED:
            snap_direction = cast(Direction, (position1 - position2).to_dir())
            cast(Snapper, struct1).add_neighbours(snap_direction.opposite())
            cast(Snapper, struct2).add_neighbours(snap_direction)

        self.sound_manager.handle_snapping_sounds(failure_sound, success_sound, snap_message)

        return snap_message

    def demolish(self, position: Vector[int], demolish_sound: bool = False) -> bool:
        struct_to_demolish = self.map_manager.struct_map.pop(position)
        if struct_to_demolish is None:
            return False
        struct_to_demolish.kill()
        if demolish_sound:
            self.sound_manager.play_fx("buildingwreck")
        if not isinstance(struct_to_demolish, StructureSnapper):
            return True
        for direction_to_neighbour in struct_to_demolish.neighbours:
            neighbour = self.map_manager.struct_map[position + direction_to_neighbour.to_vector()]
            cast(StructureSnapper, neighbour).remove_neighbours(direction_to_neighbour.opposite())
        return True
