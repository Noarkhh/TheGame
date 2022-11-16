from __future__ import annotations
import pygame as pg
from src.core_classes import *

if TYPE_CHECKING:
    from src.config import Config
    from src.map import MapManager
    from src.spritesheet import Spritesheet


class Scene(pg.sprite.Sprite):
    def __init__(self, config: Config, spritesheet: Spritesheet, map_manager: MapManager) -> None:
        super().__init__()
        self.map_image: pg.Surface = map_manager.load_terrain(spritesheet)
        self.map_image_raw: pg.Surface = self.map_image.copy()
        self.rect: pg.Rect = pg.Rect(((self.map_image.get_width() - config.window_size.x) // 2,
                                      (self.map_image.get_height() - config.window_size.y) // 2,
                                      config.window_size.x, config.window_size.y))
        self.image: pg.Surface = self.map_image.subsurface(self.rect)
        self.window_size: Vector[int] = config.window_size
        self.map_size_px: Vector[int] = map_manager.map_size_px

        self.move_velocity: Vector[float] = Vector[float](0, 0)
        self.move_velocity_decrement: Vector[float] = Vector[float](0, 0)
        self.to_decrement: int = 0
        self.retardation_period: int = 30

    def move_screen_border(self, curr_mouse_pos: Vector[int]):
        if curr_mouse_pos.x >= self.window_size.x - Tile.size / 2 and \
                self.rect.right <= self.map_size_px.x - Tile.size / 2:
            self.rect.move_ip(Tile.size / 2, 0)
        if curr_mouse_pos.x <= 0 + Tile.size / 2 <= self.rect.left:
            self.rect.move_ip(-Tile.size / 2, 0)

        if curr_mouse_pos.y >= self.window_size.y - Tile.size / 2 and \
                self.rect.bottom <= self.map_size_px.y - Tile.size / 2:
            self.rect.move_ip(0, Tile.size / 2)
        if curr_mouse_pos.y <= 0 + Tile.size / 2 <= self.rect.top:
            self.rect.move_ip(0, -Tile.size / 2)

        self.image = self.map_image.subsurface(self.rect)

    def move_screen_drag(self, curr_mouse_pos: Vector[int], previous_mouse_pos: Vector[int]):
        self.move_velocity = (previous_mouse_pos - curr_mouse_pos).to_float()
        new_rect = self.rect.move(*self.move_velocity.to_tuple())

        if new_rect.left >= 0 and new_rect.right <= self.map_size_px.x:
            self.rect.move_ip(self.move_velocity.x, 0)
        elif new_rect.left < 0:
            self.rect.left = 0
        elif new_rect.right > self.map_size_px.x:
            self.rect.right = self.map_size_px.x

        if new_rect.top >= 0 and new_rect.bottom < self.map_size_px.y:
            self.rect.move_ip(0, self.move_velocity.y)
        elif new_rect.top < 0:
            self.rect.top = 0
        elif new_rect.bottom > self.map_size_px.y:
            self.rect.bottom = self.map_size_px.y

        self.image = self.map_image.subsurface(self.rect)
