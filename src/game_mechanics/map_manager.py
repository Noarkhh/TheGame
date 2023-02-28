from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

from src.core.enums import Tile, Terrain
from src.core.vector import Vector
from src.game_mechanics.map import Map

if TYPE_CHECKING:
    from src.core.config import Config
    from src.entities.structures import Structure
    from src.graphics.spritesheet import Spritesheet


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

    def update_zoom(self, factor: float) -> None:
        self.map_size_px = Vector(int(self.map_size_px.x * factor), int(self.map_size_px.y * factor))
