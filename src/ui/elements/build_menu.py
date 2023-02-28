from __future__ import annotations

from enum import Enum, auto
from typing import TYPE_CHECKING, Type

import pygame as pg

from src.ui.elements.ui_element import UIElement

if TYPE_CHECKING:
    from src.graphics.spritesheet import Spritesheet
    from src.ui.button_manager import ButtonManager
    from src.ui.button import Button
    from src.core.config import Config
    from src.entities.structures import Structure


class Category(Enum):
    HOUSING = auto()
    MILITARY = auto()
    TRANSPORT = auto()
    MANUFACTURING = auto()
    AGRICULTURE = auto()
    RELIGION = auto()


class BuildMenu(UIElement):
    def __init__(self, config: Config, spritesheet: Spritesheet, button_manager: ButtonManager,
                 button_specs: dict[str, list]) -> None:
        self.image: pg.Surface = spritesheet.get_ui_image("Decorative", "build_menu")
        self.rect: pg.Rect = self.image.get_rect(centerx=self.ui.window_size.x // 2, top=44)
        self.structure_buttons_field_pos_x: int = 136

        self.categories: dict[Category, list[Type[Structure]]] = config.get_structure_categories()
        self.category_buttons: dict[Category, Button] = {}
        self.current_category: Category = Category.HOUSING
        self.current_category_structs_buttons: pg.sprite.Group[Button] = pg.sprite.Group()

        super().__init__(self.image, self.rect, spritesheet, button_manager, button_specs)
        self.load()

    def unload(self) -> None:
        super().unload()
        if self.ui.toolbar.named_buttons.build is not None:
            self.ui.toolbar.named_buttons.build.unlock()

    def load(self) -> None:
        super().load()
        if self.ui.toolbar.named_buttons.build is not None:
            self.ui.toolbar.named_buttons.build.lock(in_pressed_state=True)
        for (button_name, (shape, position, scale)), category in zip(self.button_specs.items(), self.categories):
            self.category_buttons[category] = \
                self.create_icon_button(button_name, shape, position, scale, self.load_category,
                                        function_args=(category,), hover_sound="metrollover", self_reference=True)
        self.load_category(self.current_category, self.category_buttons[self.current_category])

    def load_category(self, category: Category, category_button: Button) -> None:
        for button in self.current_category_structs_buttons:
            button.kill()
        self.category_buttons[self.current_category].unlock()
        category_button.lock(in_pressed_state=True)
        self.current_category = category
        button_pos_x = self.structure_buttons_field_pos_x

        for struct_class in self.categories[category]:
            icon_image = self.spritesheet.get_image(struct_class, scale=60)
            shape = "rectangle_wide" if icon_image.get_width() > 60 else "rectangle"
            contents_height = 120 - icon_image.get_height()
            new_button: Button = self.create_image_button(icon_image, shape, [button_pos_x, 0],
                                                          self.ui.cursor.assign_entity_class,
                                                          function_args=(struct_class,), contents_height=contents_height)
            self.current_category_structs_buttons.add(new_button)

            button_pos_x += new_button.rect.width - 4
