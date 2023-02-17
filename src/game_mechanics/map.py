from __future__ import annotations
import pygame as pg
from src.core_classes import *

U = TypeVar('U')


class Map(Generic[U]):
    def __init__(self, size: Vector[int]) -> None:
        self.elements: dict[tuple[int, int], U] = {}
        self.size: Vector[int] = size

    def __getitem__(self, pos: Vector[int] | tuple[int, int]) -> Optional[U]:
        if not self.contains(pos):
            return None
        if isinstance(pos, Vector):
            return self.elements[pos.to_tuple()]
        elif isinstance(pos, tuple):
            return self.elements[pos]
        else:
            raise TypeError

    def __setitem__(self, pos: Vector[int] | tuple[int, int], element: U) -> None:
        if not self.contains(pos):
            return None
        if isinstance(pos, Vector):
            self.elements[pos.to_tuple()] = element
        elif isinstance(pos, tuple):
            self.elements[pos] = element
        else:
            raise TypeError

    def __str__(self) -> str:
        return "\n".join([" ".join([str(self[x, y]) for x in range(self.size.x)]) for y in range(self.size.y)])

    def contains(self, pos: Vector[int] | tuple[int, int]) -> bool:
        if isinstance(pos, Vector):
            return 0 <= pos.x < self.size.x and 0 <= pos.y < self.size.y
        elif isinstance(pos, tuple):
            return 0 <= pos[0] < self.size.x and 0 <= pos[1] < self.size.y
        else:
            raise TypeError
