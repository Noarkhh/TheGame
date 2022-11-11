from typing import Type, ClassVar
import pygame as pg
from src.core_classes import *
from src.placeholder import StructManager


class Structure(pg.sprite.Sprite):
    image_aspect_ratio: ClassVar[Vector[float]] = Vector[float](1, 1)
    covered_tiles: ClassVar[tuple[Vector[int], ...]] = (Vector[int](0, 0),)
    unsuitable_terrain: ClassVar[tuple[Terrain, ...]] = (Terrain.WATER,)
    overrider: ClassVar[bool] = False

    base_cost: ClassVar[dict[Resource, int]]
    base_profit: ClassVar[dict[Resource, int]]
    base_capacity: ClassVar[int]
    base_cooldown: ClassVar[int]

    manager: ClassVar[StructManager]

    def __init__(self, pos: Vector[int], sprite_variant: int = 0, orientation: Orientation = Orientation.VERTICAL,
                 is_ghost: bool = False) -> None:
        if is_ghost:
            super().__init__()
        else:
            super().__init__(self.manager.structs)

        self.pos: Vector[int] = pos

        self.sprite_variant: int = sprite_variant
        self.orientation: Orientation = orientation

        self.image: pg.Surface = self.manager.spritesheet.get_image(self)
        self.rect: pg.Rect = self.image.get_rect(bottomright=((self.pos + (1, 1)) * self.manager.sizes.tile).to_tuple())

        self.cost: dict[Resource, int] = self.__class__.base_cost.copy()
        self.profit: dict[Resource, int] = self.__class__.base_profit.copy()
        self.capacity: int = self.__class__.base_capacity
        self.cooldown: int = self.__class__.base_cooldown

        self.cooldown_left: int = self.base_cooldown
        self.stockpile: dict[Resource, int] = {resource: 0 for resource in self.base_profit.keys()}

    def __repr__(self):
        return f'{self.__class__.__name__}(pos: {self.pos})'

    def can_be_placed(self) -> Message:
        tile_map = self.manager.map_manager.tile_map
        struct_map = self.manager.map_manager.struct_map

        if any(tile_map[self.pos + rel_pos] in self.unsuitable_terrain for rel_pos in self.covered_tiles):
            return Message.BAD_LOCATION_TERRAIN

        if any(isinstance(struct_map[self.pos + rel_pos], Structure) for rel_pos in self.covered_tiles):
            return Message.BAD_LOCATION_STRUCT

        if any(amount > self.manager.treasury.resources[resource] for resource, amount in self.base_cost.items()):
            return Message.NO_RESOURCES

        return Message.BUILT

    def produce(self) -> None:
        self.cooldown_left -= 1
        if self.cooldown_left == 0:
            if sum(self.stockpile.values()) < self.base_capacity:
                for resource, amount in self.base_profit.items():
                    self.stockpile[resource] += amount
            self.cooldown_left = self.base_cooldown

    def update_zoom(self) -> None:
        self.image = pg.transform.scale(self.image, (self.image_aspect_ratio * self.manager.sizes.tile).to_tuple())
        self.rect = self.image.get_rect(bottomright=((self.pos + (1, 1)) * self.manager.sizes.tile).to_tuple())

    def to_json(self) -> dict:
        return {
            "type": self.__class__.__name__,
            "pos": self.pos.to_tuple(),
            "orientation": self.orientation,
            "sprite_variant": self.sprite_variant,

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


class Mine(Structure):
    image_aspect_ratio = Vector[float](1, 2)


class Sawmill(Structure):
    image_aspect_ratio = Vector[float](2, 1)
    covered_tiles = (Vector[int](0, 0), Vector[int](-1, 0))


class Tower(Structure):
    image_aspect_ratio = Vector[float](1, 2)


class Snapper(Structure):
    def __init__(self, *args, **kwargs) -> None:
        self.snaps_to: dict[Direction, Type[Structure]] = {direction: self.__class__ for direction in Direction}
        self.neighbours: DirectionSet = DirectionSet()
        super().__init__(*args, **kwargs)

    def add_neighbours(self, neighbours: DirectionSet | set) -> None:
        self.neighbours.update(neighbours)
        self.image = self.manager.spritesheet.get_image(self)

    def remove_neighbours(self, neighbours: DirectionSet | set) -> None:
        self.neighbours.difference_update(neighbours)
        self.image = self.manager.spritesheet.get_image(self)

    def can_be_snapped(self, curr_pos: Vector[int], prev_pos: Vector[int]) -> Message:
        snap_direction = (curr_pos - prev_pos).to_dir()
        struct_map = self.manager.map_manager.struct_map
        curr_struct, prev_struct = struct_map[curr_pos], struct_map[prev_pos]

        if not issubclass(curr_struct.__class__, self.__class__):
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
    pass


class Road(Snapper):
    pass


class Farmland(Snapper):
    pass


class Bridge(Snapper):
    unsuitable_terrain = (Terrain.GRASSLAND, Terrain.DESERT)


class Gate(Wall, Road):
    image_aspect_ratio = Vector[float](1, 20 / 15)
    overrider = True

    def __init__(self, *args, orientation: Orientation = Orientation.VERTICAL, **kwargs) -> None:
        super().__init__(*args, orientation, **kwargs)
        self.directions_to_connect_to: DirectionSet = DirectionSet()

        if self.orientation == Orientation.VERTICAL:
            self.snaps_to = {Direction.N: Road, Direction.E: Wall, Direction.S: Road, Direction.W: Wall}
        elif self.orientation == Orientation.HORIZONTAL:
            self.snaps_to = {Direction.N: Wall, Direction.E: Road, Direction.S: Wall, Direction.W: Road}

    def can_override(self) -> bool:
        struct_map = self.manager.map_manager.struct_map
        if not type(struct_map[self.pos]) in (Wall, Road):
            return False

        for direction_to_neighbour in Direction:
            neighbour_pos = self.pos + direction_to_neighbour.to_vector()
            neighbour = struct_map[neighbour_pos]
            if isinstance(neighbour, Snapper) and direction_to_neighbour.opposite() in neighbour.neighbours:
                if self.snaps_to[direction_to_neighbour] != neighbour.snaps_to[direction_to_neighbour.opposite()]:
                    self.directions_to_connect_to.clear()
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

        self.image: pg.Surface = self.manager.spritesheet.get_image(self)
