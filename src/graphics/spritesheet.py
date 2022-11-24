from __future__ import annotations
import pygame as pg
import json
from src.game_mechanics.structures import Structure, Snapper
from src.core_classes import *
if TYPE_CHECKING:
    from src.graphics.entities import Entity


class Spritesheet:
    def __init__(self) -> None:
        self.sheet: pg.Surface = pg.image.load("../assets/spritesheet.png")
        self.snapper_sheet: pg.Surface = pg.image.load("../assets/snapper_sheet.png")
        with open("../config/spritesheet_coords.json", "r") as f:
            self.coords = json.load(f)

    def get_image(self, obj: Entity | Terrain) -> pg.Surface:
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
        else:
            raise TypeError

        new_surf = pg.Surface(target_rect.size)
        new_surf.blit(sheet, (0, 0), target_rect)
        new_surf = pg.transform.scale(new_surf, (aspect_ratio * Tile.size).to_tuple())

        new_surf.set_colorkey("white", pg.RLEACCEL)
        return new_surf