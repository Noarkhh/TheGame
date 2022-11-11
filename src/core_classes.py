from __future__ import annotations
from enum import Enum, IntEnum
from typing import Optional, Generic, TypeVar
from dataclasses import dataclass

T = TypeVar('T', int, float)


@dataclass(frozen=True)
class Vector(Generic[T]):
    x: T
    y: T

    def __sub__(self, other: Vector[T] | tuple[T, T]) -> Vector[T]:
        if isinstance(other, Vector):
            return Vector[T](self.x - other.x, self.y - other.y)
        if isinstance(other, tuple):
            return Vector[T](self.x - other[0], self.y - other[1])

    def __add__(self, other: Vector[T] | tuple[T, T]) -> Vector[T]:
        if isinstance(other, Vector):
            return Vector[T](self.x + other.x, self.y + other.y)
        if isinstance(other, tuple):
            return Vector[T](self.x + other[0], self.y + other[1])

    def __neg__(self) -> Vector[T]:
        return Vector[T](-self.x, -self.y)

    def __mul__(self, other: T | Vector[T]) -> Vector[T]:
        if isinstance(other, int) or isinstance(other, float):
            return Vector[T](self.x * other, self.y * other)
        if isinstance(other, Vector):
            return Vector[T](self.x * other.x, self.y * other.y)

    def to_dir(self: Vector[int]) -> Optional[Direction]:
        return {Vector(0, -1): Direction.N,
                Vector(1, 0): Direction.E,
                Vector(0, 1): Direction.S,
                Vector(-1, 0): Direction.W}.get(self)

    def to_tuple(self) -> tuple[T, T]:
        return self.x, self.y


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

    def opposite(self) -> Direction:
        return {self.N: Direction.S,
                self.E: Direction.W,
                self.S: Direction.N,
                self.W: Direction.E}[self]


class DirectionSet(set):
    def get_id(self) -> int:
        return sum(2 ** elem for elem in self)


class Orientation(IntEnum):
    VERTICAL = 0
    HORIZONTAL = 1


class Tile:
    def __init__(self, terrain: Terrain, resource: Optional[Resource] = None) -> None:
        self.terrain: Terrain = terrain
        self.resource: Optional[Resource] = resource


class Terrain(Enum):
    GRASSLAND = 0
    DESERT = 1
    WATER = 2

    def __repr__(self) -> str:
        return self.name


class Resource(Enum):
    WOOD = 0
    STONE = 1
    WHEAT = 2
    COAL = 3
    ORE = 4
    IRON = 5
    CHARCOAL = 6
    BRICKS = 7
    STEEL = 8
    REINFORCED_WOOD = 9
    BREAD = 10
    METEORITE = 11
    GOLD = 12

    def __repr__(self) -> str:
        return self.name


class Message(Enum):
    BUILT = 0
    SNAPPED = 1
    OVERRODE = 2

    BAD_LOCATION_TERRAIN = 3
    BAD_LOCATION_STRUCT = 4
    NO_RESOURCES = 5

    BAD_CONNECTOR = 6
    NOT_ADJACENT = 7
    ONE_CANT_SNAP = 8
    BAD_MATCH = 9
    ALREADY_SNAPPED = 10

    CANT_OVERRIDE = 11

    def success(self) -> bool:
        if self in (Message.BUILT, Message.SNAPPED, Message.OVERRODE):
            return True
        return False
