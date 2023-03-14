from __future__ import annotations

import sys

from typing import TYPE_CHECKING

from src.core.user_events import *
from src.sound.soundtrack import Soundtrack

if TYPE_CHECKING:
    from src.game_management.mouse_handler import MouseHandler
    from src.game_management.keyboard_handler import KeyboardHandler


class EventHandler:
    def __init__(self, mouse_handler: MouseHandler, keyboard_handler: KeyboardHandler, soundtrack: Soundtrack) -> None:
        self.mouse_handler: MouseHandler = mouse_handler
        self.keyboard_handler: KeyboardHandler = keyboard_handler
        self.soundtrack: Soundtrack = soundtrack

    def handle_events(self) -> None:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            elif event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.mouse_handler.lmb_press()
                elif event.button == 2:
                    self.mouse_handler.mmb_press()
                elif event.button == 3:
                    self.mouse_handler.rmb_press()
            elif event.type == pg.MOUSEBUTTONUP:
                if event.button == 1:
                    self.mouse_handler.lmb_release()
                elif event.button == 3:
                    self.mouse_handler.rmb_release()
            elif event.type == pg.KEYDOWN:
                if not self.mouse_handler.is_lmb_pressed and not self.mouse_handler.is_rmb_pressed:
                    self.keyboard_handler.key_pressed(event.key)
            elif event.type == pg.KEYUP:
                self.keyboard_handler.key_released(event.key)
            elif event.type == ALL_KEYS_AND_BUTTONS_UP:
                self.mouse_handler.lmb_release()
                self.mouse_handler.rmb_release()
                self.keyboard_handler.pressed_keys_time.clear()

            elif event.type == END_TRACK:
                self.soundtrack.queue_next_track()

        self.mouse_handler.handle_pressed()
        self.keyboard_handler.handle_pressed()
