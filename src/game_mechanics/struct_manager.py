from __future__ import annotations
import pygame as pg
from typing import cast
from src.core_classes import *
from src.game_mechanics.structures import Structure, Snapper, Gate

if TYPE_CHECKING:
    from src.config import Config
    from src.game_mechanics.map import Map
    from src.game_mechanics.map_manager import MapManager
    from src.game_mechanics.treasury import Treasury


class StructManager:
    def __init__(self, config: Config, map_manager: MapManager, treasury: Treasury):
        Structure.manager = self
        config.set_structures_parameters()

        self.map_manager: MapManager = map_manager
        self.treasury: Treasury = treasury

        self.structs: pg.sprite.Group[Structure] = pg.sprite.Group()

    def place(self, new_struct: Structure, previous_pos: Vector[int], play_failure_sounds: bool = False,
              play_success_sound: bool = True) -> Message:
        struct_map: Map[Structure] = self.map_manager.struct_map

        build_message: Message = new_struct.can_be_placed()

        if build_message.success():
            if build_message == Message.BUILT:
                new_struct = new_struct.copy()
                for relative_pos in new_struct.covered_tiles:
                    struct_map[new_struct.pos + relative_pos] = new_struct

            if build_message == Message.OVERRODE:
                new_struct = new_struct.copy(cast(Gate, new_struct).directions_to_connect_to)
                cast(Structure, struct_map[new_struct.pos]).kill()
                struct_map[new_struct.pos] = new_struct

            self.treasury.pay_for(new_struct)

        snap_message: Message = new_struct.can_be_snapped(new_struct.pos, previous_pos)

        if snap_message == Message.SNAPPED:
            snap_direction = cast(Direction, (new_struct.pos - previous_pos).to_dir())
            cast(Snapper, struct_map[new_struct.pos]).add_neighbours(snap_direction.opposite())
            cast(Snapper, struct_map[previous_pos]).add_neighbours(snap_direction)


        return build_message

