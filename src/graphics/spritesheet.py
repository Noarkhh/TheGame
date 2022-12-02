from __future__ import annotations
import pygame as pg
from typing import Any, Type
from src.game_mechanics.structures import Structure, Snapper
from src.core_classes import *
if TYPE_CHECKING:
    from src.graphics.entities import Entity
    from src.config import Config


class Spritesheet:
    def __init__(self, config: Config) -> None:
        self.sheet: pg.Surface = pg.image.load("../assets/spritesheet.png")
        self.ui_sheet: pg.Surface = pg.image.load("../assets/ui_sheet.png")
        self.snapper_sheet: pg.Surface = pg.image.load("../assets/snapper_sheet.png")
        self.coords: dict[str, dict[str, Any]] = config.get_spritesheet_coords()

    def get_image(self, obj: Entity | Type[Entity] | Terrain, scale: Optional[int] = None) -> pg.Surface:
        if isinstance(obj, Snapper):
            target_rect = pg.Rect(
                [obj.neighbours.get_id() * 15] + self.coords["Snappers"][obj.__class__.__name__][obj.image_variant])
            sheet = self.snapper_sheet
            aspect_ratio = obj.image_aspect_ratio
        elif isinstance(obj, Structure):
            target_rect = pg.Rect(self.coords["Structures"][obj.__class__.__name__][obj.image_variant])
            sheet = self.sheet
            aspect_ratio = obj.image_aspect_ratio
        elif isinstance(obj, Terrain):
            target_rect = pg.Rect(self.coords["Terrain"][obj.name])
            sheet = self.sheet
            aspect_ratio = Vector[float](1, 1)
        elif isinstance(obj, type):
            if issubclass(obj, Snapper):
                target_rect = pg.Rect([150] + self.coords["Snappers"][obj.__name__][0])
                sheet = self.snapper_sheet
                aspect_ratio = obj.image_aspect_ratio
            elif issubclass(obj, Structure):
                target_rect = pg.Rect(self.coords["Structures"][obj.__name__][0])
                sheet = self.sheet
                aspect_ratio = obj.image_aspect_ratio
            else:
                raise TypeError
        else:
            raise TypeError

        new_surf = pg.Surface(target_rect.size)
        new_surf.blit(sheet, (0, 0), target_rect)
        new_surf = pg.transform.scale(new_surf, (aspect_ratio * (Tile.size if scale is None else scale)).to_tuple())

        new_surf.set_colorkey("white", pg.RLEACCEL)
        return new_surf

    def get_ui_image(self, category: str, name: str, scale: int = 4) -> pg.Surface:
        target_rect = pg.Rect(self.coords["UI"][category][name])
        new_surf = pg.Surface(target_rect.size)
        new_surf.blit(self.ui_sheet, (0, 0), target_rect)
        new_surf = pg.transform.scale(new_surf, (new_surf.get_width() * scale, new_surf.get_height() * scale))
        new_surf.set_colorkey("white", pg.RLEACCEL)
        return new_surf

