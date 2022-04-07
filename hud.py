import pygame as pg
import time
import json
import os
from pygame.locals import RLEACCEL
from classes import Ghost

class Button(pg.sprite.Sprite):
    def __init__(self, rect, function, value=None, hover_surf=pg.Surface((0, 0)), press_surf=pg.Surface((0, 0)), id=-1):
        super().__init__()
        self.id = id
        self.rect = rect
        self.hover_surf = hover_surf
        self.hover_surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.press_surf = press_surf
        self.press_surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.function = function
        self.value = value
        self.hold = False

    def hovered(self, gw):
        gw.screen.blit(self.hover_surf, self.rect)

    def pressed(self, gw):
        gw.screen.blit(self.press_surf, self.rect)

    def press(self, gw, args):
        return self.function(gw, self, self.value, args)


class HUD:
    def __init__(self, gw):
        self.surf = pg.surface.Surface((0, 0))
        self.buttons = set()
        self.rect = self.surf.get_rect()
        self.button_dict = {}

    def make_button(self, contents_surf, button_topleft, method, value, button_key,
                    button_hover_key, id=-1, contents_height=4):
        button_surf = self.button_dict[button_key].copy()

        contents_rect = contents_surf.get_rect(centerx=button_surf.get_width() / 2, top=contents_height)
        button_surf.blit(contents_surf, contents_rect)
        button_rect = button_surf.get_rect(topleft=button_topleft)

        self.surf.blit(button_surf, button_rect)
        hover_surf = self.button_dict[button_hover_key].copy()
        hover_surf.blit(contents_surf, (contents_rect.x, contents_rect.y + 4))
        self.buttons.add(Button(button_rect.move(self.rect.x, self.rect.y), method, value, hover_surf, hover_surf, id))


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
        self.draw("Time: " + str(gw.global_statistics.time[0]) + ":00, Day " + str(gw.global_statistics.time[1] + 1)
                  + ", Week " + str(gw.global_statistics.time[2] + 1))
        self.draw("Gold: " + str(gw.vault.gold) + "g")
        self.draw("TPS: " + str("{:.2f}".format(1 / gw.global_statistics.elapsed * gw.TICK_RATE)))
        self.draw("Weekly Tribute: " + str(gw.global_statistics.tribute) + "g")
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
        for type, names, curr_dict in zip(("button_", "icon_"),
                                          (("", "hover", "small", "small_hover", "square", "square_hover"),
                                           ("delete", "save", "back", "load")),
                                          (self.button_dict, self.icon_dict)):
            for name in names:
                curr_dict[type + name] = pg.image.load("assets/hud/pause_menu_" + type + name + ".png").convert()
                curr_dict[type + name] = pg.transform.scale(curr_dict[type + name], (
                    curr_dict[type + name].get_width() * 4, curr_dict[type + name].get_height() * 4))
                curr_dict[type + name].set_colorkey((255, 255, 255))

        self.load_menu(gw)

    def load_menu(self, gw, button=None, value=None, press_hold=None):
        self.surf = self.surf_raw.copy()
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.buttons = set()

        for h, (button_name, method) in enumerate(self.button_properties):
            text_surf = self.font.render(button_name, False, (62, 61, 58), (255, 255, 255))
            text_surf.set_colorkey((255, 255, 255))
            self.make_button(text_surf, (40, 28 + (self.button_dict["button_"].get_height() + 4) * h),
                             method, None, "button_", "button_hover", h)
        gw.screen.blit(self.surf, self.rect)

        return True, True, -1

    def load_savefile_menu(self, gw):
        def savefile_choose(gw, button, value, pause_menu):
            def load_from_slot(gw, button, value, pause_menu):
                if pause_menu.dates[value] != "Empty slot":
                    return False, True, value
                else:
                    return True, True, -1

            def save_to_slot(gw, button, value, pause_menu):
                pause_menu.dates[value] = time.strftime("%H:%M %d-%m-%y")
                pause_menu.buttons.remove(button)
                text_surf = self.font_small.render(pause_menu.dates[value], False, (62, 61, 58), (255, 255, 255))
                text_surf.set_colorkey((255, 255, 255))
                pause_menu.make_button(text_surf,
                                       (40, 28 + (self.button_dict["button_small"].get_height() + 4) * value),
                                       savefile_choose, value, "button_small", "button_small_hover")
                with open("saves/savefile" + str(value) + ".json", "w+") as f:
                    json.dump(gw.to_json(), f, indent=2)
                with open("saves/save_dates.json", "w+") as f:
                    json.dump(pause_menu.dates, f)
                self.load_savefile_menu(gw)
                return True, True, -1

            def del_save(gw, button, value, pause_menu):
                pause_menu.dates[value] = "Empty slot"
                os.remove("saves/savefile" + str(value) + ".json")
                self.load_savefile_menu(gw)

                return True, True, -1

            self.load_savefile_menu(gw)
            if pause_menu.dates[value] != "Empty slot":
                self.make_button(self.icon_dict["icon_delete"], (40, 268), del_save, value,
                                 "button_square", "button_square_hover", 5)
            if self.save:
                self.make_button(self.icon_dict["icon_save"], (100, 268), save_to_slot, value,
                                 "button_square", "button_square_hover", 6)
            elif pause_menu.dates[value] != "Empty slot":
                self.make_button(self.icon_dict["icon_load"], (100, 268), load_from_slot, value,
                                 "button_square", "button_square_hover", 7)

            for any_button in pause_menu.buttons:
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

    def resume(self, gw, button, value, press_hold):
        return False, True, -1

    def save(self, gw, button, value, press_hold):
        self.save = True
        self.load_savefile_menu(gw)
        return True, True, -1

    def load(self, gw, button, value, glob_stats):
        self.save = False
        self.load_savefile_menu(gw)
        return True, True, -1

    def options(self, gw, button, value, press_hold):
        return True, True, -1

    def quit(self, gw, button, value, press_hold):
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
        self.surf = pg.Surface((76 + len(gw.key_structure_dict.values()) * 104, 136))
        self.surf.fill((255, 255, 255))
        self.button_dict = \
            {"tile_hover": pg.transform.scale(pg.image.load("assets/hud/hud_tile_horiz_hover.png").convert(),
                                              (108, 120)),
             "tile_press": pg.transform.scale(pg.image.load("assets/hud/hud_tile_horiz_press.png").convert(),
                                              (108, 120)),
             "tile": pg.transform.scale(pg.image.load("assets/hud/hud_tile_horiz.png").convert(), (108, 120))}
        self.rect = self.surf.get_rect(centerx=gw.WINDOW_WIDTH / 2, top=44)
        self.surf.blit(pg.transform.scale(pg.image.load("assets/hud/hud_edge_horiz.png").convert(), (36, 136)), (0, 0))
        lowest = 0

        for i, building in enumerate(gw.key_structure_dict.values()):
            new_build = building([0, 0], gw)
            height = 100 - 60 * new_build.surf_ratio[1]
            self.make_button(pg.transform.scale(new_build.surf, (60, 60 * new_build.surf_ratio[1])), (36 + i * 104, 0),
                             self.assign, type(new_build), "tile", "tile_hover", i, 4 + height)
            lowest = i

        self.surf.blit(pg.transform.flip(pg.transform.scale(pg.image.load("assets/hud/hud_edge_horiz.png").convert(),
                                                            (36, 136)), True, False), (144 + lowest * 104, 0))
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.collide_rect = pg.Rect(self.rect.left + 4, 0, self.rect.width - 8, self.rect.height - 16)
        gw.buttons.update(self.buttons)

    def assign(self, gw, button, value, press_hold):
        if not press_hold:
            gw.cursor.hold = value([0, 0], gw)
            gw.cursor.ghost = Ghost(gw)
            gw.sounds["woodpush2"].play()

