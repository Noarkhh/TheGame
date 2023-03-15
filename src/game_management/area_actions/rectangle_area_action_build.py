from __future__ import annotations

from collections import deque
from typing import TypeVar

from src.core.enums import Message
from src.entities.structure_snapper import StructureSnapper
from src.game_management.area_actions.rectangle_area_action import RectangleAreaAction

S = TypeVar("S", bound=StructureSnapper)


class RectangleAreaActionBuild(RectangleAreaAction[S]):

    def resolve(self) -> None:
        segments_queue: deque[tuple[int, int]] = deque([self.origin.to_tuple()])
        visited: set[tuple[int, int]] = set()
        success_sound: bool = False
        build_message: Message = Message.BUILT

        while len(segments_queue) > 0:
            segment_position = segments_queue.pop()
            if segment_position in visited:
                continue
            visited.add(segment_position)
            segment_to_place = self.segments[segment_position]

            build_message = self.struct_manager.build(segment_to_place, success_sound=False)
            if not (build_message.success() or build_message == Message.BAD_LOCATION_STRUCT):
                continue
            if build_message.success():
                success_sound = True

            for neighbour_pos in segment_to_place.pos.neighbours():
                if neighbour_pos.to_tuple() not in self.segments:
                    continue
                test_snap_message = segment_to_place.can_be_snapped(neighbour_pos, self.tile_entity_class)
                if test_snap_message not in (Message.SNAPPED, Message.ALREADY_SNAPPED, Message.OTHER_IS_NONE):
                    continue
                segments_queue.append(neighbour_pos.to_tuple())
                snap_message = self.struct_manager.snap(segment_to_place.pos, neighbour_pos,
                                                        self.tile_entity_class, success_sound=False)
                if snap_message.success():
                    success_sound = True

        build_message = Message.BUILT if success_sound else build_message
        self.struct_manager.sound_player.handle_placement_sounds(not success_sound, success_sound, build_message)

        self.kill_segments()
