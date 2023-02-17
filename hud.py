import json
import os
import time
from structures import *
from cursor import Ghost
from algorithms import detect_surrounded_tiles
from graphics import zoom


class Statistics:
    def __init__(self):
        self.rect = None
        self.font_size = 20
        self.font = pg.font.Font('assets/Minecraft.otf', self.font_size)
        self.stat_window = pg.Surface((self.font_size * 20, self.font_size * 10))
        self.stat_window.fill((0, 0, 0))
        self.stat_scene = pg.Surface((self.font_size * 20, self.font_size * 10))
        self.stat_scene.fill((255, 255, 255))
        self.stat_height = self.font_size + 4
        self.screen_part = ""
        self.curr_coords = []

    def blit_stat(self, stat):
        stat_surf = self.font.render(stat, False, (255, 255, 255), (0, 0, 0))
        if self.screen_part == "topleft":
            stat_rect = stat_surf.get_rect(topleft=self.curr_coords)
        elif self.screen_part == "topright":
            stat_rect = stat_surf.get_rect(topright=self.curr_coords)
        elif self.screen_part == "bottomleft":
            stat_rect = stat_surf.get_rect(bottomleft=self.curr_coords)
        elif self.screen_part == "bottomright":
            stat_rect = stat_surf.get_rect(bottomright=self.curr_coords)
        else:
            stat_rect = stat_surf.get_rect(topleft=self.curr_coords)

        self.stat_window.blit(stat_surf, stat_rect)
        layer = pg.Surface((stat_rect.width + 8, stat_rect.height + 6))
        layer.fill((0, 0, 0))
        self.stat_scene.blit(layer, (stat_rect.x - 5, stat_rect.y - 3))
        if self.screen_part in {"topleft", "topright"}:
            self.curr_coords[1] += self.stat_height
        else:
            self.curr_coords[1] -= self.stat_height

    def print_stats(self, gw):
        self.stat_window.set_colorkey((0, 0, 0), RLEACCEL)
        self.stat_scene.set_colorkey((255, 255, 255), RLEACCEL)
        self.stat_scene.set_alpha(48)

        gw.screen.blit(self.stat_scene, self.rect)
        gw.screen.blit(self.stat_window, self.rect)


class GlobalStatistics(Statistics):
    def __init__(self, gw):
        super().__init__()
        self.rect = self.stat_window.get_rect(bottomleft=(0, gw.WINDOW_HEIGHT))
        self.screen_part = "bottomleft"
        self.curr_coords = [4, gw.WINDOW_HEIGHT - 4]

    def update_global_stats(self, gw):
        self.stat_window.fill((0, 0, 0))
        self.stat_scene.fill((255, 255, 255))
        self.curr_coords = [4, self.stat_window.get_height() - 4]

        self.blit_stat(
            "Time: " + str(gw.time_manager.time[0]) + ":00, Day " + str(gw.time_manager.time[1] + 1) + ", Week " + str(
                gw.time_manager.time[2] + 1))
        self.blit_stat("Gold: " + str(gw.time_manager.gold) + "g")
        self.blit_stat("TPS: " + str("{:.2f}".format(1 / gw.time_manager.elapsed * gw.TICK_RATE)))
        self.blit_stat("Weekly Tribute: " + str(gw.time_manager.tribute) + "g")

        self.print_stats(gw)


class TileStatistics(Statistics):
    def __init__(self, gw):
        super().__init__()
        self.rect = self.stat_window.get_rect(bottomright=(gw.WINDOW_WIDTH, gw.WINDOW_HEIGHT))
        self.screen_part = "bottomright"
        self.curr_coords = [self.stat_window.get_width() - 4, self.stat_window.get_height() - 4]

    def update_tile_stats(self, xy, gw):
        self.stat_window.fill((0, 0, 0))
        self.stat_scene.fill((255, 255, 255))
        self.curr_coords = [self.stat_window.get_width() - 4, self.stat_window.get_height() - 4]

        if isinstance(gw.struct_map[xy[0]][xy[1]], Structure):
            self.blit_stat(
                "time left: " + str("{:.2f}".format(gw.struct_map[xy[0]][xy[1]].time_left / gw.TICK_RATE)) + "s")
            self.blit_stat("cooldown: " + str(gw.struct_map[xy[0]][xy[1]].cooldown / gw.TICK_RATE) + "s")
            self.blit_stat("profit: " + str(gw.struct_map[xy[0]][xy[1]].profit) + "g")
            self.blit_stat("inside: " + str(gw.struct_map[xy[0]][xy[1]].inside))
            self.blit_stat(str(type(gw.struct_map[xy[0]][xy[1]]))[16:-2])
        self.blit_stat(gw.tile_type_map[xy[0]][xy[1]])
        self.blit_stat(str(xy))

        self.print_stats(gw)


class Button:
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
        self.is_held_down = False
        self.is_locked = False

    def hovered(self, gw):
        gw.screen.blit(self.hover_surf, self.rect)
        if self.is_held_down:
            gw.screen.blit(self.press_surf, self.rect)

    def play_hover_sound(self, gw):
        if self.sound == "woodrollover":
            gw.sounds["woodrollover" + str(randint(1, 4))].play()
        if self.sound == "metrollover":
            gw.sounds["metrollover" + str(randint(1, 6))].play()

    def press(self, gw, *args):
        return self.function(gw, self, self.value, *args)


class ButtonHandler:
    def __init__(self, gw):
        self.held_button = None
        self.hovered_button = None
        self.previous_button = None

    def handle_button_press(self, gw, event):
        press_result = None
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if self.hovered_button is not None:
                self.hovered_button.is_held_down = True
                self.held_button = self.hovered_button
                gw.sounds["woodpush"].play()
        if event.type == pg.MOUSEBUTTONUP and event.button == 1:
            if self.held_button is not None:
                if not self.held_button.is_locked:
                    self.held_button.is_held_down = False
                if self.hovered_button is self.held_button:
                    press_result = self.hovered_button.press(gw)
            self.held_button = None
        return press_result

    def handle_hovered_buttons(self, gw, active_buttons):
        self.hovered_button = None
        for button in active_buttons:
            if button.rect.collidepoint(pg.mouse.get_pos()):
                self.hovered_button = button
                button.hovered(gw)
            if button.is_held_down:
                button.hovered(gw)

        if gw.button_handler.hovered_button is not None and \
                ((gw.button_handler.previous_button is not None and
                  gw.button_handler.previous_button.id != gw.button_handler.hovered_button.id) or
                 gw.button_handler.previous_button is None):
            gw.button_handler.hovered_button.play_hover_sound(gw)

        gw.button_handler.previous_button = gw.button_handler.hovered_button


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

    def fill_dicts(self, button_names, icon_names, icon_scale=4):
        for type, names, curr_dict, scale in zip(("button_", "icon_"),
                                                 (button_names, icon_names),
                                                 (self.button_dict, self.icon_dict),
                                                 (4, icon_scale)):
            for name in names:
                curr_dict[name] = pg.image.load(
                    "assets/hud/" + type + name + ".png").convert()
                curr_dict[name] = pg.transform.scale(curr_dict[name], (
                    curr_dict[name].get_width() * scale, curr_dict[name].get_height() * scale))
                curr_dict[name].set_colorkey((255, 255, 255))


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
        self.draw("Time: " + str(gw.time_manager.time[0]) + ":00, Day " + str(gw.time_manager.time[1] + 1)
                  + ", Week " + str(gw.time_manager.time[2] + 1))
        self.draw("Gold: " + str(gw.time_manager.gold) + "g")
        self.draw("TPS: " + str("{:.2f}".format(1 / gw.time_manager.elapsed * gw.TICK_RATE)))
        self.draw("Weekly Tribute: " + str(gw.time_manager.tribute) + "g")
        gw.screen.blit(self.surf, self.rect)
        self.rightmost = 12


class PauseMenu(HUD):
    def __init__(self, gw):
        super().__init__(gw)
        self.font = pg.font.Font('assets/Minecraft.otf', 40)
        self.font_small = pg.font.Font('assets/Minecraft.otf', 20)

        self.button_functions = {"Resume": self.resume, "Save": self.save, "Load": self.load,
                                 "Options": self.options, "Quit": self.quit}
        self.buttons = set()
        with open("saves/save_dates.json", "r") as f:
            self.dates = json.load(f)
        # self.dates = ["Empty slot"] * 5
        self.surf = pg.transform.scale(pg.image.load("assets/hud/pause_menu.png").convert(), (64 * 4, 88 * 4))
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)

        self.surf_raw = self.surf.copy()

        self.rect = self.surf.get_rect(center=(gw.WINDOW_WIDTH / 2, gw.WINDOW_HEIGHT / 2))
        self.save = True
        self.is_menu_open = True
        self.fill_dicts(("wide", "wide_hover", "wide_thin", "wide_thin_hover", "round_square", "round_square_hover"),
                        ("delete", "save", "back", "load"))

        self.load_pause_menu(gw)

    def load_pause_menu(self, gw, *args):
        self.surf = self.surf_raw.copy()
        self.buttons.clear()

        for h, (button_name, method) in enumerate(self.button_functions.items()):
            text_surf = self.font.render(button_name, False, (62, 61, 58), (255, 255, 255))
            text_surf.set_colorkey((255, 255, 255))
            self.make_button(text_surf, (40, 28 + (self.button_dict["wide"].get_height() + 4) * h),
                             method, None, "wide", "wide_hover", h, 4)
        gw.screen.blit(self.surf, self.rect)

        return True, True

    def run_pause_menu_loop(self, gw, *args):

        self.load_pause_menu(gw)
        self.is_menu_open = True

        while self.is_menu_open:
            gw.screen.blit(gw.hud.pause_menu.surf, gw.hud.pause_menu.rect)
            gw.button_handler.hovered_button = None
            gw.button_handler.handle_hovered_buttons(gw, gw.hud.pause_menu.buttons)

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.is_menu_open = False
                    gw.running = False
                    return
                if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    gw.buttons.difference_update(gw.hud.pause_menu.buttons)
                    self.is_menu_open = False
                    return
                gw.button_handler.handle_button_press(gw, event)

            pg.display.flip()

    def load_savefile_menu(self, gw):
        def savefile_choose(gw, button, value):
            def load_from_slot(gw, button, value):
                if gw.hud.pause_menu.dates[value] != "Empty slot":
                    with open("saves/savefile" + str(value) + ".json", "r") as f:
                        gw.from_json(json.load(f))
                        detect_surrounded_tiles(gw)
                        zoom(gw, None, 1)
                        gw.hud.is_build_menu_open = False
                        gw.buttons.difference_update(gw.hud.build_menu.buttons)
                    self.is_menu_open = False

            def save_to_slot(gw, button, value):
                gw.hud.pause_menu.dates[value] = time.strftime("%H:%M %d-%m-%y")
                gw.hud.pause_menu.buttons.remove(button)
                text_surf = self.font_small.render(gw.hud.pause_menu.dates[value], False, (62, 61, 58), (255, 255, 255))
                text_surf.set_colorkey((255, 255, 255))
                gw.hud.pause_menu.make_button(text_surf,
                                              (40, 28 + (self.button_dict["wide_thin"].get_height() + 4) * value),
                                              savefile_choose, value, "wide_thin", "wide_thin_hover")
                with open("saves/savefile" + str(value) + ".json", "w+") as f:
                    json.dump(gw.to_json(), f, indent=2)
                with open("saves/save_dates.json", "w+") as f:
                    json.dump(gw.hud.pause_menu.dates, f)
                self.load_savefile_menu(gw)
                return True, True

            def del_save(gw, button, value):
                gw.hud.pause_menu.dates[value] = "Empty slot"
                with open("saves/save_dates.json", "w+") as f:
                    json.dump(gw.hud.pause_menu.dates, f)
                try:
                    os.remove("saves/savefile" + str(value) + ".json")
                except:
                    pass
                self.load_savefile_menu(gw)

                return True, True

            self.load_savefile_menu(gw)
            if gw.hud.pause_menu.dates[value] != "Empty slot":
                self.make_button(self.icon_dict["delete"], (40, 268), del_save, value,
                                 "round_square", "round_square_hover", 5)
            if self.save:
                self.make_button(self.icon_dict["save"], (100, 268), save_to_slot, value,
                                 "round_square", "round_square_hover", 6)
            elif gw.hud.pause_menu.dates[value] != "Empty slot":
                self.make_button(self.icon_dict["load"], (100, 268), load_from_slot, value,
                                 "round_square", "round_square_hover", 7)

            for any_button in gw.hud.pause_menu.buttons:
                if any_button.id == button.id:
                    any_button.is_held_down = True
                    any_button.is_locked = True
                else:
                    any_button.is_held_down = False
                    any_button.is_locked = False
            # button.hold = True
            return True, True

        gw.buttons.difference_update(self.buttons)
        self.buttons.clear()
        self.surf.blit(self.surf_raw, (0, 0))
        for h in range(5):
            text_surf = self.font_small.render(self.dates[h], False, (62, 61, 58), (255, 255, 255))
            text_surf.set_colorkey((255, 255, 255))
            self.make_button(text_surf, (40, 28 + (self.button_dict["wide_thin"].get_height() + 4) * h),
                             savefile_choose, h, "wide_thin", "wide_thin_hover", h)
        self.make_button(self.icon_dict["back"], (160, 268), self.load_pause_menu, 0,
                         "round_square", "round_square_hover")

    def resume(self, *args):
        self.is_menu_open = False

    def save(self, gw, *args):
        self.save = True
        self.load_savefile_menu(gw)

    def load(self, gw, *args):
        self.save = False
        self.load_savefile_menu(gw)

    def options(self, *args):
        pass

    def quit(self, gw, *args):
        self.is_menu_open = False
        gw.running = False


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
        self.visible_area.fill((198, 15, 24))
        cutout = pg.surface.Surface((self.visible_area.get_width() - 4, self.visible_area.get_height() - 4))
        cutout.fill((0, 0, 0))
        self.visible_area.blit(cutout, (2, 2))
        self.visible_area.set_colorkey((0, 0, 0), RLEACCEL)

    def update_minimap(self, gw):
        self.surf.blit(self.surf_raw, (0, 0))
        self.surf.blit(self.visible_area, ((gw.scene.rect.x / gw.tile_s) * (128 / gw.width_tiles),
                                           (gw.scene.rect.y / gw.tile_s) * (128 / gw.height_tiles)))
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

        self.fill_dicts(("tile", "tile_hover", "tile_big", "tile_big_hover", "round_small", "round_small_hover"),
                        ("housing", "military", "transport", "manufacturing", "agriculture", "religion"), 2)
        self.rect = self.surf.get_rect(centerx=gw.WINDOW_WIDTH // 2, top=44)
        self.category_dict = {"housing": (House,), "military": (Wall, Gate, Tower), "religion": (),
                              "transport": (Road,), "manufacturing": (Sawmill, Mine, Pyramid),
                              "agriculture": (Tree, Farmland)}
        self.structure_buttons = set()
        self.is_build_menu_open = True

        self.load_menu(gw)

    def load_menu(self, gw, manual_open=False):
        self.surf.blit(self.surf_raw, (0, 0))
        gw.buttons.difference_update(self.buttons)
        self.buttons.clear()

        for i, (category, icon) in enumerate(self.icon_dict.items()):
            curr_button = self.make_button(icon, (52 + (i % 2) * 36, 4 + (i // 2) * 36), self.open_category,
                                           category, "round_small", "round_small_hover",
                                           i, sound="metrollover")
            if i == 0 and not manual_open:
                self.open_category(gw, curr_button, category)

        gw.buttons.update(self.buttons)

    def toggle_build_menu(self, gw, *args):
        if self.is_build_menu_open:
            gw.buttons.difference_update(gw.hud.build_menu.buttons)
            self.buttons.clear()
        else:
            self.load_menu(gw)
        self.is_build_menu_open = not self.is_build_menu_open

    def open_category(self, gw, button, value):
        self.load_menu(gw, True)
        gw.buttons.difference_update(self.structure_buttons)
        self.buttons.difference_update(self.structure_buttons)
        self.structure_buttons.clear()

        curr_button_pos_left = 136
        for i, building in enumerate(self.category_dict[value]):
            new_build = building([0, 0], gw)
            height = 120 - 60 * new_build.surf_ratio[1]
            if new_build.surf_ratio[0] <= 1:
                button_tile, button_tile_hover = "tile", "tile_hover"
            else:
                button_tile, button_tile_hover = "tile_big", "tile_big_hover"
            curr_button = self.make_button(
                pg.transform.scale(new_build.surf, (60 * new_build.surf_ratio[0], 60 * new_build.surf_ratio[1])),
                (curr_button_pos_left, 0), self.assign, type(new_build),
                button_tile, button_tile_hover, -i - 1, 4 + height)
            self.structure_buttons.add(curr_button)
            if new_build.surf_ratio[0] <= 1:
                curr_button_pos_left += 88
            else:
                curr_button_pos_left += 148

        for any_button in self.buttons:
            if any_button.id == button.id:
                any_button.is_held_down = True
                any_button.is_locked = True
            else:
                any_button.is_held_down = False
                any_button.is_locked = False

        gw.buttons.update(self.buttons)

    def assign(self, gw, button, struct_type):
        gw.cursor.change_mode(gw, None, "demolish", "off")
        gw.cursor.held_structure = struct_type([0, 0], gw)
        gw.cursor.ghost = Ghost(gw)
        if struct_type in {Farmland, Road, Wall}:
            gw.cursor.change_mode(gw, None, "drag_build", "on")
        else:
            gw.cursor.change_mode(gw, None, "drag_build", "off")


class Toolbar(HUD):
    def __init__(self, gw, hud):
        super().__init__(gw)
        self.surf = pg.transform.scale(pg.image.load("assets/hud/toolbar.png").convert(), (108, 300))
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.surf_raw = self.surf.copy()

        self.fill_dicts(("round_square", "round_square_hover", "round_small", "round_small_hover"),
                        ("zoom_in", "zoom_out", "drag", "debug"), 2)
        self.fill_dicts((), ("build", "demolish", "pause"))
        self.small_button_functions = {"zoom_in": zoom, "zoom_out": zoom, "drag": gw.cursor.change_mode,
                                       "debug": self.foo}
        self.big_button_functions = {"build": hud.build_menu.toggle_build_menu,
                                     "demolish": gw.cursor.change_mode,
                                     "pause": hud.pause_menu.run_pause_menu_loop}

        self.rect = self.surf.get_rect(right=gw.WINDOW_WIDTH, top=184)

        self.demolish_button = None
        self.drag_build_button = None

        self.load_toolbar(gw)

    def load_toolbar(self, gw):
        self.surf.blit(self.surf_raw, (0, 0))
        gw.buttons.difference_update(self.buttons)
        self.buttons.clear()

        for i, (icon, function) in enumerate(self.small_button_functions.items()):
            new_button = self.make_button(self.icon_dict[icon], (32 + (i % 2) * 40, 4 + (i // 2) * 40),
                                          function, (2, 0.5, "drag_build", None)[i], "round_small", "round_small_hover",
                                          sound="metrollover")
            if icon == "drag":
                self.drag_build_button = new_button

        for i, (icon, function) in enumerate(self.big_button_functions.items()):
            new_button = self.make_button(self.icon_dict[icon], (40, 88 + (i * 64)),
                                          function, (None, "demolish", None)[i], "round_square", "round_square_hover")
            if icon == "demolish":
                self.demolish_button = new_button

        gw.buttons.update(self.buttons)

    def foo(self, *args):
        pass
