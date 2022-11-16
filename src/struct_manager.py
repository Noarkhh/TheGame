from __future__ import annotations
import pygame as pg
from src.core_classes import *
from src.structures import Structure

if TYPE_CHECKING:
    from src.config import Config
    from src.map import MapManager
    from src.spritesheet import Spritesheet
    from src.treasury import Treasury


class StructManager:
    def __init__(self, config: Config, map_manager: MapManager, spritesheet: Spritesheet, treasury: Treasury):
        Structure.manager = self
        config.set_structures_parameters()

        self.map_manager: MapManager = map_manager
        self.spritesheet: Spritesheet = spritesheet
        self.treasury: Treasury = treasury

        self.structs: pg.sprite.Group = pg.sprite.Group()
