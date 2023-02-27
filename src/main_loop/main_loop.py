from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

if TYPE_CHECKING:
    from src.main_loop.event_handler import EventHandler
    from src.graphics.renderer import Renderer
    from src.graphics.scene import Scene
    from src.ui.ui import UI
    from src.sound.soundtrack import Soundtrack


class MainLoop:
    def __init__(self, event_handler: EventHandler, renderer: Renderer, scene: Scene, ui: UI, soundtrack: Soundtrack,
                 frame_rate: int) -> None:
        self.clock: pg.time.Clock = pg.time.Clock()
        self.running: bool = True
        self.event_handler: EventHandler = event_handler
        self.renderer: Renderer = renderer
        self.scene: Scene = scene
        self.ui: UI = ui
        self.frame_rate: int = frame_rate

        soundtrack.start()

        self.loop()

    def loop(self) -> None:
        while self.running:
            self.ui.button_manager.check_for_hovers()
            self.event_handler.handle_events()
            self.renderer.render()
            self.scene.update()
            self.clock.tick(self.frame_rate)
