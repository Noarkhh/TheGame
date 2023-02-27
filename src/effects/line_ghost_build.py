from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar, Optional

from src.core.vector import Vector
from src.core.enums import Message
from src.effects.line_ghost import LineGhost
from src.game_mechanics.structure_snapper import StructureSnapper

if TYPE_CHECKING:
    pass

S = TypeVar("S", bound=StructureSnapper)


class LineGhostBuild(LineGhost[S]):

    def resolve(self) -> None:
        def dist_from_origin(segment: tuple[int, int]) -> int:
            return abs(segment[0] - self.origin.x) + abs(segment[1] - self.origin.y)

        segments_to_build: list[Vector[int]] = [Vector(pos) for pos in sorted(self.segments, key=dist_from_origin)]

        previous_segment_position: Optional[Vector[int]] = None
        success_sound: bool = False
        build_message: Message = Message.BUILT

        for segment_position in segments_to_build:
            segment_to_place = self.segments[segment_position.to_tuple()]
            build_message = self.struct_manager.build(segment_to_place, success_sound=False)
            if not (build_message.success() or build_message == Message.BAD_LOCATION_STRUCT):
                break
            if previous_segment_position is None and build_message == Message.BAD_LOCATION_STRUCT:
                second_segment = self.segments[segments_to_build[1].to_tuple()]
                test_snap_message = second_segment.can_be_snapped(segment_position, self.tile_entity_class)
                if not (test_snap_message.success() or test_snap_message == Message.ALREADY_SNAPPED):
                    break

            if build_message.success():
                success_sound = True

            if previous_segment_position is not None:
                snap_message = self.struct_manager.snap(segment_position, previous_segment_position,
                                                        self.tile_entity_class, success_sound=False)
                if not (snap_message.success() or snap_message == Message.ALREADY_SNAPPED):
                    break
                if snap_message.success():
                    success_sound = True

            previous_segment_position = segment_position

        build_message = Message.BUILT if success_sound else build_message
        self.struct_manager.sound_manager.handle_placement_sounds(not success_sound, success_sound, build_message)

        self.kill_segments()
