from __future__ import annotations

from abc import ABCMeta
from typing import Type, ClassVar, cast, Self, TYPE_CHECKING, Optional

from src.core.enums import Terrain, Resource, Message, Orientation, DirectionSet, Tile
from src.entities.snapper import Snapper
from src.entities.tile_entity import TileEntity

if TYPE_CHECKING:
    from src.game_mechanics.struct_manager import StructManager
    from src.core.vector import Vector


class Structure(TileEntity, metaclass=ABCMeta):
    unsuitable_terrain: ClassVar[list[Terrain]] = [Terrain.WATER]
    overrider: ClassVar[bool] = False

    base_cost: ClassVar[dict[Resource, int]]
    base_profit: ClassVar[dict[Resource, int]]
    base_capacity: ClassVar[int]
    base_cooldown: ClassVar[int]

    manager: ClassVar[StructManager]

    def __init__(self, pos: Vector[int], image_variant: int = 0, orientation: Orientation = Orientation.VERTICAL,
                 is_ghost: bool = False) -> None:
        super().__init__(pos, image_variant, is_ghost)

        self.orientation: Orientation = orientation

        if not self.is_ghost:
            self.manager.structs.add(self)

        self.cost: dict[Resource, int] = self.base_cost.copy()
        self.profit: dict[Resource, int] = self.base_profit.copy()
        self.capacity: int = self.base_capacity
        self.cooldown: int = self.base_cooldown

        self.cooldown_left: int = self.cooldown
        self.stockpile: dict[Resource, int] = {resource: 0 for resource in self.base_profit.keys()}

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(pos: {self.pos})'

    def can_be_placed(self) -> Message:
        tile_map = self.manager.map_manager.tile_map
        struct_map = self.manager.map_manager.struct_map

        if any(isinstance(struct_map[self.pos + rel_pos], Structure) for rel_pos in self.covered_tiles):
            return Message.BAD_LOCATION_STRUCT

        if any(cast(Tile, tile_map[self.pos + rel_pos]).terrain in
               self.unsuitable_terrain for rel_pos in self.covered_tiles):
            return Message.BAD_LOCATION_TERRAIN

        if any(amount > self.manager.treasury.resources[resource] for resource, amount in self.base_cost.items()):
            return Message.NO_RESOURCES

        return Message.BUILT

    def can_be_snapped(self, prev_pos: Vector[int], connector: Type[Structure]) -> Message:
        return Message.NOT_A_SNAPPER

    def produce(self) -> None:
        self.cooldown_left -= 1
        if self.cooldown_left == 0:
            if sum(self.stockpile.values()) < self.base_capacity:
                for resource, amount in self.base_profit.items():
                    self.stockpile[resource] += amount
            self.cooldown_left = self.base_cooldown

    def copy(self: Self, neighbours: Optional[DirectionSet] = None) -> Self:
        new_copy = self.__class__(self.pos, image_variant=self.image_variant, orientation=self.orientation)
        if neighbours is not None:
            assert isinstance(new_copy, Snapper)
            new_copy.add_neighbours(neighbours)
        return new_copy

    def to_json(self) -> dict:
        return {
            "type": self.__class__.__name__,
            "pos": self.pos.to_tuple(),
            "orientation": self.orientation,
            "sprite_variant": self.image_variant,

            "cost": {resource.name: amount for resource, amount in self.base_cost.items()},
            "profit": {resource.name: amount for resource, amount in self.base_cost.items()},
            "capacity": self.base_capacity,
            "cooldown": self.base_cooldown,
            "cooldown_left": self.cooldown_left,
            "stockpile": {resource.name: amount for resource, amount in self.stockpile.items()}
        }

    def from_json(self, y: dict) -> None:
        self.cost = {Resource[name]: amount for name, amount in y["cost"]}
        self.profit = {Resource[name]: amount for name, amount in y["profit"]}
        self.capacity = y["capacity"]
        self.cooldown = y["cooldown"]
        self.cooldown_left = y["cooldown_left"]
        self.stockpile = {Resource[name]: amount for name, amount in y["stockpile"]}
