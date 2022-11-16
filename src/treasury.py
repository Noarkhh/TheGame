from __future__ import annotations
from src.core_classes import *
if TYPE_CHECKING:
    from src.config import Config
    from src.structures import Structure


class Treasury:
    def __init__(self, config: Config) -> None:
        self.resources: dict[Resource, int] = config.get_starting_resources()

    def pay_for(self, struct: Structure) -> None:
        for resource, amount in struct.cost.items():
            self.resources[resource] -= amount
