from __future__ import annotations
from typing import TYPE_CHECKING
from abc import ABC, abstractmethod

if TYPE_CHECKING:
    from src.game_mechanics.treasury import Treasury
    from src.entities.structure import Structure
    from src.core.enums import Resource


class ResourceManager(ABC):
    structure: Structure
    treasury: Treasury

    profit: dict[Resource, int]
    capacity: int
    stockpile: dict[Resource, int]
    cooldown: int
    cooldown_left: int

    def __init__(self, structure: Structure, treasury: Treasury) -> None:
        self.treasury = treasury
        self.structure = structure
        self.profit = structure.base_profit.copy()
        self.capacity = structure.base_capacity
        self.cooldown = structure.base_cooldown

        self.cooldown_left = self.cooldown
        self.stockpile = {resource: 0 for resource in self.profit}

    def update_cooldown(self) -> None:
        self.cooldown_left -= 1
        if self.cooldown_left == 0:
            self.produce()
            self.cooldown_left = self.cooldown

    @abstractmethod
    def produce(self) -> None: ...
