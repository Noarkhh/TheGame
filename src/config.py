from __future__ import annotations
import json
from src.game_mechanics.structures import *
from typing import Any


class Config:
    def __init__(self) -> None:
        self.tile_size: int = 30
        self.frame_rate: int = 60
        self.window_size: Vector[int] = Vector[int](1080, 720)
        self.layout_path: str = "../assets/maps/river_L.png"
        self.structures_config_path: str = "../config/structures_config.json"
        self.starting_resources_path: str = "../config/starting_resources.json"
        self.button_specs_path: str = "../config/button_specs.json"
        self.fx_config_path: str = "../config/fx_config.json"

        Tile.size = self.tile_size

    def set_structures_parameters(self):
        with open(self.structures_config_path, "r") as f:
            for name, params in json.load(f).items():
                setattr(globals()[name], "base_cost",
                        {Resource[name]: amount for name, amount in params.get("cost", {}).items()})
                setattr(globals()[name], "base_profit",
                        {Resource[name]: amount for name, amount in params.get("profit", {}).items()})
                setattr(globals()[name], "base_capacity", params.get("capacity", 100))
                setattr(globals()[name], "base_cooldown", params.get("cooldown", 5))

    def get_starting_resources(self) -> dict[Resource, int]:
        with open(self.starting_resources_path, "r") as f:
            return {Resource[name]: info for name, info in json.load(f).items()}

    def get_layout(self) -> pg.Surface:
        return pg.image.load(self.layout_path).convert()

    def get_button_specs(self) -> dict[str, dict[str, dict[str, Any]]]:
        with open(self.button_specs_path, "r") as f:
            return json.load(f)

    def get_fx_config(self) -> dict[str, dict[str, int]]:
        with open(self.fx_config_path, "r") as f:
            return json.load(f)
