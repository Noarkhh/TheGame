from __future__ import annotations
import pygame as pg
from typing import Type, ClassVar, cast, Any, Self
from src.core.enums import *
from src.graphics.tile_entity import TileEntity, DragShape
from abc import ABCMeta
if TYPE_CHECKING:
    from src.game_mechanics.struct_manager import StructManager


class Structure(TileEntity, metaclass=ABCMeta):
    unsuitable_terrain: ClassVar[list[Terrain]] = [Terrain.WATER]
    overrider: ClassVar[bool] = False

    base_cost: ClassVar[dict[Resource, int]]
    base_profit: ClassVar[dict[Resource, int]]
    base_capacity: ClassVar[int]
    base_cooldown: ClassVar[int]

    manager: ClassVar[StructManager]

    def __init__(self, pos: Vector[int], image_variant: int = 0, orientation: Orientation = Orientation.VERTICAL,
                 is_ghost: bool = False) -> None:
        super().__init__(pos, image_variant, is_ghost)

        self.orientation: Orientation = orientation

        if not self.is_ghost:
            self.manager.structs.add(self)

        self.cost: dict[Resource, int] = self.base_cost.copy()
        self.profit: dict[Resource, int] = self.base_profit.copy()
        self.capacity: int = self.base_capacity
        self.cooldown: int = self.base_cooldown

        self.cooldown_left: int = self.cooldown
        self.stockpile: dict[Resource, int] = {resource: 0 for resource in self.base_profit.keys()}

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(pos: {self.pos})'

    def can_be_placed(self) -> Message:
        tile_map = self.manager.map_manager.tile_map
        struct_map = self.manager.map_manager.struct_map

        if any(cast(Tile, tile_map[self.pos + rel_pos]).terrain in
               self.unsuitable_terrain for rel_pos in self.covered_tiles):
            return Message.BAD_LOCATION_TERRAIN

        if any(isinstance(struct_map[self.pos + rel_pos], Structure) for rel_pos in self.covered_tiles):
            return Message.BAD_LOCATION_STRUCT

        if any(amount > self.manager.treasury.resources[resource] for resource, amount in self.base_cost.items()):
            return Message.NO_RESOURCES

        return Message.BUILT

    def can_be_snapped(self, curr_pos: Vector[int], prev_pos: Vector[int]) -> Message:
        return Message.NOT_A_SNAPPER

    def produce(self) -> None:
        self.cooldown_left -= 1
        if self.cooldown_left == 0:
            if sum(self.stockpile.values()) < self.base_capacity:
                for resource, amount in self.base_profit.items():
                    self.stockpile[resource] += amount
            self.cooldown_left = self.base_cooldown

    def copy(self: Self, neighbours: Optional[DirectionSet] = None) -> Self:
        new_copy = self.__class__(self.pos, image_variant=self.image_variant, orientation=self.orientation)
        if neighbours is not None:
            assert isinstance(new_copy, Snapper)
            new_copy.add_neighbours(neighbours)
        return new_copy

    def to_json(self) -> dict:
        return {
            "type": self.__class__.__name__,
            "pos": self.pos.to_tuple(),
            "orientation": self.orientation,
            "sprite_variant": self.image_variant,

            "cost": {resource.name: amount for resource, amount in self.base_cost.items()},
            "profit": {resource.name: amount for resource, amount in self.base_cost.items()},
            "capacity": self.base_capacity,
            "cooldown": self.base_cooldown,
            "cooldown_left": self.cooldown_left,
            "stockpile": {resource.name: amount for resource, amount in self.stockpile.items()}
        }

    def from_json(self, y: dict) -> None:
        self.cost = {Resource[name]: amount for name, amount in y["cost"]}
        self.profit = {Resource[name]: amount for name, amount in y["profit"]}
        self.capacity = y["capacity"]
        self.cooldown = y["cooldown"]
        self.cooldown_left = y["cooldown_left"]
        self.stockpile = {Resource[name]: amount for name, amount in y["stockpile"]}


class House(Structure):
    image_aspect_ratio = Vector[float](1, 21 / 15)
    image_variants = 2


class Mine(Structure):
    image_aspect_ratio = Vector[float](1, 2)


class Sawmill(Structure):
    image_aspect_ratio = Vector[float](2, 1)
    covered_tiles = [Vector[int](0, 0), Vector[int](-1, 0)]


class Tower(Structure):
    image_aspect_ratio = Vector[float](1, 2)


class Snapper(Structure):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.snaps_to: dict[Direction, Type[Structure]] = {direction: self.__class__ for direction in Direction}
        self.neighbours: DirectionSet = DirectionSet()
        super().__init__(*args, **kwargs)

    def add_neighbours(self, neighbours: DirectionSet | set | Direction) -> None:
        if isinstance(neighbours, Direction):
            self.neighbours.add(neighbours)
        else:
            self.neighbours.update(neighbours)
        self.image = self.get_image()

    def remove_neighbours(self, neighbours: DirectionSet | set | Direction) -> None:
        if isinstance(neighbours, Direction):
            self.neighbours.remove(neighbours)
        else:
            self.neighbours.difference_update(neighbours)
        self.image = self.get_image()

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

        if not isinstance(curr_struct, Snapper) or not isinstance(prev_struct, Snapper):
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


class Wall(Snapper):
    is_draggable = True
    drag_shape = DragShape.LINE
    pass


class Road(Snapper):
    is_draggable = True
    drag_shape = DragShape.LINE
    pass


class Farmland(Snapper):
    is_draggable = True
    drag_shape = DragShape.RECTANGLE
    pass


class Bridge(Snapper):
    is_draggable = True
    drag_shape = DragShape.LINE
    unsuitable_terrain = [Terrain.GRASSLAND, Terrain.DESERT]

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.snaps_to = {direction: Road for direction in Direction}


class Gate(Wall, Road):
    image_aspect_ratio = Vector[float](1, 20 / 15)
    overrider = True

    def __init__(self, *args: Any, image_variant: int = 0,
                 orientation: Orientation = Orientation.VERTICAL, **kwargs: Any) -> None:
        super().__init__(*args, image_variant=orientation, orientation=orientation, **kwargs)

        if self.orientation == Orientation.VERTICAL:
            self.snaps_to = {Direction.N: Road, Direction.E: Wall, Direction.S: Road, Direction.W: Wall}
        elif self.orientation == Orientation.HORIZONTAL:
            self.snaps_to = {Direction.N: Wall, Direction.E: Road, Direction.S: Wall, Direction.W: Road}
        self.directions_to_connect_to: DirectionSet = DirectionSet()

    def can_override(self) -> bool:
        struct_map = self.manager.map_manager.struct_map
        self.directions_to_connect_to.clear()

        if not type(struct_map[self.pos]) in (Wall, Road):
            return False

        for direction_to_neighbour in Direction:
            neighbour_pos = self.pos + direction_to_neighbour.to_vector()
            neighbour = struct_map[neighbour_pos]
            if isinstance(neighbour, Snapper) and direction_to_neighbour.opposite() in neighbour.neighbours:
                if self.snaps_to[direction_to_neighbour] != neighbour.snaps_to[direction_to_neighbour.opposite()]:
                    return False
                self.directions_to_connect_to.add(direction_to_neighbour)

        return True

    def can_be_placed(self) -> Message:
        message = super().can_be_placed()
        if message == Message.BAD_LOCATION_STRUCT and self.can_override():
            message = Message.OVERRODE
        return message

    def rotate(self) -> None:
        if self.orientation == Orientation.VERTICAL:
            self.orientation = Orientation.HORIZONTAL
            self.snaps_to = {Direction.N: Wall, Direction.E: Road, Direction.S: Wall, Direction.W: Road}
        elif self.orientation == Orientation.HORIZONTAL:
            self.orientation = Orientation.VERTICAL
            self.snaps_to = {Direction.N: Road, Direction.E: Wall, Direction.S: Road, Direction.W: Wall}

        self.image_variant = self.orientation
        self.image: pg.Surface = self.get_image()
