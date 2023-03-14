from __future__ import annotations

from typing import TYPE_CHECKING

from src.core.enums import Resource

if TYPE_CHECKING:
    from src.core.config import Config
    from src.entities.structures import Structure


class Treasury:
    def __init__(self, config: Config) -> None:
        self.resources: dict[Resource, int] = config.get_starting_resources()
        self.display_state_changed: bool = False

    def can_afford(self, struct: Structure) -> bool:
        return all(amount <= self.resources[resource] for resource, amount in struct.base_cost.items())

    def pay_for(self, struct: Structure) -> None:
        for resource, amount in struct.cost.items():
            self.resources[resource] -= amount
            self.display_state_changed = True

    def save_to_json(self) -> dict[str, int]:
        return {resource.name: self.resources[resource] for resource, amount in self.resources.items()}

    def load_from_json(self, treasury_dict: dict[str, int]) -> None:
        for resource, amount in treasury_dict.items():
            self.resources[Resource[resource]] = amount
        self.display_state_changed = True
