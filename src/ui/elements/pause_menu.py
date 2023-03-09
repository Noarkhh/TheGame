from __future__ import annotations

import json
import os
import time
import sys
from typing import TYPE_CHECKING, Callable, Optional

import pygame as pg

from src.core.user_events import ALL_KEYS_AND_BUTTONS_UP
from src.ui.elements.ui_element import UIElement

if TYPE_CHECKING:
    from src.ui.button_manager import ButtonManager
    from src.game_management.save_manager import SaveManager
    from src.ui.button import Button
    from src.graphics.spritesheet import Spritesheet

# mypy: disable-error-code=misc


class PauseMenu(UIElement):
    def __init__(self, spritesheet: Spritesheet, button_manager: ButtonManager, save_manager: SaveManager,
                 button_specs: dict[str, list]) -> None:
        self.save_manager: SaveManager = save_manager
        self.image: pg.Surface = spritesheet.get_ui_image("Decorative", "pause_menu")
        self.rect: pg.Rect = self.image.get_rect(center=(self.ui.window_size / 2).to_tuple())

        super().__init__(self.image, self.rect, spritesheet, button_manager, button_specs)

        self.is_loaded = False

        self.buttons_to_functions: dict[str, Optional[Callable]] = {
            "Resume": self.unload,
            "Save": self.load_saving_view,
            "Load": self.load_loading_view,
            "Options": None,
            "Quit": self.quit,
            "delete": None,
            "save": None,
            "load": None,
            "back": None
        }
        with open("saves/save_dates.json", "r") as f:
            self.save_names = json.load(f)
            assert isinstance(self.save_names, list) and all(isinstance(name, str) for name in self.save_names)

        self.selected_savefile_button: Optional[Button] = None
        self.is_in_saving_mode: bool = True
        self.action_buttons: pg.sprite.Group[Button] = pg.sprite.Group()

    def load(self) -> None:
        super().load()
        self.load_main_view()

        self.pause_loop()

    def pause_loop(self) -> None:
        clock: pg.time.Clock = pg.time.Clock()
        button_manager: ButtonManager = self.ui.button_manager
        button_manager.held_button = None
        global_buttons = button_manager.buttons
        button_manager.buttons = self.buttons

        while self.is_loaded:
            button_manager.check_for_hovers()
            self.handle_pause_events()
            self.ui.draw_elements()

            pg.display.flip()
            clock.tick(60)

        pg.event.post(pg.event.Event(ALL_KEYS_AND_BUTTONS_UP))
        button_manager.buttons = global_buttons

    def handle_pause_events(self) -> None:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                self.ui.button_manager.lmb_press()
            if event.type == pg.MOUSEBUTTONUP and event.button == 1:
                self.ui.button_manager.lmb_release()
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                self.unload()

    def load_main_view(self) -> None:
        for button in self.buttons:
            button.kill()
        for name in ("Resume", "Save", "Load", "Options", "Quit"):
            self.create_text_button(name, *self.button_specs[name], function=self.buttons_to_functions[name])

    def load_saving_view(self) -> None:
        self.is_in_saving_mode = True
        self.load_savefiles_view()

    def load_loading_view(self) -> None:
        self.is_in_saving_mode = False
        self.load_savefiles_view()

    def load_savefiles_view(self) -> None:
        for button in self.buttons:
            button.kill()
        self.create_icon_button("back", *self.button_specs["back"], function=self.load_main_view)
        for save_id in range(5):
            self.create_text_button(self.save_names[save_id], *self.button_specs["savefile" + str(save_id)],
                                    function=self.choose_savefile, function_args=(save_id,), self_reference=True)

    # noinspection PyTypeChecker
    def choose_savefile(self, save_id: int, savefile_button: Button) -> None:
        for action_button in self.action_buttons:
            action_button.kill()
        if self.selected_savefile_button is not None:
            self.selected_savefile_button.unlock()
        self.selected_savefile_button = savefile_button
        savefile_button.lock(in_pressed_state=True)

        if self.is_in_saving_mode:
            self.action_buttons.add(self.create_icon_button("save", *self.button_specs["save"],
                                                            function=self.savefile_save,
                                                            function_args=(save_id,)))
        if self.save_names[save_id] != "Empty Slot":
            self.action_buttons.add(self.create_icon_button("delete", *self.button_specs["delete"],
                                                            function=self.savefile_delete,
                                                            function_args=(save_id,)))
            if not self.is_in_saving_mode:
                self.action_buttons.add(self.create_icon_button("load", *self.button_specs["load"],
                                                                function=self.savefile_load,
                                                                function_args=(save_id,)))

    def savefile_save(self, save_id: int) -> None:
        self.save_names[save_id] = time.strftime("%H:%M %d-%m-%y")
        with open("saves/save_dates.json", "w+") as f:
            json.dump(self.save_names, f)
        self.save_manager.save_to_savefile(save_id)
        self.load_savefiles_view()

    def savefile_delete(self, save_id: int) -> None:
        self.save_names[save_id] = "Empty Slot"
        with open("saves/save_dates.json", "w+") as f:
            json.dump(self.save_names, f)
        os.remove(f"saves/savefile{save_id}.json")
        self.load_savefiles_view()

    def savefile_load(self, save_id: int) -> None:
        if self.save_names[save_id] == "Empty Slot":
            self.load_savefiles_view()
            return
        self.save_manager.load_from_savefile(save_id)
        self.unload()

    def quit(self) -> None:
        pg.quit()
        sys.exit()
