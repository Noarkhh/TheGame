from __future__ import annotations
from typing import TypeVar
import pygame as pg
import json
from core_classes import *

T = TypeVar('T')


class Map:
    def __init__(self, size: Vector) -> None:
        self.elements: list[list[T]] = [[None for _ in range(size.y)] for _ in range(size.x)]
        self.size: Vector = size

    def __getitem__(self, pos: Vector | tuple) -> T:
        if isinstance(pos, Vector):
            return self.elements[pos.x][pos.y]
        elif isinstance(pos, tuple):
            return self.elements[pos[0]][pos[1]]

    def __setitem__(self, pos: Vector | tuple, element: T) -> None:
        if isinstance(pos, Vector):
            self.elements[pos.x][pos.y] = element
        elif isinstance(pos, tuple):
            self.elements[pos[0]][pos[1]] = element

    def __str__(self) -> str:
        return "\n".join([" ".join([str(self[x, y]) for x in range(self.size.x)]) for y in range(self.size.y)])

    def contains(self, pos: Vector) -> bool:
        return 0 <= pos.x < self.size.x and 0 <= pos.y < self.size.y


class Message(Enum):
    BAD_LOCATION_TERRAIN = 0
    BAD_LOCATION_STRUCT = 1
    NO_RESOURCES = 2

    NOT_ADJACENT = 3
    ONE_CANT_SNAP = 4
    BAD_MATCH = 5
    ALREADY_SNAPPED = 6

    CANT_OVERRIDE = 7

    BUILT = 8
    SNAPPED = 9
    OVERRODE = 10


class Spritesheet:
    def __init__(self, sizes) -> None:
        self.sheet: pg.Surface = pg.image.load("assets/spritesheet.png")
        self.snapper_sheet: pg.Surface = pg.image.load("assets/snapper_sheet.png")
        with open("config/spritesheet_coords.json", "r") as f:
            self.coords = json.load(f)
        self.sizes: Sizes = sizes

    def get_image(self, obj: Structure | Terrain) -> pg.Surface:
        if isinstance(obj, Snapper):
            target_rect = pg.Rect(
                [obj.neighbours.get_id() * 15] + self.coords["Snappers"][obj.__class__.__name__][obj.sprite_variant])
            new_surf = pg.Surface(target_rect.size)
            new_surf.blit(self.snapper_sheet, (0, 0), target_rect)
        elif isinstance(obj, Structure):
            target_rect = pg.Rect(self.coords["Structures"][obj.__class__.__name__][obj.sprite_variant])
            new_surf = pg.Surface(target_rect.size)
            new_surf.blit(self.sheet, (0, 0), target_rect)
        elif isinstance(obj, Terrain):
            target_rect = pg.Rect(self.coords["TileTypes"][obj.name])
            new_surf = pg.Surface(target_rect.size)
            new_surf.blit(self.sheet, (0, 0), target_rect)
        else:
            raise ValueError

        new_surf.set_colorkey((255, 255, 255), pg.RLEACCEL)
        return pg.transform.scale(new_surf, (obj.surf_aspect_ratio[0] * self.sizes.tile,
                                             obj.surf_aspect_ratio[1] * self.sizes.tile))


class Structure(pg.sprite.Sprite):
    surf_aspect_ratio: tuple[int, int | float] = (1, 1)
    covered_tiles: tuple[Vector, ...] = (Vector(0, 0),)
    unsuitable_terrain: tuple[Terrain, ...] = (Terrain.WATER,)
    overrider: bool = False

    cost: dict[Resource, int]
    profit: dict[Resource, int]
    capacity: int
    cooldown: int

    manager: StructManager

    def __init__(self, pos: Vector, sprite_variant: int = 0, orientation: Orientation = Orientation.VERTICAL,
                 is_ghost: bool = False) -> None:
        super().__init__(self.manager.structs if not is_ghost else ())

        self.pos: Vector = pos

        self.sprite_variant: int = sprite_variant
        self.orientation: Orientation = orientation

        self.image: pg.Surface = self.manager.spritesheet.get_image(self)
        self.rect: pg.Rect = self.image.get_rect(bottomright=((self.pos + (1, 1)) * self.manager.sizes.tile).to_tuple())

        self.cost: dict[Resource, int] = self.__class__.cost.copy()
        self.profit: dict[Resource, int] = self.__class__.profit.copy()
        self.capacity: int = self.__class__.capacity
        self.cooldown: int = self.__class__.cooldown

        self.cooldown_left: int = self.cooldown
        self.stockpile: dict[Resource, int] = {resource: 0 for resource in self.profit.keys()}

    def __repr__(self):
        return f'{self.__class__.__name__}(pos: {self.pos})'

    def can_be_placed(self, map_manager: MapManager) -> tuple[bool, Message]:

        if any(map_manager.tile_map[self.pos + rel_pos] in self.unsuitable_terrain for rel_pos in
               self.covered_tiles):
            return False, Message.BAD_LOCATION_TERRAIN

        if any(isinstance(map_manager.struct_map[self.pos + rel_pos], Structure) for rel_pos in self.covered_tiles):
            return False, Message.BAD_LOCATION_STRUCT

        if any(amount > self.manager.treasury.resources[resource] for resource, amount in self.cost.items()):
            return False, Message.NO_RESOURCES

        return True, Message.BUILT

    def produce(self) -> None:
        self.cooldown_left -= 1
        if self.cooldown_left == 0:
            if sum(self.stockpile.values()) < self.capacity:
                for resource, amount in self.profit.items():
                    self.stockpile[resource] += amount
            self.cooldown_left = self.cooldown

    def update_zoom(self) -> None:
        self.image = pg.transform.scale(self.image, (self.surf_aspect_ratio[0] * self.manager.sizes.tile,
                                                     self.surf_aspect_ratio[1] * self.manager.sizes.tile))
        self.rect = self.image.get_rect(bottomright=((self.pos + (1, 1)) * self.manager.sizes.tile).to_tuple())

    def to_json(self) -> dict:
        return {
            "type": self.__class__.__name__,
            "pos": self.pos.to_tuple(),
            "orientation": self.orientation,
            "sprite_variant": self.sprite_variant,

            "cost": {resource.name: amount for resource, amount in self.cost},
            "profit": {resource.name: amount for resource, amount in self.cost},
            "capacity": self.capacity,
            "cooldown": self.cooldown,
            "cooldown_left": self.cooldown_left,
            "stockpile": {resource.name: amount for resource, amount in self.stockpile}
        }

    def from_json(self, y: dict) -> None:
        self.cost = {Resource[name]: amount for name, amount in y["cost"]}
        self.profit = {Resource[name]: amount for name, amount in y["profit"]}
        self.capacity = y["capacity"]
        self.cooldown = y["cooldown"]
        self.cooldown_left = y["cooldown_left"]
        self.stockpile = {Resource[name]: amount for name, amount in y["stockpile"]}


class House(Structure):
    surf_aspect_ratio = (1, 21 / 15)


class Mine(Structure):
    surf_aspect_ratio = (1, 2)


class Sawmill(Structure):
    surf_aspect_ratio = (2, 1)
    covered_tiles = (Vector(0, 0), Vector(-1, 0))


class Snapper(Structure):
    def __init__(self, *args, **kwargs) -> None:
        self.snaps_to: dict[Direction, Structure] = {direction: self.__class__ for direction in Direction}
        self.neighbours: DirectionSet = DirectionSet()
        super().__init__(*args, **kwargs)

    def add_neighbours(self, neighbours: DirectionSet | set) -> None:
        self.neighbours.update(neighbours)
        self.image = self.manager.spritesheet.get_image(self)

    def remove_neighbours(self, neighbours: DirectionSet | set) -> None:
        self.neighbours.difference_update(neighbours)
        self.image = self.manager.spritesheet.get_image(self)

    def can_be_snapped(self, prev_pos) -> tuple[bool, Message]:
        snap_direction = (self.pos - prev_pos).to_dir()
        struct_map = self.manager.map_manager.struct_map
        if snap_direction is None:
            return False, Message.NOT_ADJACENT

        if not isinstance(struct_map[self.pos], Snapper) or not isinstance(struct_map[prev_pos], Snapper):
            return False, Message.ONE_CANT_SNAP

        if self.snaps_to[-snap_direction] != struct_map[prev_pos].snapsto[snap_direction]:
            return False, Message.BAD_MATCH

        if -snap_direction in self.neighbours:
            return False, Message.ALREADY_SNAPPED

        return True, Message.SNAPPED

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


class Gate(Wall, Road):
    surf_aspect_ratio = (1, 20 / 15)
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

        for tested_direction in Direction:
            neighbour_pos = self.pos + tested_direction.to_vector()
            if struct_map.contains(neighbour_pos) and isinstance(struct_map[neighbour_pos], Snapper) and \
                    -tested_direction in struct_map[neighbour_pos].neighbours:
                if self.snaps_to[tested_direction] != struct_map[neighbour_pos].snaps_to[-tested_direction]:
                    self.directions_to_connect_to.clear()
                    return False
                self.directions_to_connect_to.add(tested_direction)
        return True

    def rotate(self) -> None:
        if self.orientation == Orientation.VERTICAL:
            self.orientation = Orientation.HORIZONTAL
            self.snaps_to = {Direction.N: Wall, Direction.E: Road, Direction.S: Wall, Direction.W: Road}
        elif self.orientation == Orientation.HORIZONTAL:
            self.orientation = Orientation.VERTICAL
            self.snaps_to = {Direction.N: Road, Direction.E: Wall, Direction.S: Road, Direction.W: Wall}

        self.image: pg.Surface = self.manager.spritesheet.get_image(self)


class MapManager:
    def __init__(self, sizes: Sizes):
        self.layout: pg.Surface = Config.get_layout()
        self.struct_map: Map = Map(sizes.map_tiles)
        self.tile_map: Map = Map(sizes.map_tiles)
        self.enclosed_tiles: Map = Map(sizes.map_tiles)

    def load_terrain(self) -> None:
        color_to_terrain = {(181, 199, 75, 255): Terrain.GRASSLAND,
                            (41, 153, 188, 255): Terrain.WATER,
                            (250, 213, 100, 255): Terrain.DESERT}

        for x in range(self.tile_map.size.x):
            for y in range(self.tile_map.size.y):
                tile_color = self.layout.get_at((x, y))
                self.tile_map[(x, y)] = Tile(color_to_terrain[tuple(tile_color)])


class StructManager:
    def __init__(self, sizes: Sizes, map_manager: MapManager, spritesheet: Spritesheet, treasury: Treasury):
        Structure.manager = self
        Config.get_structures_config()

        self.map_manager: MapManager = map_manager
        self.sizes: Sizes = sizes
        self.spritesheet: Spritesheet = spritesheet
        self.treasury: Treasury = treasury

        self.structs: pg.sprite.Group = pg.sprite.Group()


class Sizes:
    def __init__(self, config):
        self.tile: int = config.tile_size

        self.map_tiles: Vector = Vector(*Config.get_layout().get_size())
        self.map_pixels: Vector = self.map_tiles * self.tile


class Config:

    def __init__(self):
        self.tile_size: int = 60
        self.tick_rate: int = 60

    @staticmethod
    def get_structures_config():
        with open("config/structures_config.json", "r") as f:
            for name, params in json.load(f).items():
                setattr(globals()[name], "cost",
                        {Resource[name]: amount for name, amount in params.get("cost", {}).items()})
                setattr(globals()[name], "profit",
                        {Resource[name]: amount for name, amount in params.get("profit", {}).items()})
                setattr(globals()[name], "capacity", params.get("capacity", 100))
                setattr(globals()[name], "cooldown", params.get("cooldown", 5))

    @staticmethod
    def get_starting_resources():
        with open("config/starting_resources.json", "r") as f:
            return {Resource[name]: info for name, info in json.load(f).items()}

    @staticmethod
    def get_layout():
        return pg.image.load("assets/maps/river_L.png").convert()


class Treasury:

    def __init__(self, config):
        self.resources: dict[Resource, int] = config.get_starting_resources()
