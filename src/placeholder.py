from __future__ import annotations
import pygame as pg
import json
from src.core_classes import *
from src.structures import Structure, Snapper

U = TypeVar('U')


class Map(Generic[U]):
    def __init__(self, size: Vector[int]) -> None:
        self.elements: list[list[Optional[U]]] = [[None for _ in range(size.y)] for _ in range(size.x)]
        self.size: Vector[int] = size

    def __getitem__(self, pos: Vector[int] | tuple[int, int]) -> Optional[U]:
        if not self.contains(pos):
            return None
        if isinstance(pos, Vector):
            return self.elements[pos.x][pos.y]
        elif isinstance(pos, tuple):
            return self.elements[pos[0]][pos[1]]
        else:
            raise TypeError

    def __setitem__(self, pos: Vector[int] | tuple[int, int], element: U) -> None:
        if not self.contains(pos):
            return None
        if isinstance(pos, Vector):
            self.elements[pos.x][pos.y] = element
        elif isinstance(pos, tuple):
            self.elements[pos[0]][pos[1]] = element

    def __str__(self) -> str:
        return "\n".join([" ".join([str(self[x, y]) for x in range(self.size.x)]) for y in range(self.size.y)])

    def contains(self, pos: Vector[int] | tuple[int, int]) -> bool:
        if isinstance(pos, Vector):
            return 0 <= pos.x < self.size.x and 0 <= pos.y < self.size.y
        elif isinstance(pos, tuple):
            return 0 <= pos[0] < self.size.x and 0 <= pos[1] < self.size.y
        else:
            raise TypeError


class Spritesheet:
    def __init__(self, sizes) -> None:
        self.sheet: pg.Surface = pg.image.load("../assets/spritesheet.png")
        self.snapper_sheet: pg.Surface = pg.image.load("../assets/snapper_sheet.png")
        with open("../config/spritesheet_coords.json", "r") as f:
            self.coords = json.load(f)
        self.sizes: Sizes = sizes

    def get_image(self, obj: Structure | Terrain) -> pg.Surface:
        if isinstance(obj, Snapper):
            target_rect = pg.Rect(
                [obj.neighbours.get_id() * 15] + self.coords["Snappers"][obj.__class__.__name__][obj.sprite_variant])
            sheet = self.snapper_sheet
            aspect_ratio = obj.image_aspect_ratio
        elif isinstance(obj, Structure):
            target_rect = pg.Rect(self.coords["Structures"][obj.__class__.__name__][obj.sprite_variant])
            sheet = self.sheet
            aspect_ratio = obj.image_aspect_ratio
        elif isinstance(obj, Terrain):
            target_rect = pg.Rect(self.coords["TileTypes"][obj.name])
            sheet = self.sheet
            aspect_ratio = Vector[float](1, 1)
        else:
            raise TypeError

        new_surf = pg.Surface(target_rect.size)
        new_surf.blit(sheet, (0, 0), target_rect)
        new_surf = pg.transform.scale(new_surf, (aspect_ratio * self.sizes.tile).to_tuple())

        new_surf.set_colorkey((255, 255, 255), pg.RLEACCEL)
        return new_surf


class MapManager:
    def __init__(self, sizes: Sizes) -> None:
        self.layout: pg.Surface = Config.get_layout()
        self.struct_map: Map[Structure] = Map(sizes.map_tiles)
        self.tile_map: Map[Tile] = Map(sizes.map_tiles)
        self.enclosed_tiles: Map[bool] = Map(sizes.map_tiles)

    def load_terrain(self) -> None:
        color_to_terrain: dict[tuple[int, ...], Terrain] = {(181, 199, 75, 255): Terrain.GRASSLAND,
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
    def __init__(self, config: Config) -> None:
        self.tile: int = config.tile_size

        self.map_tiles: Vector[int] = Vector[int](*Config.get_layout().get_size())
        self.map_pixels: Vector[int] = self.map_tiles * self.tile


class Config:

    def __init__(self) -> None:
        self.tile_size: int = 60
        self.tick_rate: int = 60
        self.window_size: Vector[int] = Vector[int](1080, 720)

    @staticmethod
    def get_structures_config():
        with open("../config/structures_config.json", "r") as f:
            for name, params in json.load(f).items():
                setattr(globals()[name], "base_cost",
                        {Resource[name]: amount for name, amount in params.get("cost", {}).items()})
                setattr(globals()[name], "base_profit",
                        {Resource[name]: amount for name, amount in params.get("profit", {}).items()})
                setattr(globals()[name], "base_capacity", params.get("capacity", 100))
                setattr(globals()[name], "base_cooldown", params.get("cooldown", 5))

    @staticmethod
    def get_starting_resources() -> dict[Resource, int]:
        with open("../config/starting_resources.json", "r") as f:
            return {Resource[name]: info for name, info in json.load(f).items()}

    @staticmethod
    def get_layout() -> pg.Surface:
        return pg.image.load("../assets/maps/river_L.png").convert()


class Treasury:
    def __init__(self, config: Config) -> None:
        self.resources: dict[Resource, int] = config.get_starting_resources()
