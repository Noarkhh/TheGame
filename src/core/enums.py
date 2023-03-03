from __future__ import annotations

from enum import Enum, IntEnum, auto
from typing import Optional

from src.core.vector import Vector


class Direction(IntEnum):
    N = 0
    E = 1
    S = 2
    W = 3

    def to_vector(self) -> Vector:
        return {self.N: Vector(0, -1),
                self.E: Vector(1, 0),
                self.S: Vector(0, 1),
                self.W: Vector(-1, 0)}[self]

    def to_tuple(self) -> tuple[int, int]:
        return {self.N: (0, -1),
                self.E: (1, 0),
                self.S: (0, 1),
                self.W: (-1, 0)}[self]

    def opposite(self) -> Direction:
        return {self.N: Direction.S,
                self.E: Direction.W,
                self.S: Direction.N,
                self.W: Direction.E}[self]


class DirectionSet(set[Direction]):
    def get_id(self) -> int:
        return sum(2 ** elem for elem in self)


class Orientation(IntEnum):
    VERTICAL = 0
    HORIZONTAL = 1


class Tile:
    size: int

    def __init__(self, terrain: Terrain, resource: Optional[Resource] = None) -> None:
        self.terrain: Terrain = terrain
        self.resource: Optional[Resource] = resource


class Terrain(Enum):
    GRASSLAND = auto()
    DESERT = auto()
    WATER = auto()

    def __repr__(self) -> str:
        return self.name


class Resource(Enum):
    WOOD = auto()
    STONE = auto()
    WHEAT = auto()
    COAL = auto()
    ORE = auto()
    IRON = auto()
    BRICKS = auto()
    STEEL = auto()
    BEAMS = auto()
    BREAD = auto()
    ASTRUM = auto()
    GOLD = auto()

    def __repr__(self) -> str:
        return self.name


class Message(Enum):
    BUILT = auto()
    SNAPPED = auto()
    OVERRODE = auto()

    BAD_LOCATION_TERRAIN = auto()
    BAD_LOCATION_STRUCT = auto()
    NO_RESOURCES = auto()

    NOT_A_SNAPPER = auto()
    BAD_CONNECTOR = auto()
    NOT_ADJACENT = auto()
    OTHER_IS_NONE = auto()
    OTHER_CANT_SNAP = auto()
    BAD_MATCH = auto()
    ALREADY_SNAPPED = auto()

    CANT_OVERRIDE = auto()

    def success(self) -> bool:
        return self in (Message.BUILT, Message.SNAPPED, Message.OVERRODE)
