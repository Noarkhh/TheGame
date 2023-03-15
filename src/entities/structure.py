from __future__ import annotations

from abc import ABCMeta
from typing import Type, ClassVar, cast, Self, TYPE_CHECKING, Optional, Any

from src.core.enums import Terrain, Resource, Message, Orientation, DirectionSet, Tile
from src.entities.snapper import Snapper
from src.entities.tile_entity import TileEntity
from src.resources.resource_manager import ResourceManager

if TYPE_CHECKING:
    from src.game_mechanics.struct_manager import StructManager
    from src.core.vector import Vector


class Structure(TileEntity, metaclass=ABCMeta):
    unsuitable_terrain: ClassVar[list[Terrain]] = [Terrain.WATER]
    overrider: ClassVar[bool] = False

    base_cost: ClassVar[dict[Resource, int]]
    base_instant_profit: ClassVar[dict[Resource, int]]
    base_upkeep: ClassVar[dict[Resource, int]]
    base_profit: ClassVar[dict[Resource, int]]
    base_capacity: ClassVar[int]
    base_cooldown: ClassVar[int]

    manager: ClassVar[StructManager]

    resource_manager: ResourceManager
    efficiency: float

    def __init__(self, pos: Vector[int], image_variant: int = 0, orientation: Orientation = Orientation.VERTICAL,
                 is_ghost: bool = False) -> None:
        super().__init__(pos, image_variant, is_ghost)

        self.orientation: Orientation = orientation

        if not self.is_ghost:
            self.manager.structs.add(self)
            self.resource_manager = ResourceManager(self, self.manager.treasury)

        self.efficiency = 1.0

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(pos: {self.pos}, efficiency: {self.efficiency}, stockpile: {self.resource_manager.stockpile})"

    def can_be_placed(self) -> Message:
        tile_map = self.manager.map_container.tile_map
        struct_map = self.manager.map_container.struct_map

        if not self.manager.treasury.can_afford(self.base_cost):
            return Message.NO_RESOURCES

        if any(isinstance(struct_map[self.pos + rel_pos], Structure) for rel_pos in self.covered_tiles):
            return Message.BAD_LOCATION_STRUCT

        for rel_pos in self.covered_tiles:
            if tile_map[self.pos + rel_pos] is None or \
                    cast(Tile, tile_map[self.pos + rel_pos]).terrain in self.unsuitable_terrain:
                return Message.BAD_LOCATION_TERRAIN

        if any(cast(Tile, tile_map[self.pos + rel_pos]).terrain in self.unsuitable_terrain for rel_pos in
               self.covered_tiles):
            return Message.BAD_LOCATION_TERRAIN

        return Message.BUILT

    def can_be_snapped(self, prev_pos: Vector[int], connector: Type[Structure]) -> Message:
        return Message.NOT_A_SNAPPER

    def update(self, *args: Any, **kwargs: Any) -> None:
        self.resource_manager.update_cooldown()

    def build(self) -> None:
        pass

    def demolish(self) -> None:
        self.kill()
        self.resource_manager.refund()

    def copy(self: Self, neighbours: Optional[DirectionSet] = None) -> Self:
        new_copy = self.__class__(self.pos, image_variant=self.image_variant, orientation=self.orientation)
        if neighbours is not None:
            assert isinstance(new_copy, Snapper)
            new_copy.add_neighbours(neighbours)
        return new_copy

    def save_to_json(self) -> dict:
        return {
            "type": self.__class__.__name__,
            "pos": self.pos.to_tuple(),
            "orientation": self.orientation.name,
            "image_variant": self.image_variant,

            "cost": {resource.name: amount for resource, amount in self.base_cost.items()},
            "profit": {resource.name: amount for resource, amount in self.base_profit.items()},
            "capacity": self.base_capacity,
            "cooldown": self.base_cooldown,
            "cooldown_left": self.cooldown_left,
            "stockpile": {resource.name: amount for resource, amount in self.stockpile.items()}
        }

    def load_from_json(self, struct_dict: dict) -> None:
        self.cost = {Resource[name]: amount for name, amount in struct_dict["cost"].items()}
        self.profit = {Resource[name]: amount for name, amount in struct_dict["profit"].items()}
        self.capacity = struct_dict["capacity"]
        self.cooldown = struct_dict["cooldown"]
        self.cooldown_left = struct_dict["cooldown_left"]
        self.stockpile = {Resource[name]: amount for name, amount in struct_dict["stockpile"].items()}
