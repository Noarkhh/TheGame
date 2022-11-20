from __future__ import annotations
import pygame as pg
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.main_loop.event_handler import EventHandler


class MainLoop:
    def __init__(self, event_handler: EventHandler) -> None:
        self.clock: pg.time.Clock = pg.time.Clock()
        self.running: bool = True
        self.event_handler: EventHandler = event_handler
        self.loop()

    def loop(self):
        while self.running:
            self.event_handler.handle_events()
            self.clock.tick()
