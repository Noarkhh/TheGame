from __future__ import annotations
import pygame as pg
from typing import cast
from src.core_classes import *
from src.structures import Structure

if TYPE_CHECKING:
    from src.config import Config
    from src.map import MapManager, Map
    from src.spritesheet import Spritesheet
    from src.treasury import Treasury
    from src.entities import Entities
    from src.structures import Snapper


class StructManager:
    def __init__(self, config: Config, map_manager: MapManager, spritesheet: Spritesheet, treasury: Treasury,
                 entities: Entities):
        Structure.manager = self
        config.set_structures_parameters()

        self.map_manager: MapManager = map_manager
        self.spritesheet: Spritesheet = spritesheet
        self.treasury: Treasury = treasury

        self.entities: Entities = entities
        self.structs: pg.sprite.Group = pg.sprite.Group()

    def place(self, new_struct: Structure, previous_pos: Vector[int]) -> Message:
        struct_map: Map[Structure] = self.map_manager.struct_map

        build_message: Message = new_struct.can_be_placed()

        if build_message.success():
            if build_message == Message.BUILT:
                for relative_pos in new_struct.covered_tiles:
                    struct_map[new_struct.pos + relative_pos] = new_struct
            if build_message == Message.OVERRODE:
                cast(Structure, struct_map[new_struct.pos]).kill()
                struct_map[new_struct.pos] = new_struct
            self.treasury.pay_for(new_struct)

        snap_message: Message = new_struct.can_be_snapped(new_struct.pos, previous_pos)

        if snap_message == Message.SNAPPED:
            snap_direction = cast(Direction, (new_struct.pos - previous_pos).to_dir())
            cast(Snapper, new_struct).add_neighbours(snap_direction.opposite())
            cast(Snapper, struct_map[previous_pos]).add_neighbours(snap_direction)



        return build_message
