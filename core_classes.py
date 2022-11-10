from __future__ import annotations
from enum import Enum, IntEnum
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

    def to_dir(self) -> Directions:
        return {Vector(0, -1): Directions.N,
                Vector(1, 0): Directions.E,
                Vector(0, 1): Directions.S,
                Vector(-1, 0): Directions.W}.get(self)

    def to_tuple(self) -> tuple:
        return self.x, self.y


class Directions(IntEnum):
    N = 0
    E = 1
    S = 2
    W = 3

    def to_vector(self) -> Vector:
        return {self.N: Vector(0, -1),
                self.E: Vector(1, 0),
                self.S: Vector(0, 1),
                self.W: Vector(-1, 0)}[self]

    def __neg__(self) -> Directions:
        return {self.N: self.S,
                self.E: self.W,
                self.S: self.N,
                self.W: self.E}[self]


class DirectionSet(set):
    def get_id(self) -> int:
        return sum(2 ** elem for elem in self)


class Orientation(IntEnum):
    VERTICAL = 0
    HORIZONTAL = 1


class Tile:
    def __init__(self, terrain: 'Terrain', resource: 'Resources'):
        self.terrain = terrain
        self.resource = resource


class Terrain(Enum):
    GRASSLAND = 0
    DESERT = 1
    WATER = 2

    def __repr__(self):
        return self.name


class Resources(Enum):
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

    def __repr__(self):
        return self.name
