from __future__ import annotations
from enum import Enum, IntEnum, auto
from typing import Optional, Generic, TypeVar, TYPE_CHECKING, overload
from dataclasses import dataclass

T = TypeVar('T', int, float)


@dataclass(init=False, unsafe_hash=True)
class Vector(Generic[T]):
    @overload
    def __init__(self, x: tuple[T, T]) -> None: ...
    @overload
    def __init__(self, x: T, y: T) -> None: ...

    def __init__(self, x: tuple[T, T] | T, y: Optional[T] = None) -> None:
        if isinstance(x, tuple):
            self._x: T = x[0]
            self._y: T = x[1]
        elif y is not None:
            self._x = x
            self._y = y
        else:
            raise TypeError

    @property
    def x(self) -> T:
        return self._x

    @property
    def y(self) -> T:
        return self._y

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Vector):
            return self.x == other.x and self.y == other.y
        return NotImplemented

    def __sub__(self, other: Vector[T] | tuple[T, T]) -> Vector[T]:
        if isinstance(other, Vector):
            return Vector(self.x - other.x, self.y - other.y)
        if isinstance(other, tuple):
            return Vector(self.x - other[0], self.y - other[1])

    def __add__(self, other: Vector[T] | tuple[T, T]) -> Vector[T]:
        if isinstance(other, Vector):
            return Vector(self.x + other.x, self.y + other.y)
        if isinstance(other, tuple):
            return Vector(self.x + other[0], self.y + other[1])

    def __neg__(self) -> Vector[T]:
        return Vector(-self.x, -self.y)

    def __mul__(self, other: T) -> Vector[T]:
        if isinstance(other, int) or isinstance(other, float):
            return Vector(self.x * other, self.y * other)
        if isinstance(other, Vector):
            return Vector(self.x * other.x, self.y * other.y)

    def __floordiv__(self, other: int) -> Vector[int]:
        return Vector(int(self.x // other), int(self.y // other))

    def __truediv__(self, other: int | float) -> Vector[float]:
        return Vector(self.x / other, self.y / other)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.x}, {self.y})"

    def to_dir(self: Vector[int]) -> Optional[Direction]:
        return {Vector(0, -1): Direction.N,
                Vector(1, 0): Direction.E,
                Vector(0, 1): Direction.S,
                Vector(-1, 0): Direction.W}.get(self)

    def to_tuple(self) -> tuple[T, T]:
        return self.x, self.y

    def to_float(self: Vector[int]) -> Vector[float]:
        return Vector(float(self.x), float(self.y))

    def to_int(self: Vector[float]) -> Vector[int]:
        return Vector(int(self.x), int(self.y))


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
    CHARCOAL = auto()
    BRICKS = auto()
    STEEL = auto()
    REINFORCED_WOOD = auto()
    BREAD = auto()
    METEORITE = auto()
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
    ONE_CANT_SNAP = auto()
    BAD_MATCH = auto()
    ALREADY_SNAPPED = auto()

    CANT_OVERRIDE = auto()

    def success(self) -> bool:
        return self in (Message.BUILT, Message.SNAPPED, Message.OVERRODE)
