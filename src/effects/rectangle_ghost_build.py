from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar
from collections import deque

from src.effects.rectangle_ghost import RectangleGhost
from src.game_mechanics.structure_snapper import StructureSnapper
from src.core.vector import Vector
from src.core.enums import Direction, Message

if TYPE_CHECKING:
    pass

S = TypeVar("S", bound=StructureSnapper)


class RectangleGhostBuild(RectangleGhost[S]):

    def resolve(self) -> None:
        segments_queue: deque[tuple[int, int]] = deque([self.origin.to_tuple()])
        visited: set[tuple[int, int]] = set()
        while len(segments_queue) > 0:
            current_segment = segments_queue.pop()
            new_struct = self.segments[current_segment]

            build_message = self.struct_manager.place(new_struct)
            if not (build_message.success() or build_message == Message.BAD_LOCATION_STRUCT) or current_segment in visited:
                continue
            visited.add(current_segment)
            for direction in Direction:
                neighbour_pos = new_struct.pos + direction.to_vector()
                if neighbour_pos.to_tuple() not in self.segments:
                    continue
                segments_queue.append(neighbour_pos.to_tuple())
                self.struct_manager.snap(new_struct.pos, neighbour_pos, self.tile_entity_class).success()

        self.kill_segments()


