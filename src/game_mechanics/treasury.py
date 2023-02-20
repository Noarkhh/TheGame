from __future__ import annotations
from src.core.enums import *
if TYPE_CHECKING:
    from src.core.config import Config
    from src.game_mechanics.structures import Structure


class Treasury:
    def __init__(self, config: Config) -> None:
        self.resources: dict[Resource, int] = config.get_starting_resources()

    def pay_for(self, struct: Structure) -> None:
        for resource, amount in struct.cost.items():
            self.resources[resource] -= amount
