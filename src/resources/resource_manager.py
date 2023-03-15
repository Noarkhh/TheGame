from __future__ import annotations
from typing import TYPE_CHECKING
from src.core.enums import Resource

if TYPE_CHECKING:
    from src.game_mechanics.treasury import Treasury
    from src.entities.structure import Structure


class ResourceManager:
    structure: Structure
    treasury: Treasury

    cost: dict[Resource, int]
    instant_profit: dict[Resource, int]
    profit: dict[Resource, int]
    capacity: int
    stockpile: dict[Resource, int]
    cooldown: int
    cooldown_left: int

    def __init__(self, structure: Structure, treasury: Treasury) -> None:
        self.treasury = treasury
        self.structure = structure

        self.workers = structure.base_workers
        self.cost = structure.base_cost.copy()
        self.profit = structure.base_profit.copy()
        self.upkeep = structure.base_upkeep.copy()
        self.capacity = structure.base_capacity
        self.cooldown = structure.base_cooldown

        self.cooldown_left = self.cooldown
        self.stockpile = {resource: 0 for resource in self.profit}

        self.treasury.add({Resource.WORKERS: self.workers})

    def update_cooldown(self) -> None:
        self.cooldown_left -= 1
        if self.cooldown_left == 0:
            self.produce()
            self.cooldown_left = self.cooldown

    def produce(self) -> None:
        if not self.treasury.can_afford(self.upkeep):
            return
        self.treasury.subtract(self.upkeep)
        if sum(self.stockpile.values()) < self.capacity:
            for resource, amount in self.profit.items():
                real_efficiency = max(0.0, min(1.0, self.structure.efficiency))
                # self.stockpile[resource] += int(amount * real_efficiency)
                self.treasury.add({resource: round(amount * real_efficiency)})

    def refund(self) -> None:
        self.treasury.subtract({Resource.WORKERS: self.workers})

