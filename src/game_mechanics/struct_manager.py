from __future__ import annotations

from typing import cast, Type

from src.core.vector import Vector
from src.entities.structures import *

if TYPE_CHECKING:
    from src.core.config import Config
    from src.game_mechanics.map import Map
    from src.game_mechanics.map_container import MapContainer
    from src.game_mechanics.treasury import Treasury
    from src.sound.sound_player import SoundPlayer


class StructManager:
    def __init__(self, config: Config, map_container: MapContainer,
                 treasury: Treasury, sound_player: SoundPlayer) -> None:
        Structure.manager = self
        config.set_structures_parameters()

        self.map_container: MapContainer = map_container
        self.treasury: Treasury = treasury
        self.sound_player: SoundPlayer = sound_player

        self.structs: pg.sprite.Group[Structure] = pg.sprite.Group()

    def update(self) -> None:
        self.structs.update()

    def build(self, new_struct: Structure, failure_sound: bool = False, success_sound: bool = True) -> Message:
        struct_map: Map[Structure] = self.map_container.struct_map

        build_message: Message = new_struct.can_be_placed()

        if build_message.success():
            if build_message == Message.BUILT:
                new_struct = new_struct.copy()
                new_struct.build()
                for relative_pos in new_struct.covered_tiles:
                    struct_map[new_struct.pos + relative_pos] = new_struct

            elif build_message == Message.OVERRODE:
                new_struct = new_struct.copy(cast(Gate, new_struct).directions_to_connect_to)
                cast(Structure, struct_map[new_struct.pos]).kill()
                struct_map[new_struct.pos] = new_struct

        self.sound_player.handle_placement_sounds(failure_sound, success_sound, build_message)

        return build_message

    def snap(self, position1: Vector[int], position2: Vector[int], connector: Type[Structure],
             failure_sound: bool = False, success_sound: bool = True) -> Message:
        struct1 = self.map_container.struct_map[position1]
        struct2 = self.map_container.struct_map[position2]

        if struct1 is None:
            return Message.NOT_A_SNAPPER

        snap_message: Message = struct1.can_be_snapped(position2, connector)

        if snap_message == Message.SNAPPED:
            snap_direction = cast(Direction, (position1 - position2).to_dir())
            cast(StructureSnapper, struct1).add_neighbours(snap_direction.opposite())
            cast(StructureSnapper, struct2).add_neighbours(snap_direction)

        self.sound_player.handle_snapping_sounds(failure_sound, success_sound, snap_message)

        return snap_message

    def demolish(self, position: Vector[int], demolish_sound: bool = False) -> bool:
        struct_to_demolish = self.map_container.struct_map.elements.pop(position.to_tuple(), None)
        if struct_to_demolish is None:
            return False
        for relative_pos in struct_to_demolish.covered_tiles:
            self.map_container.struct_map.pop(struct_to_demolish.pos + relative_pos)
        struct_to_demolish.demolish()
        if demolish_sound:
            self.sound_player.play_fx("buildingwreck")
        return True

    def save_to_json(self) -> dict[str, dict[str, Any]]:
        return {f"({struct.pos.x},{struct.pos.y})": struct.save_to_json() for struct in self.structs}

    def load_from_json(self, structures_dict: dict[str, dict[str, Any]]) -> None:
        for struct in self.structs:
            struct.kill()
        for pos_str, struct_dict in structures_dict.items():
            pos_tuple = pos_str[1:-1].split(",")
            struct_position = Vector(int(pos_tuple[0]), int(pos_tuple[1]))
            loaded_struct = globals()[struct_dict["type"]](struct_position,
                                                           orientation=Orientation[struct_dict["orientation"]],
                                                           image_variant=struct_dict["image_variant"])
            assert isinstance(loaded_struct, Structure)

            loaded_struct.load_from_json(struct_dict)
            for relative_pos in loaded_struct.covered_tiles:
                self.map_container.struct_map[loaded_struct.pos + relative_pos] = loaded_struct
