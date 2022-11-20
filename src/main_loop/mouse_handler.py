from __future__ import annotations
import pygame as pg


class MouseHandler:
    def __init__(self) -> None:
        self.is_lmb_pressed: bool = False
        self.is_rmb_pressed: bool = False

    def lmb_press(self) -> None:
        self.is_lmb_pressed = True

    def lmb_release(self) -> None:
        self.is_lmb_pressed = False

    def lmb_held_down(self) -> None:
        pass

    def rmb_press(self) -> None:
        self.is_rmb_pressed = True

    def rmb_release(self) -> None:
        self.is_rmb_pressed = False

    def mmb_press(self) -> None:
        pass
