from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Generic, TypeVar, overload

import src.core.enums as enums

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

    def to_dir(self: Vector[int]) -> Optional[enums.Direction]:
        return {Vector(0, -1): enums.Direction.N,
                Vector(1, 0): enums.Direction.E,
                Vector(0, 1): enums.Direction.S,
                Vector(-1, 0): enums.Direction.W}.get(self)

    def to_tuple(self) -> tuple[T, T]:
        return self.x, self.y

    def to_float(self: Vector[int]) -> Vector[float]:
        return Vector(float(self.x), float(self.y))

    def to_int(self: Vector[float]) -> Vector[int]:
        return Vector(int(self.x), int(self.y))

    def neighbours(self: Vector[int]) -> tuple[Vector, Vector, Vector, Vector]:
        return (Vector(self.x, self.y - 1),
                Vector(self.x + 1, self.y),
                Vector(self.x, self.y + 1),
                Vector(self.x - 1, self.y))
