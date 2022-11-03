from typing import Union, TypeVar
from enum import IntEnum, Enum
import pygame as pg
import json
from gameworld import GameWorld

T = TypeVar('T')


class Vector:
    def __init__(self, x: int, y: int):
        self.x: int = x
        self.y: int = y

    def __sub__(self, other: Union[tuple[int, int], 'Vector']) -> 'Vector':
        if isinstance(other, Vector):
            return Vector(self.x - other.x, self.y - other.y)
        if isinstance(other, tuple):
            return Vector(self.x - other[0], self.y - other[1])

    def __add__(self, other: Union[tuple[int, int], 'Vector']) -> 'Vector':
        if isinstance(other, Vector):
            return Vector(self.x + other.x, self.y + other.y)
        if isinstance(other, tuple):
            return Vector(self.x + other[0], self.y + other[1])

    def __neg__(self):
        return Vector(-self.x, -self.y)

    def __mul__(self, other: Union[int, 'Vector']) -> 'Vector':
        if isinstance(other, int):
            return Vector(self.x * other, self.y * other)
        if isinstance(other, Vector):
            return Vector(self.x * other.x, self.y * other.y)

    def __eq__(self, other: 'Vector') -> 'Vector':
        return self.x == other.x and self.y == other.y

    def __str__(self) -> str:
        return f'({self.x}, {self.y})'

    def __hash__(self):
        return hash((self.__class__, self.x, self.y))

    def to_dir(self) -> 'Direction':
        return {Vector(0, -1): Direction.N,
                Vector(1, 0): Direction.E,
                Vector(0, 1): Direction.S,
                Vector(-1, 0): Direction.W}.get(self)

    def to_tuple(self) -> tuple:
        return self.x, self.y


class Map:
    def __init__(self, elements: Union[list[list[T]], Vector]):
        if isinstance(elements, list):
            self.elements: list[list[T]] = elements
        elif isinstance(elements, Vector):
            self.elements: list[list[T]] = [[None for _ in range(elements.y)] for _ in range(elements.x)]
        self.width: int = len(elements)
        self.height: int = len(elements[0])

    def __getitem__(self, pos: Vector):
        if isinstance(pos, Vector):
            return self.elements[pos.x][pos.y]
        elif isinstance(pos, tuple) or isinstance(pos, list):
            return self.elements[pos[0]][pos[1]]

    def __str__(self):
        return "\n".join([" ".join([str(self[x, y]) for x in range(self.width)]) for y in range(self.height)])

    def contains(self, pos: Vector) -> bool:
        return 0 <= pos.x < self.width and 0 <= pos.y < self.height


class Direction(IntEnum):
    N = 0
    E = 1
    S = 2
    W = 3

    def to_vector(self) -> Vector:
        return {self.N: Vector(0, -1),
                self.E: Vector(1, 0),
                self.S: Vector(0, 1),
                self.W: Vector(-1, 0)}[self]

    def __neg__(self) -> 'Direction':
        return {self.N: self.S,
                self.E: self.W,
                self.S: self.N,
                self.W: self.E}[self]


class TileType(Enum):
    GRASSLAND = 0
    DESERT = 1
    WATER = 2


class Tile:
    def __init__(self, tile_type: TileType, resource):
        self.tile_type = tile_type
        self.resource = resource


class Structure(pg.sprite.Sprite):
    def __init__(self, pos, tile_size, spritesheet, surf_aspect_ratio=Vector(1, 1)):
        super().__init__()
        self.pos = pos
        self.surf_aspect_ratio = surf_aspect_ratio
        self.sprite_variant = 0
        self.surf = spritesheet.get_surf(self)
        self.rect = self.surf.get_rect(bottomright=((self.pos + (1, 1)) * tile_size).to_tuple())
        self.surf.set_colorkey((255, 255, 255), pg.RLEACCEL)

    def __repr__(self):
        return f'{self.__class__.__name__}(pos: {self.pos})'


class House(Structure):
    def __init__(self, pos, tile_size, spritesheet):
        super().__init__(pos, tile_size, spritesheet)


class Spritesheet:
    def __init__(self, sizes):
        self.spritesheet = pg.image.load("assets/spritesheet.png")
        self.snapper_spritesheet = pg.image.load("assets/snapper_sheet.png")
        with open("assets/spritesheet_coords.json", "r") as f:
            self.coords = json.load(f)
        self.sizes = sizes

    def get_surf(self, obj):
        if isinstance(obj, Structure):
            target_rect = pg.Rect(self.coords["Structures"][obj.__class__.__name__][obj.sprite_variant])
        elif isinstance(obj, TileType):
            target_rect = pg.Rect(self.coords["TileTypes"][str(obj)])
        new_surf = pg.Surface(target_rect.size)
        new_surf.blit(self.spritesheet, (0, 0), target_rect)
        new_surf.set_colorkey((255, 255, 255), pg.RLEACCEL)
        return pg.transform.scale(new_surf, (obj.surf_aspect_ratio * self.sizes.tile).to_tuple())


class MapManager:
    def __init__(self, sizes):

        self.struct_map = Map(sizes.map_tiles)
        self.tile_map = Map(sizes.map_tiles)


class StructManager:
    def __init__(self, sizes):
        self.sizes = sizes
        self.structs = pg.sprite.Group()


class Sizes:
    def __init__(self, config):
        self.map_tiles = Vector(config.layout.get_width(), config.layout.get_height())
        self.tile = config.tile_size
        self.map_pixels = self.map_tiles * self.tile


class Config:
    def __init__(self):
        self.layout_path = "assets/maps/river_L.png"
        self.layout = pg.image.load(self.layout_path).convert()
        self.tile_size = 60
