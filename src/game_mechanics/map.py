from __future__ import annotations
import pygame as pg
from src.core_classes import *
if TYPE_CHECKING:
    from src.config import Config
    from src.game_mechanics.structures import Structure
    from src.graphics.spritesheet import Spritesheet

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
        else:
            raise TypeError

    def __str__(self) -> str:
        return "\n".join([" ".join([str(self[x, y]) for x in range(self.size.x)]) for y in range(self.size.y)])

    def contains(self, pos: Vector[int] | tuple[int, int]) -> bool:
        if isinstance(pos, Vector):
            return 0 <= pos.x < self.size.x and 0 <= pos.y < self.size.y
        elif isinstance(pos, tuple):
            return 0 <= pos[0] < self.size.x and 0 <= pos[1] < self.size.y
        else:
            raise TypeError


class MapManager:
    def __init__(self, config: Config) -> None:
        self.layout: pg.Surface = config.get_layout()
        self.map_size_tiles: Vector[int] = Vector[int](*self.layout.get_size())
        self.map_size_px: Vector[int] = self.map_size_tiles * Tile.size

        self.struct_map: Map[Structure] = Map(self.map_size_tiles)
        self.tile_map: Map[Tile] = Map(self.map_size_tiles)
        self.enclosed_tiles: Map[bool] = Map(self.map_size_tiles)

    def load_terrain(self, spritesheet: Spritesheet) -> pg.Surface:
        color_to_terrain: dict[tuple[int, ...], Terrain] = {(181, 199, 75, 255): Terrain.GRASSLAND,
                                                            (41, 153, 188, 255): Terrain.WATER,
                                                            (250, 213, 100, 255): Terrain.DESERT}
        scene_image: pg.Surface = pg.Surface(self.map_size_px.to_tuple())

        for x in range(self.tile_map.size.x):
            for y in range(self.tile_map.size.y):
                terrain = color_to_terrain[tuple(self.layout.get_at((x, y)))]
                self.tile_map[(x, y)] = Tile(terrain)
                scene_image.blit(spritesheet.get_image(terrain), (x * Tile.size, y * Tile.size))
        return scene_image
