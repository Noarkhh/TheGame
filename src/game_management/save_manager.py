from __future__ import annotations

import json
from dataclasses import dataclass
from typing import TYPE_CHECKING

from src.core.cursor import Cursor
from src.entities.entities import Entities
from src.game_mechanics.struct_manager import StructManager
from src.game_mechanics.treasury import Treasury
from src.graphics.scene import Scene
from src.graphics.spritesheet import Spritesheet

if TYPE_CHECKING:
    from src.core.config import Config
    from src.game_mechanics.map_manager import MapManager


@dataclass
class SaveManager:
    config: Config
    map_manager: MapManager
    struct_manager: StructManager
    treasury: Treasury
    scene: Scene
    spritesheet: Spritesheet
    entities: Entities
    cursor: Cursor

    def save_to_savefile(self, save_id: int) -> None:
        data_dict: dict = {
            "layout_path": self.config.layout_path,
            "structures": self.struct_manager.save_to_json(),
            "treasury": self.treasury.save_to_json()
        }
        with open(f"saves/savefile{save_id}.json", "w+") as f:
            json.dump(data_dict, f, indent=2)

    def load_from_savefile(self, save_id: int) -> None:
        with open(f"saves/savefile{save_id}.json", "r") as f:
            data_dict: dict = json.load(f)
            self.cursor.unassign()
            self.entities.empty()
            self.config.layout_path = data_dict["layout_path"]
            self.map_manager.load_from_json(self.config)
            self.scene.load_from_savefile(self.config, self.spritesheet, self.map_manager)
            self.struct_manager.load_from_json(data_dict["structures"])
