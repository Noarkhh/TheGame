from __future__ import annotations
from enum import Enum, IntEnum
from typing import Optional
from dataclasses import dataclass


@dataclass(frozen=True)
class Vector:
    x: int
    y: int

    def __sub__(self, other: Vector | tuple[int, int]) -> Vector:
        if isinstance(other, Vector):
            return Vector(self.x - other.x, self.y - other.y)
        if isinstance(other, tuple):
            return Vector(self.x - other[0], self.y - other[1])

    def __add__(self, other: Vector | tuple[int, int]) -> Vector:
        if isinstance(other, Vector):
            return Vector(self.x + other.x, self.y + other.y)
        if isinstance(other, tuple):
            return Vector(self.x + other[0], self.y + other[1])

    def __neg__(self) -> Vector:
        return Vector(-self.x, -self.y)

    def __mul__(self, other: int | Vector) -> Vector:
        if isinstance(other, int):
            return Vector(self.x * other, self.y * other)
        if isinstance(other, Vector):
            return Vector(self.x * other.x, self.y * other.y)

    def to_dir(self) -> Optional[Direction]:
        return {Vector(0, -1): Direction.N,
                Vector(1, 0): Direction.E,
                Vector(0, 1): Direction.S,
                Vector(-1, 0): Direction.W}.get(self)

    def to_tuple(self) -> tuple:
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

    def __neg__(self) -> Direction:
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
