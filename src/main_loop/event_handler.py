from __future__ import annotations
import pygame as pg
from typing import TYPE_CHECKING
from src.sound.soundtrack import Soundtrack, END_TRACK
if TYPE_CHECKING:
    from src.main_loop.mouse_handler import MouseHandler
    from src.main_loop.keyboard_handler import KeyboardHandler


class EventHandler:
    def __init__(self, mouse_handler: MouseHandler, keyboard_handler: KeyboardHandler, soundtrack: Soundtrack) -> None:
        self.mouse_handler: MouseHandler = mouse_handler
        self.keyboard_handler: KeyboardHandler = keyboard_handler
        self.soundtrack: Soundtrack = soundtrack

    def handle_events(self) -> None:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.mouse_handler.lmb_press()
                if event.button == 2:
                    self.mouse_handler.mmb_press()
                if event.button == 3:
                    self.mouse_handler.rmb_press()
            if event.type == pg.MOUSEBUTTONUP:
                if event.button == 1:
                    self.mouse_handler.lmb_release()
                if event.button == 3:
                    self.mouse_handler.rmb_release()
            if event.type == pg.KEYDOWN:
                self.keyboard_handler.key_pressed(event.key)
            if event.type == pg.KEYUP:
                self.keyboard_handler.key_released(event.key)

            if event.type == END_TRACK:
                self.soundtrack.queue_next_track()

        self.mouse_handler.handle_pressed()
        self.keyboard_handler.handle_pressed()


