from __future__ import annotations
from typing import TypeVar
import pygame as pg
import json
from core_classes import *

T = TypeVar('T')


class Map:
    def __init__(self, size: Vector):
        self.elements: list[list[T]] = [[None for _ in range(size.y)] for _ in range(size.x)]
        self.size = size

    def __getitem__(self, pos: Vector | tuple):
        if isinstance(pos, Vector):
            return self.elements[pos.x][pos.y]
        elif isinstance(pos, tuple):
            return self.elements[pos[0]][pos[1]]

    def __setitem__(self, pos: Vector | tuple, element: T):
        if isinstance(pos, Vector):
            self.elements[pos.x][pos.y] = element
        elif isinstance(pos, tuple):
            self.elements[pos[0]][pos[1]] = element

    def __str__(self):
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
    def __init__(self, sizes):
        self.spritesheet = pg.image.load("assets/spritesheet.png")
        self.snapper_spritesheet = pg.image.load("assets/snapper_sheet.png")
        with open("config/spritesheet_coords.json", "r") as f:
            self.coords = json.load(f)
        self.sizes = sizes

        Structure.spritesheet = self

    def get_image(self, obj: Structure | Terrain):
        if isinstance(obj, Snapper):
            target_rect = pg.Rect(
                [obj.neighbours.get_id() * 15] + self.coords["Snappers"][obj.__class__.__name__][obj.sprite_variant])
            new_surf = pg.Surface(target_rect.size)
            new_surf.blit(self.snapper_spritesheet, (0, 0), target_rect)
        elif isinstance(obj, Structure):
            target_rect = pg.Rect(self.coords["Structures"][obj.__class__.__name__][obj.sprite_variant])
            new_surf = pg.Surface(target_rect.size)
            new_surf.blit(self.spritesheet, (0, 0), target_rect)
        elif isinstance(obj, Terrain):
            target_rect = pg.Rect(self.coords["TileTypes"][obj.name])
            new_surf = pg.Surface(target_rect.size)
            new_surf.blit(self.spritesheet, (0, 0), target_rect)
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

    cost: dict[Resources, int]
    profit: dict[Resources, int]
    capacity: int
    cooldown: int

    manager: StructManager

    def __init__(self, pos: Vector, sprite_variant: int = 0, orientation: Orientation = Orientation.VERTICAL):
        super().__init__()
        self.manager.structs.add(self)
        self.pos: Vector = pos

        self.sprite_variant: int = sprite_variant
        self.orientation: Orientation = orientation

        self.image: pg.Surface = self.manager.spritesheet.get_image(self)
        self.rect: pg.Rect = self.image.get_rect(bottomright=((self.pos + (1, 1)) * self.manager.sizes.tile).to_tuple())

        self.cost = self.__class__.cost.copy()
        self.profit = self.__class__.profit.copy()
        self.capacity = self.__class__.capacity
        self.cooldown = self.__class__.cooldown

        self.cooldown_left = self.cooldown
        self.stockpile = {resource: 0 for resource in self.profit.keys()}

    def __repr__(self):
        return f'{self.__class__.__name__}(pos: {self.pos})'

    def can_be_placed(self, map_manager: MapManager) -> tuple[bool, Message]:

        if any(map_manager.terrain_map[self.pos + rel_pos] in self.unsuitable_terrain for rel_pos in self.covered_tiles):
            return False, Message.BAD_LOCATION_TERRAIN

        if any(isinstance(map_manager.struct_map[self.pos + rel_pos], Structure) for rel_pos in self.covered_tiles):
            return False, Message.BAD_LOCATION_STRUCT

        if any(amount > self.manager.treasury.resources[resource] for resource, amount in self.cost.items()):
            return False, Message.NO_RESOURCES

        return True, Message.BUILT

    def produce(self):
        self.cooldown_left -= 1
        if self.cooldown_left == 0:
            if sum(self.stockpile.values()) < self.capacity:
                for resource, amount in self.profit.items():
                    self.stockpile[resource] += amount
            self.cooldown_left = self.cooldown


class House(Structure):
    surf_aspect_ratio = (1, 21 / 15)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Mine(Structure):
    surf_aspect_ratio = (1, 2)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Sawmill(Structure):
    surf_aspect_ratio = (2, 1)
    covered_tiles = (Vector(0, 0), Vector(-1, 0))

    def __init__(self, *args, **kwargs):
        super(Sawmill, self).__init__(*args, **kwargs)


class Snapper(Structure):
    def __init__(self, *args, **kwargs):
        self.neighbours: DirectionSet = DirectionSet()
        super().__init__(*args, **kwargs)

    def add_neighbours(self, neighbours: DirectionSet | set) -> None:
        self.neighbours.update(neighbours)
        self.image = self.manager.spritesheet.get_image(self)

    def remove_neighbours(self, neighbours: DirectionSet | set) -> None:
        self.neighbours.difference_update(neighbours)
        self.image = self.manager.spritesheet.get_image(self)


class Wall(Snapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Road(Snapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Gate(Wall, Road):
    surf_aspect_ratio = (1, 20 / 15)
    overrider = True

    def __init__(self, *args, orientation: Orientation = Orientation.VERTICAL, **kwargs):
        super().__init__(*args, orientation, **kwargs)
        self.directions_to_connect_to: DirectionSet = DirectionSet()

        if self.orientation == Orientation.VERTICAL:
            self.snapsto = {Directions.N: Road, Directions.E: Wall, Directions.S: Road, Directions.W: Wall}
        elif self.orientation == Orientation.HORIZONTAL:
            self.snapsto = {Directions.N: Wall, Directions.E: Road, Directions.S: Wall, Directions.W: Road}

    def can_override(self) -> bool:
        struct_map = self.manager.map_manager.struct_map
        if not type(struct_map[self.pos]) in (Wall, Road):
            return False

        for tested_direction in Directions:
            neighbour_pos = self.pos + tested_direction.to_vector()
            if struct_map.contains(neighbour_pos) and isinstance(struct_map[neighbour_pos], Snapper) and \
                    -tested_direction in struct_map[neighbour_pos].neighbours:
                if self.snapsto[tested_direction] != struct_map[neighbour_pos].snaps_to[-tested_direction]:
                    self.directions_to_connect_to.clear()
                    return False
                self.directions_to_connect_to.add(tested_direction)
        return True


class MapManager:
    def __init__(self, sizes: Sizes):
        self.layout = Config.get_layout()
        self.struct_map = Map(sizes.map_tiles)
        self.terrain_map = Map(sizes.map_tiles)
        self.enclosed_tiles = Map(sizes.map_tiles)

    def load_terrain(self):
        color_to_terrain = {(181, 199, 75, 255): Terrain.GRASSLAND,
                            (41, 153, 188, 255): Terrain.WATER,
                            (250, 213, 100, 255): Terrain.DESERT}

        for x in range(self.terrain_map.size.x):
            for y in range(self.terrain_map.size.y):
                tile_color = self.layout.get_at((x, y))
                self.terrain_map[(x, y)] = color_to_terrain[tuple(tile_color)]


class StructManager:
    def __init__(self, sizes: Sizes, map_manager: MapManager, spritesheet: Spritesheet, treasury: Treasury):
        Structure.manager = self

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
                        {Resources[name]: amount for name, amount in params.get("cost", {}).items()})
                setattr(globals()[name], "profit",
                        {Resources[name]: amount for name, amount in params.get("profit", {}).items()})
                setattr(globals()[name], "capacity", params.get("capacity", 100))
                setattr(globals()[name], "cooldown", params.get("cooldown", 5))

    @staticmethod
    def get_starting_resources():
        with open("config/starting_resources.json", "r") as f:
            return {Resources[name]: info for name, info in json.load(f).items()}

    @staticmethod
    def get_layout():
        return pg.image.load("assets/maps/river_L.png").convert()


class Treasury:

    def __init__(self, config):
        self.resources = config.get_starting_resources()