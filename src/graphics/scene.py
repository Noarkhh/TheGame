from __future__ import annotations
import pygame as pg
from src.core_classes import *

if TYPE_CHECKING:
    from src.config import Config
    from src.game_mechanics.map import MapManager
    from src.graphics.spritesheet import Spritesheet
    from src.cursor import Cursor


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

        self.velocity: Vector[float] = Vector[float](0, 0)
        self.velocity_decrement: Vector[float] = Vector[float](0, 0)
        self.to_decrement: int = 0
        self.retardation_period: int = 20

    def update_velocity(self, new_velocity: Optional[Vector[float]] = None, slow_down: bool = False):
        if slow_down and self.velocity != Vector[float](0.0, 0.0):
            velocity_sign_before = self.velocity.x > 0 - self.velocity.x < 0
            self.velocity -= self.velocity_decrement
            velocity_sign_after = self.velocity.x > 0 - self.velocity.x < 0
            if velocity_sign_before != velocity_sign_after:
                self.velocity = Vector[float](0.0, 0.0)
        if new_velocity is not None:
            self.velocity = new_velocity

    def set_decrement(self):
        self.velocity_decrement = self.velocity / self.retardation_period

    def update(self):
        self.move_by_velocity()
        self.move_screen_border(Vector(pg.mouse.get_pos()))
        self.update_velocity(slow_down=True)

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

    def move_by_velocity(self):
        new_rect = self.rect.move(*self.velocity.to_tuple())

        if new_rect.left >= 0 and new_rect.right <= self.map_size_px.x:
            self.rect.move_ip(self.velocity.x, 0)
        elif new_rect.left < 0:
            self.rect.left = 0
        elif new_rect.right > self.map_size_px.x:
            self.rect.right = self.map_size_px.x

        if new_rect.top >= 0 and new_rect.bottom < self.map_size_px.y:
            self.rect.move_ip(0, self.velocity.y)
        elif new_rect.top < 0:
            self.rect.top = 0
        elif new_rect.bottom > self.map_size_px.y:
            self.rect.bottom = self.map_size_px.y

        self.image = self.map_image.subsurface(self.rect)

    def reset_image(self) -> None:
        self.image.blit(self.map_image_raw.subsurface(self.rect), (0, 0))