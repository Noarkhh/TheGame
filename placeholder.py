from __future__ import annotations
from typing import TypeVar
import pygame as pg
import json
from core_classes import *

T = TypeVar('T')


class Map:
    def __init__(self, size: Vector):
        self.elements: list[list[T]] = [[None for _ in range(size.y)] for _ in range(size.x)]
        self.width: int = size.x
        self.height: int = size.y

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
        return "\n".join([" ".join([str(self[x, y]) for x in range(self.width)]) for y in range(self.height)])

    def contains(self, pos: Vector) -> bool:
        return 0 <= pos.x < self.width and 0 <= pos.y < self.height


class Message(Enum):
    BAD_LOCATION_TILE = 0
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

    def get_image(self, obj: Structure | TileTypes):
        if isinstance(obj, Snapper):
            target_rect = pg.Rect(
                [obj.neighbours.get_id() * 15] + self.coords["Snappers"][obj.__class__.__name__][obj.sprite_variant])
            new_surf = pg.Surface(target_rect.size)
            new_surf.blit(self.snapper_spritesheet, (0, 0), target_rect)
        elif isinstance(obj, Structure):
            target_rect = pg.Rect(self.coords["Structures"][obj.__class__.__name__][obj.sprite_variant])
            new_surf = pg.Surface(target_rect.size)
            new_surf.blit(self.spritesheet, (0, 0), target_rect)
        elif isinstance(obj, TileTypes):
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
    unsuitable_tiles: tuple[TileTypes, ...] = (TileTypes.WATER,)
    overrider: bool = False

    cost: dict[Resources] = {}
    profit: dict[Resources] = {}
    capacity: int = 100
    cooldown: int = 5

    def __init__(self, pos: Vector, tile_size: int, spritesheet: Spritesheet, treasury: Treasury,
                 sprite_variant: int = 0, orientation: Orientation = Orientation.VERTICAL):
        super().__init__()
        self.pos: Vector = pos
        self.spritesheet: Spritesheet = spritesheet

        self.sprite_variant: int = sprite_variant
        self.orientation: Orientation = orientation

        self.image: pg.Surface = spritesheet.get_image(self)
        self.rect: pg.Rect = self.image.get_rect(bottomright=((self.pos + (1, 1)) * tile_size).to_tuple())

        self.cost = self.__class__.cost.copy()
        self.profit = self.__class__.profit.copy()
        self.capacity = self.__class__.capacity
        self.cooldown = self.__class__.cooldown

        self.cooldown_left = self.cooldown
        self.stockpile = {resource: 0 for resource in self.profit.keys()}

    def __repr__(self):
        return f'{self.__class__.__name__}(pos: {self.pos})'

    def can_be_placed(self, map_manager: MapManager, treasury: Treasury) -> tuple[bool, Message]:

        if any(map_manager.tile_map[self.pos + rel_pos] in self.unsuitable_tiles for rel_pos in self.covered_tiles):
            return False, Message.BAD_LOCATION_TILE

        if any(isinstance(map_manager.struct_map[self.pos + rel_pos], Structure) for rel_pos in self.covered_tiles):
            return False, Message.BAD_LOCATION_STRUCT

        if any(amount > treasury.resources[resource] for resource, amount in self.cost.items()):
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
        self.image = self.spritesheet.get_image(self)

    def remove_neighbours(self, neighbours: DirectionSet | set) -> None:
        self.neighbours.difference_update(neighbours)
        self.image = self.spritesheet.get_image(self)


class Wall(Snapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Road(Snapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Gate(Wall, Road):
    surf_aspect_ratio = (1, 20 / 15)
    overrider = True

    def __init__(self, *args, orientation: Orientation, **kwargs):
        super().__init__(*args, orientation, **kwargs)
        self.directions_to_connect_to: DirectionSet = DirectionSet()

        if self.orientation == Orientation.VERTICAL:
            self.snapsto = {Directions.N: Road, Directions.E: Wall, Directions.S: Road, Directions.W: Wall}
        elif self.orientation == Orientation.HORIZONTAL:
            self.snapsto = {Directions.N: Wall, Directions.E: Road, Directions.S: Wall, Directions.W: Road}

    def can_override(self, struct_map: Map) -> bool:
        if not type(struct_map[self.pos]) in (Wall, Road):
            return False

        for direction in Directions:
            neighbour_pos = self.pos + direction.to_vector()
            if struct_map.contains(neighbour_pos) and isinstance(struct_map[neighbour_pos], Snapper) and \
                    direction in struct_map[neighbour_pos].neighbours:
                if self.snapsto[-direction] != struct_map[neighbour_pos].snaps_to[direction]:
                    self.directions_to_connect_to.clear()
                    return False
                self.directions_to_connect_to.add(direction)
        return True


class MapManager:
    def __init__(self, sizes: Sizes):
        self.struct_map = Map(sizes.map_tiles)
        self.tile_map = Map(sizes.map_tiles)
        self.enclosed_tiles = Map(sizes.map_tiles)


class StructManager:
    def __init__(self, sizes: Sizes, map_manager: MapManager):
        self.map_manager = map_manager
        self.sizes = sizes
        self.structs = pg.sprite.Group()


class Sizes:
    def __init__(self, config: Config):
        self.map_tiles = Vector(config.layout.get_width(), config.layout.get_height())
        self.tile = config.tile_size
        self.map_pixels = self.map_tiles * self.tile


class Config:
    @staticmethod
    def get_structures_config():
        with open("config/structures_config.json", "r") as f:
            base_structure_params = {}
            for name, params in json.load(f).items():
                base_structure_params[globals()[name]] = params
                setattr(globals()[name], "cost", {Resources[name]: amount for name, amount in params["cost"].items()})
                setattr(globals()[name], "profit", {Resources[name]: amount for name, amount in params["profit"].items()})
                setattr(globals()[name], "capacity", params.get("capacity", 100))
                setattr(globals()[name], "cooldown", params.get("cooldown", 5))
            return base_structure_params

    @staticmethod
    def get_starting_resources():
        with open("config/starting_resources.json", "r") as f:
            return {Resources[name]: info for name, info in json.load(f).items()}

    def __init__(self):
        self.layout_path = "assets/maps/river_L.png"
        self.layout = pg.image.load(self.layout_path).convert()
        self.tile_size = 60


class Treasury:
    def __init__(self):
        self.structures_params = Config.get_structures_config()
        self.resources = Config.get_starting_resources()
        self.default_cooldown = 5


class ResourceManager:
    def __init__(self, struct, treasury):
        self.treasury = treasury
        self.cost = treasury.structures_params[struct.__class__].get("cost", 0)
        self.base_profit = treasury.structures_params[struct.__class__].get("profit", 0)
        self.profit = self.base_profit
        self.base_capacity = treasury.structures_params[struct.__class__].get("capacity", 0)
        self.capacity = self.base_capacity
        self.stockpile = {resource: 0 for resource in self.profit.keys()}
        self.base_cooldown = treasury.structures_params[struct.__class__].get("cooldown", treasury.default_cooldown)
        self.cooldown = self.base_cooldown

    def __repr__(self):
        return f'{self.__class__.__name__}(cost: {self.cost}, profit: {self.profit}, ' \
               f'capacity: {self.capacity}, self.stockpile: {self.stockpile}, cooldown: {self.cooldown}'

    def produce(self):
        self.cooldown -= 1
        if self.cooldown == 0:
            if sum(self.stockpile.values() < self.capacity):
                for resource, amount in self.profit.items():
                    self.stockpile[resource] += amount
            self.cooldown = self.base_cooldown
