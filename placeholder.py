from typing import TypeVar
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


class Message(Enum):
    BAD_LOCATION_TILE = 0
    BAD_LOCATION_STRUCT = 1
    NO_RESOURCES = 2

    BAD_DIFF = 3
    ONE_CANT_SNAP = 4
    BAD_MATCH = 5
    ALREADY_SNAPPED = 6

    CANT_OVERRIDE = 7

    BUILT = 8
    SNAPPED = 9
    OVERRODE = 10


class Structure(pg.sprite.Sprite):
    def __init__(self, pos, tile_size, spritesheet, resource_manager, surf_aspect_ratio=(1, 1),
                 covered_tiles=(Vector(0, 0),), orientation=Orientation.VERTICAL, unsuitable_tiles=(TileTypes.WATER,),
                 sprite_variant=0, can_override=False):
        super().__init__()
        self.pos = pos
        self.surf_aspect_ratio = surf_aspect_ratio
        self.covered_tiles = covered_tiles
        self.sprite_variant = sprite_variant
        self.spritesheet = spritesheet
        self.orientation = orientation
        self.unsuitable_tiles = unsuitable_tiles
        self.can_override = can_override

        self.surf = spritesheet.get_surf(self)
        self.rect = self.surf.get_rect(bottomright=((self.pos + (1, 1)) * tile_size).to_tuple())

        self.cost = resource_manager.structures_info[self.__class__.__name__]["cost"]
        self.profit = resource_manager.structures_info[self.__class__.__name__]["profit"]

    def __repr__(self):
        return f'{self.__class__.__name__}(pos: {self.pos})'

    def can_be_placed(self, pos, map_manager, resource_manager):

        if any(map_manager.tile_map[pos + rel_pos] in self.unsuitable_tiles for rel_pos in self.covered_tiles):
            return False, Message.BAD_LOCATION_TILE

        if any(isinstance(map_manager.struct_map[pos + rel_pos], Structure) for rel_pos in self.covered_tiles):
            return False, Message.BAD_LOCATION_STRUCT

        if any(amount > resource_manager.resources[resource] for resource, amount in self.cost.items()):
            return False, Message.NO_RESOURCES

        return True, Message.BUILT


class House(Structure):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, surf_aspect_ratio=(1, 21 / 15), **kwargs)


class Mine(Structure):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, surf_aspect_ratio=(1, 2), **kwargs)


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


class Road(Snapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Gate(Wall, Road):
    def __init__(self, *args, orientation, **kwargs):
        super().__init__(*args, orientation, surf_aspect_ratio=(1, 20/15), can_override=True, **kwargs)
        if self.orientation == Orientation.VERTICAL:
            self.snapsto = {Direction.N: Road, Direction.E: Wall, Direction.S: Road, Direction.W: Wall}
        elif self.orientation == Orientation.HORIZONTAL:
            self.snapsto = {Direction.N: Wall, Direction.E: Road, Direction.S: Wall, Direction.W: Road}


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
        return pg.transform.scale(new_surf, (obj.surf_aspect_ratio[0] * self.sizes.tile,
                                             obj.surf_aspect_ratio[1] * self.sizes.tile))


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
