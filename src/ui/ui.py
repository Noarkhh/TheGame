from __future__ import annotations
import pygame as pg
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.ui.button_manager import ButtonManager


class UI:
    def __init__(self, button_manager: ButtonManager) -> None:
        self.button_manager: ButtonManager = button_manager

