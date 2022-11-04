from typing import Union, TypeVar
from enum import IntEnum, Enum
import pygame as pg
import json
from core_classes import *

T = TypeVar('T')


class Map:
    def __init__(self, elements: Union[list[list[T]], Vector]):
        if isinstance(elements, list):
            self.elements: list[list[T]] = elements
        elif isinstance(elements, Vector):
            self.elements: list[list[T]] = [[None for _ in range(elements.y)] for _ in range(elements.x)]
        self.width: int = len(elements)
        self.height: int = len(elements[0])

    def __getitem__(self, pos: Union[Vector, tuple]):
        if isinstance(pos, Vector):
            return self.elements[pos.x][pos.y]
        elif isinstance(pos, tuple) or isinstance(pos, list):
            return self.elements[pos[0]][pos[1]]

    def __str__(self):
        return "\n".join([" ".join([str(self[x, y]) for x in range(self.width)]) for y in range(self.height)])

    def contains(self, pos: Vector) -> bool:
        return 0 <= pos.x < self.width and 0 <= pos.y < self.height


class Structure(pg.sprite.Sprite):
    def __init__(self, pos, tile_size, spritesheet, resource_manager, surf_aspect_ratio=Vector(1, 1),
                 covered_tiles=(Vector(0, 0),), orientation=Orientation.VERTICAL, unsuitable_tiles=(TileTypes.WATER,)):
        super().__init__()
        self.pos = pos
        self.surf_aspect_ratio = surf_aspect_ratio
        self.covered_tiles = covered_tiles
        self.sprite_variant = 0
        self.spritesheet = spritesheet
        self.surf = spritesheet.get_surf(self)
        self.rect = self.surf.get_rect(bottomright=((self.pos + (1, 1)) * tile_size).to_tuple())
        self.orientation = orientation
        self.unsuitable_tiles = unsuitable_tiles
        self.cost = resource_manager.structures_info[self.__class__.__name__]["cost"]
        self.profit = resource_manager.structures_info[self.__class__.__name__]["profit"]

    def __repr__(self):
        return f'{self.__class__.__name__}(pos: {self.pos})'


class House(Structure):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Mine(Structure):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, surf_aspect_ratio=Vector(1, 2), **kwargs)


class Snapper(Structure):
    def __init__(self, *args, **kwargs):
        self.neighbours = DirectionSet()
        super().__init__(*args, **kwargs)

    def add_neighbour(self, neighbour):
        self.neighbours.add(neighbour)
        self.surf = self.spritesheet.get_surf(self)

    def remove_neighbour(self, neighbour):
        self.neighbours.remove(neighbour)
        self.surf = self.spritesheet.get_surf(self)


class Wall(Snapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Spritesheet:
    def __init__(self, sizes):
        self.spritesheet = pg.image.load("assets/spritesheet.png")
        self.snapper_spritesheet = pg.image.load("assets/snapper_sheet.png")
        with open("config/spritesheet_coords.json", "r") as f:
            self.coords = json.load(f)
        self.sizes = sizes

    def get_surf(self, obj):
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
            target_rect = pg.Rect(self.coords["TileTypes"][str(obj)])
            new_surf = pg.Surface(target_rect.size)
            new_surf.blit(self.spritesheet, (0, 0), target_rect)

        new_surf.set_colorkey((255, 255, 255), pg.RLEACCEL)
        return pg.transform.scale(new_surf, (obj.surf_aspect_ratio * self.sizes.tile).to_tuple())


class MapManager:
    def __init__(self, sizes):
        self.struct_map = Map(sizes.map_tiles)
        self.tile_map = Map(sizes.map_tiles)
        self.enclosed_tiles = Map(sizes.map_tiles)


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


class ResourceManager:
    def __init__(self):
        with open("config/structures_config.json", "r") as f:
            self.structures_info = json.load(f)
