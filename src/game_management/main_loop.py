from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.game_management.event_handler import EventHandler
    from src.game_management.time_manager import TimeManager
    from src.graphics.renderer import Renderer
    from src.graphics.scene import Scene
    from src.ui.ui import UI
    from src.sound.soundtrack import Soundtrack


class MainLoop:
    def __init__(self, event_handler: EventHandler, renderer: Renderer, scene: Scene, ui: UI, soundtrack: Soundtrack,
                 time_manager: TimeManager) -> None:
        self.running: bool = True
        self.event_handler: EventHandler = event_handler
        self.renderer: Renderer = renderer
        self.scene: Scene = scene
        self.ui: UI = ui
        self.time_manager: TimeManager = time_manager

        soundtrack.start()

        self.loop()

    def loop(self) -> None:
        while self.running:
            self.ui.button_manager.check_for_hovers()
            self.event_handler.handle_events()
            self.renderer.render()
            self.scene.update()
            self.time_manager.tick()
