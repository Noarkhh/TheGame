import pygame as pg
import time
import json
import os
from pygame.locals import RLEACCEL
from classes import *
from functions import detect_surrounded_tiles, zoom


class Button(pg.sprite.Sprite):
    def __init__(self, rect, function, value=None, hover_surf=pg.Surface((0, 0)), press_surf=pg.Surface((0, 0)), id=-1,
                 sound="woodrollover"):
        super().__init__()
        self.id = id
        self.rect = rect
        self.hover_surf = hover_surf
        self.hover_surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.press_surf = press_surf
        self.press_surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.function = function
        self.value = value
        self.sound = sound
        self.hold = False

    def hovered(self, gw):
        gw.screen.blit(self.hover_surf, self.rect)

    def pressed(self, gw):
        gw.screen.blit(self.press_surf, self.rect)

    def play_hover_sound(self, gw):
        if self.sound == "woodrollover":
            gw.sounds["woodrollover" + str(randint(2, 5))].play()
        if self.sound == "metrollover":
            gw.sounds["metrollover" + str(randint(2, 7))].play()

    def press(self, gw, *args):
        return self.function(gw, self, self.value, *args)


class HUD:
    def __init__(self, gw):
        self.surf = pg.surface.Surface((0, 0))
        self.buttons = set()
        self.rect = self.surf.get_rect()
        self.button_dict = {}
        self.icon_dict = {}

    def make_button(self, contents_surf, button_topleft, method, value, button_key,
                    button_hover_key, id=-1, contents_height=4, sound="woodrollover"):
        button_surf = self.button_dict[button_key].copy()

        contents_rect = contents_surf.get_rect(centerx=button_surf.get_width() / 2, top=contents_height)
        button_surf.blit(contents_surf, contents_rect)
        button_rect = button_surf.get_rect(topleft=button_topleft)

        self.surf.blit(button_surf, button_rect)
        hover_surf = self.button_dict[button_hover_key].copy()
        hover_surf.blit(contents_surf, (contents_rect.x, contents_rect.y + 4))
        button = Button(button_rect.move(self.rect.x, self.rect.y), method, value, hover_surf, hover_surf, id, sound)
        self.buttons.add(button)
        return button

    def fill_dicts(self, button_names, icon_names, hud_type, icon_scale=4):
        for type, names, curr_dict, scale in zip(("button_", "icon_"),
                                                 (button_names, icon_names),
                                                 (self.button_dict, self.icon_dict),
                                                 (4, icon_scale)):
            for name in names:
                curr_dict[type + name] = pg.image.load(
                    "assets/hud/" + hud_type + "_" + type + name + ".png").convert()
                curr_dict[type + name] = pg.transform.scale(curr_dict[type + name], (
                    curr_dict[type + name].get_width() * scale, curr_dict[type + name].get_height() * scale))
                curr_dict[type + name].set_colorkey((255, 255, 255))


class TopBar(HUD):
    def __init__(self, gw):
        super().__init__(gw)
        self.font_size = 20
        self.font = pg.font.Font('assets/Minecraft.otf', self.font_size)
        self.surf = pg.surface.Surface((gw.WINDOW_WIDTH, 44))
        self.rect = self.surf.get_rect()
        self.bar_segment = pg.transform.scale(pg.image.load("assets/hud/main_bar_segment.png"), (4 * 27, 44))
        self.rightmost = 12
        curr_pos = 0
        while curr_pos < gw.WINDOW_WIDTH:
            self.surf.blit(self.bar_segment, (curr_pos, 0))
            curr_pos += 4 * 27
        self.surf_raw = self.surf.copy()

    def draw(self, text):
        text_surf = self.font.render(text, False, (62, 61, 58), (255, 255, 255))
        text_surf.set_colorkey((255, 255, 255))
        self.surf.blit(text_surf, (self.rightmost, 8))
        self.rightmost += text_surf.get_width() + 20

    def update(self, gw):
        self.surf.blit(self.surf_raw, (0, 0))
        self.draw("Time: " + str(gw.reality.time[0]) + ":00, Day " + str(gw.reality.time[1] + 1)
                  + ", Week " + str(gw.reality.time[2] + 1))
        self.draw("Gold: " + str(gw.reality.gold) + "g")
        self.draw("TPS: " + str("{:.2f}".format(1 / gw.reality.elapsed * gw.TICK_RATE)))
        self.draw("Weekly Tribute: " + str(gw.reality.tribute) + "g")
        gw.screen.blit(self.surf, self.rect)
        self.rightmost = 12


class PauseMenu(HUD):
    def __init__(self, gw):
        super().__init__(gw)
        self.font = pg.font.Font('assets/Minecraft.otf', 40)
        self.font_small = pg.font.Font('assets/Minecraft.otf', 20)

        self.button_properties = [("Resume", self.resume), ("Save", self.save), ("Load", self.load),
                                  ("Options", self.options), ("Quit", self.quit)]
        self.buttons = set()
        with open("saves/save_dates.json", "r") as f:
            self.dates = json.load(f)
        # self.dates = ["Empty slot"] * 5
        self.surf = pg.transform.scale(pg.image.load("assets/hud/pause_menu.png").convert(), (64 * 4, 88 * 4))
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)

        self.surf_raw = self.surf.copy()

        self.rect = self.surf.get_rect(center=(gw.WINDOW_WIDTH / 2, gw.WINDOW_HEIGHT / 2))
        self.button_dict = {}
        self.icon_dict = {}
        self.save = True
        self.fill_dicts(("", "hover", "small", "small_hover", "square", "square_hover"),
                        ("delete", "save", "back", "load"), "pause_menu")

        self.load_menu(gw)

    def load_menu(self, gw, button=None, value=None, press_hold=None):
        self.surf = self.surf_raw.copy()
        self.buttons = set()

        for h, (button_name, method) in enumerate(self.button_properties):
            text_surf = self.font.render(button_name, False, (62, 61, 58), (255, 255, 255))
            text_surf.set_colorkey((255, 255, 255))
            self.make_button(text_surf, (40, 28 + (self.button_dict["button_"].get_height() + 4) * h),
                             method, None, "button_", "button_hover", h)
        gw.screen.blit(self.surf, self.rect)

        return True, True, -1

    def load_savefile_menu(self, gw):
        def savefile_choose(gw, button, value):
            def load_from_slot(gw, button, value):
                if gw.hud.pause_menu.dates[value] != "Empty slot":
                    with open("saves/savefile" + str(value) + ".json", "r") as f:
                        gw.from_json(json.load(f))
                        detect_surrounded_tiles(gw)
                        zoom(gw, 1)
                    return False, True, value
                else:
                    return True, True, -1

            def save_to_slot(gw, button, value):
                gw.hud.pause_menu.dates[value] = time.strftime("%H:%M %d-%m-%y")
                gw.hud.pause_menu.buttons.remove(button)
                text_surf = self.font_small.render(gw.hud.pause_menu.dates[value], False, (62, 61, 58), (255, 255, 255))
                text_surf.set_colorkey((255, 255, 255))
                gw.hud.pause_menu.make_button(text_surf,
                                              (40, 28 + (self.button_dict["button_small"].get_height() + 4) * value),
                                              savefile_choose, value, "button_small", "button_small_hover")
                with open("saves/savefile" + str(value) + ".json", "w+") as f:
                    json.dump(gw.to_json(), f, indent=2)
                with open("saves/save_dates.json", "w+") as f:
                    json.dump(gw.hud.pause_menu.dates, f)
                self.load_savefile_menu(gw)
                return True, True, -1

            def del_save(gw, button, value):
                gw.hud.pause_menu.dates[value] = "Empty slot"
                with open("saves/save_dates.json", "w+") as f:
                    json.dump(gw.hud.pause_menu.dates, f)
                try:
                    os.remove("saves/savefile" + str(value) + ".json")
                except:
                    pass
                self.load_savefile_menu(gw)

                return True, True, -1

            self.load_savefile_menu(gw)
            if gw.hud.pause_menu.dates[value] != "Empty slot":
                self.make_button(self.icon_dict["icon_delete"], (40, 268), del_save, value,
                                 "button_square", "button_square_hover", 5)
            if self.save:
                self.make_button(self.icon_dict["icon_save"], (100, 268), save_to_slot, value,
                                 "button_square", "button_square_hover", 6)
            elif gw.hud.pause_menu.dates[value] != "Empty slot":
                self.make_button(self.icon_dict["icon_load"], (100, 268), load_from_slot, value,
                                 "button_square", "button_square_hover", 7)

            for any_button in gw.hud.pause_menu.buttons:
                if any_button.id == button.id:
                    any_button.hold = True
                else:
                    any_button.hold = False
            # button.hold = True
            return True, True, -1

        gw.buttons.difference_update(self.buttons)
        self.buttons = set()
        self.surf.blit(self.surf_raw, (0, 0))
        for h in range(5):
            text_surf = self.font_small.render(self.dates[h], False, (62, 61, 58), (255, 255, 255))
            text_surf.set_colorkey((255, 255, 255))
            self.make_button(text_surf, (40, 28 + (self.button_dict["button_small"].get_height() + 4) * h),
                             savefile_choose, h, "button_small", "button_small_hover", h)
        self.make_button(self.icon_dict["icon_back"], (160, 268), self.load_menu, 0,
                         "button_square", "button_square_hover")

    def resume(self, gw, button, value):
        return False, True, -1

    def save(self, gw, button, value):
        self.save = True
        self.load_savefile_menu(gw)
        return True, True, -1

    def load(self, gw, button, value):
        self.save = False
        self.load_savefile_menu(gw)
        return True, True, -1

    def options(self, gw, button, value):
        return True, True, -1

    def quit(self, gw, button, value):
        return False, False, -1


class Minimap(HUD):
    def __init__(self, gw):
        super().__init__(gw)
        self.frame = pg.image.load("assets/hud/map_frame.png").convert()
        self.frame.set_colorkey((255, 255, 255), RLEACCEL)
        self.surf = pg.transform.scale(gw.layout.copy(), (128, 128))
        self.surf_raw = self.surf.copy()
        self.rect = self.surf.get_rect(topright=(gw.WINDOW_WIDTH, 44))
        self.visible_area = pg.surface.Surface(((gw.WINDOW_WIDTH / gw.tile_s) * (128 / gw.width_tiles),
                                                (gw.WINDOW_HEIGHT / gw.tile_s) * (128 / gw.height_tiles)))
        self.visible_area.fill((223, 17, 28))
        cutout = pg.surface.Surface((self.visible_area.get_width() - 4, self.visible_area.get_height() - 4))
        cutout.fill((0, 0, 0))
        self.visible_area.blit(cutout, (2, 2))
        self.visible_area.set_colorkey((0, 0, 0), RLEACCEL)

    def update_minimap(self, gw):
        self.surf.blit(self.surf_raw, (0, 0))
        self.surf.blit(self.visible_area, ((gw.background.rect.x / gw.tile_s) * (128 / gw.width_tiles),
                                           (gw.background.rect.y / gw.tile_s) * (128 / gw.height_tiles)))
        gw.screen.blit(self.surf, self.rect)
        gw.screen.blit(self.frame, (self.rect.x - 16, self.rect.y))

    def update_zoom(self, gw):
        self.visible_area = pg.surface.Surface(((gw.WINDOW_WIDTH / gw.tile_s) * (128 / gw.width_tiles),
                                                (gw.WINDOW_HEIGHT / gw.tile_s) * (128 / gw.height_tiles)))
        self.visible_area.fill((223, 17, 28))
        cutout = pg.surface.Surface((self.visible_area.get_width() - 4, self.visible_area.get_height() - 4))
        cutout.fill((0, 0, 0))
        self.visible_area.blit(cutout, (2, 2))
        self.visible_area.set_colorkey((0, 0, 0), RLEACCEL)


class BuildMenu(HUD):
    def __init__(self, gw):
        super().__init__(gw)
        self.surf = pg.transform.scale(pg.image.load("assets/hud/build_menu.png").convert(), (704, 156))
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)

        self.surf_raw = self.surf.copy()

        self.surf.fill((255, 255, 255))
        self.fill_dicts(("tile", "tile_hover", "tile_big", "tile_big_hover", "category", "category_hover"),
                        ("housing", "military", "transport", "manufacturing", "agriculture", "religion"), "build_menu", 2)
        self.rect = self.surf.get_rect(centerx=gw.WINDOW_WIDTH / 2, top=44)
        self.category_dict = {"housing": (House,), "military": (Wall, Gate, Tower), "religion": (),
                              "transport": (Road,), "manufacturing": (Sawmill, Mine, Pyramid), "agriculture": (Tree,)}
        self.build_buttons = set()

        self.collide_rect = pg.Rect(self.rect.left + 4, 0, self.rect.width - 8, self.rect.height - 16)

        self.load_menu(gw)

    def load_menu(self, gw, manual_open=False):
        self.surf.blit(self.surf_raw, (0, 0))
        gw.buttons.difference_update(self.buttons)
        self.buttons.clear()

        for i, (category, icon) in enumerate(self.icon_dict.items()):
            curr_button = self.make_button(icon, (52 + (i % 2) * 36, 4 + (i // 2) * 36), self.open_category,
                                           category[5:], "button_category", "button_category_hover", i,
                                           sound="metrollover")
            if i == 0 and not manual_open:
                self.open_category(gw, curr_button, category[5:], False, False)

        gw.buttons.update(self.buttons)

    def open_category(self, gw, button, value, press_hold, manual_open=True):
        if not press_hold:
            self.load_menu(gw, True)
            gw.buttons.difference_update(self.build_buttons)
            self.buttons.difference_update(self.build_buttons)

            curr_button_pos_left = 136
            for i, building in enumerate(self.category_dict[value]):
                new_build = building([0, 0], gw)
                height = 120 - 60 * new_build.surf_ratio[1]
                if new_build.surf_ratio[0] <= 1:
                    button_tile, button_tile_hover = "button_tile", "button_tile_hover"
                else:
                    button_tile, button_tile_hover = "button_tile_big", "button_tile_big_hover"
                curr_button = self.make_button(
                    pg.transform.scale(new_build.surf, (60 * new_build.surf_ratio[0], 60 * new_build.surf_ratio[1])),
                    (curr_button_pos_left, 0), self.assign, type(new_build),
                    button_tile, button_tile_hover, -i - 1, 4 + height)
                self.build_buttons.add(curr_button)
                if new_build.surf_ratio[0] <= 1:
                    curr_button_pos_left += 88
                else:
                    curr_button_pos_left += 148

            for any_button in self.buttons:
                if any_button.id == button.id:
                    any_button.hold = True
                else:
                    any_button.hold = False

            # print(button.value)
            # for gw_button in gw.buttons:
            #     print(gw_button.value)
            # print("\n\n")
            gw.buttons.update(self.buttons)
            if manual_open:
                gw.sounds["woodpush2"].play()

    def assign(self, gw, button, value, press_hold):
        if not press_hold:
            gw.cursor.hold = value([0, 0], gw)
            gw.cursor.ghost = Ghost(gw)
            gw.sounds["woodpush2"].play()
