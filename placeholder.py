import typing
from enum import IntEnum
import pygame as pg


class Pos:
    def __init__(self, x: int, y: int):
        self.x: int = x
        self.y: int = y

    def __sub__(self, other: 'Pos') -> 'Pos':
        return Pos(self.x - other.x, self.y - other.y)

    def __add__(self, other: 'Pos') -> 'Pos':
        return Pos(self.x + other.x, self.y + other.y)

    def __mul__(self, other: int) -> 'Pos':
        return Pos(self.x * other, self.y * other)

    def __eq__(self, other: 'Pos') -> 'Pos':
        return self.x == other.x and self.y == other.y

    def __str__(self) -> str:
        return f'({self.x}, {self.y})'

    def __hash__(self):
        return hash((self.__class__, self.x, self.y))

    def to_dir(self) -> 'Direction':
        return {Pos(0, -1): Direction.N,
                Pos(1, 0): Direction.E,
                Pos(0, 1): Direction.S,
                Pos(-1, 0): Direction.W}.get(self)

    def to_tuple(self) -> tuple:
        return self.x, self.y


class Map:
    def __init__(self, elements):
        self.elements = elements
        self.width = len(elements)
        self.height = len(elements[0])

    def __getitem__(self, pos: Pos):
        if isinstance(pos, Pos):
            return self.elements[pos.x][pos.y]
        elif isinstance(pos, tuple) or isinstance(pos, list):
            return self.elements[pos[0]][pos[1]]

    def __str__(self):
        return "\n".join([" ".join([str(self[x, y]) for x in range(self.width)]) for y in range(self.height)])

    def contains(self, pos: Pos) -> bool:
        return 0 <= pos.x < self.width and 0 <= pos.y < self.height


class Direction(IntEnum):
    N = 0
    E = 1
    S = 2
    W = 3

    def to_pos(self) -> Pos:
        return {self.N: Pos(0, -1),
                self.E: Pos(1, 0),
                self.S: Pos(0, 1),
                self.W: Pos(-1, 0)}[self]

    def __neg__(self) -> 'Direction':
        return {self.N: self.S,
                self.E: self.W,
                self.S: self.N,
                self.W: self.E}[self]


class Structure(pg.sprite.Sprite):
    def __init__(self, pos: Pos, gw):
        super().__init__()
        self.pos = pos

    def __repr__(self):
        return f'{self.__class__.__name__}(pos: {self.pos})'

