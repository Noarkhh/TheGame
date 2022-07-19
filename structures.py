import pygame as pg
from random import randint
import time
from pygame.locals import RLEACCEL


class Scene(pg.sprite.Sprite):
    def __init__(self, gw):
        super().__init__()
        self.surf = pg.transform.scale(gw.map_surf.copy(), (gw.width_pixels, gw.height_pixels))
        self.surf_raw = self.surf.copy()
        self.surf_rendered = self.surf.subsurface((0, 0, gw.WINDOW_WIDTH, gw.WINDOW_HEIGHT))
        self.rect = self.surf_rendered.get_rect()

    def move_screen(self, gw):
        if not gw.MOUSE_STEERING:
            if gw.cursor.rect.right >= self.rect.right <= gw.width_pixels - gw.tile_s / 2:
                self.rect.move_ip(gw.tile_s / 2, 0)
            if gw.cursor.rect.left <= self.rect.left >= 0 + gw.tile_s / 2:
                self.rect.move_ip(-gw.tile_s / 2, 0)
            if gw.cursor.rect.bottom >= self.rect.bottom <= gw.height_pixels - gw.tile_s / 2:
                self.rect.move_ip(0, gw.tile_s / 2)
            if gw.cursor.rect.top <= self.rect.top >= 0 + gw.tile_s / 2:
                self.rect.move_ip(0, -gw.tile_s / 2)
        else:
            if pg.mouse.get_pos()[0] >= gw.WINDOW_WIDTH - gw.tile_s / 2 and \
                    self.rect.right <= gw.width_pixels - gw.tile_s / 2:
                self.rect.move_ip(gw.tile_s / 2, 0)
            if pg.mouse.get_pos()[0] <= 0 + gw.tile_s / 2 <= self.rect.left:
                self.rect.move_ip(-gw.tile_s / 2, 0)
            if pg.mouse.get_pos()[1] >= gw.WINDOW_HEIGHT - gw.tile_s / 2 and \
                    self.rect.bottom <= gw.height_pixels - gw.tile_s / 2:
                self.rect.move_ip(0, gw.tile_s / 2)
            if pg.mouse.get_pos()[1] <= 0 + gw.tile_s / 2 <= self.rect.top:
                self.rect.move_ip(0, -gw.tile_s / 2)
        self.surf_rendered = self.surf.subsurface(self.rect)


class Entities(pg.sprite.Group):
    def draw(self, scene):
        sprites = self.sprites()
        for spr in sorted(sprites, key=lambda spr: spr.pos[1]):
            if spr.rect.colliderect(scene.rect):
                scene.surf.blit(spr.surf, spr.rect)
        self.lostsprites = []


class TimeManager:
    def __init__(self, gw):
        self.time = 0
        self.tick = 0
        self.time = [0, 0, 0]
        self.elapsed = 1
        self.start = time.time()
        self.end = 0
        self.tribute = 40
        self.gold = gw.STARTING_GOLD

    def time_lapse(self, gw):
        self.tick += 1
        if self.tick >= gw.TICK_RATE:
            self.tick = 0
            self.time[0] += 1
            self.end = time.time()
            self.elapsed = self.end - self.start
            self.start = time.time()
            if self.time[0] >= 24:
                self.time[0] = 0
                self.time[1] += 1
                if self.time[1] >= 7:
                    self.time[1] = 0
                    self.time[2] += 1
                    gw.time_manager.gold -= self.tribute
                    gw.sounds["ignite_oil"].play()
                    self.tribute = int(self.tribute ** 1.2)

    def to_json(self):
        return {
            "time": self.time,
            "tribute": self.tribute
        }

    def from_json(self, json_dict):
        self.time = json_dict["time"]
        self.tribute = json_dict["tribute"]
        return self


class Cursor(pg.sprite.Sprite):
    def __init__(self, gw):
        super().__init__()
        self.is_in_demolish_mode = False
        self.is_in_drag_build_mode = False
        self.is_dragging = False
        self.is_lmb_held_down = False
        self.is_lmb_pressed = False

        self.surf = pg.transform.scale(pg.image.load("assets/cursor2.png").convert(), (gw.tile_s, gw.tile_s))
        self.surf_demolish = pg.transform.scale(pg.image.load("assets/cursor_demolish.png").convert(),
                                                (gw.tile_s, gw.tile_s))
        self.surf_demolish.set_alpha(128)

        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.surf_demolish.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.surf.get_rect()
        self.pos = [0, 0]
        self.previous_pos = [0, 0]
        self.drag_starting_pos = [0, 0]
        self.held_structure = None
        self.ghost = None

    def update(self, gw):
        self.previous_pos = self.pos.copy()
        self.pos[0] = (pg.mouse.get_pos()[0] + gw.scene.rect.x) // gw.tile_s
        self.pos[1] = (pg.mouse.get_pos()[1] + gw.scene.rect.y) // gw.tile_s
        self.rect.x = self.pos[0] * gw.tile_s
        self.rect.y = self.pos[1] * gw.tile_s

    def draw(self, gw):
        if self.is_in_demolish_mode:
            gw.scene.surf.blit(self.surf_demolish, self.rect)
        else:
            gw.scene.surf.blit(self.surf, self.rect)
        if self.held_structure is not None:
            self.ghost.update(gw)
            gw.scene.surf.blit(self.ghost.surf, self.ghost.rect)

    def change_mode(self, gw, button, mode, state="toggle"):
        if mode == "demolish":
            mode_button = gw.hud.toolbar.demolish_button
            mode_state = self.is_in_demolish_mode
        elif mode == "drag_build":
            mode_button = gw.hud.toolbar.drag_build_button
            mode_state = self.is_in_drag_build_mode
        else:
            return

        if state == "toggle":
            mode_state = not mode_state
        elif state == "on":
            mode_state = True
        elif state == "off":
            mode_state = False

        if mode_state:
            mode_button.is_locked = True
            mode_button.is_held_down = True
            if mode == "demolish":
                self.held_structure = None
        else:
            mode_button.is_locked = False
            mode_button.is_held_down = False

        if mode == "demolish":
            self.is_in_demolish_mode = mode_state
        if mode == "drag_build":
            self.is_in_drag_build_mode = mode_state

    def to_json(self):
        return {
            "pos": self.pos
        }


class Ghost:
    def __init__(self, gw):
        self.surf = gw.cursor.held_structure.surf
        self.surf.set_alpha(128)
        self.pos = gw.cursor.pos
        self.drag_starting_pos = gw.cursor.pos.copy()
        self.rect = self.surf.get_rect(bottomright=(gw.tile_s * (self.pos[0] + 1), gw.tile_s * (self.pos[1] + 1)))
        self.sides_to_draw = []

    def update(self, gw):
        self.pos = gw.cursor.pos
        if not gw.cursor.is_dragging:
            self.surf = gw.cursor.held_structure.surf
            self.rect = self.surf.get_rect(bottomright=(gw.tile_s * (self.pos[0] + 1), gw.tile_s * (self.pos[1] + 1)))

        else:
            self.surf = pg.Surface(((abs(self.pos[0] - self.drag_starting_pos[0]) + 1) * gw.tile_s,
                                    (abs(self.pos[1] - self.drag_starting_pos[1]) + 1) * gw.tile_s))
            self.surf.set_colorkey((0, 0, 0), RLEACCEL)
            self.rect = self.surf.get_rect(topleft=(min(self.pos[0], self.drag_starting_pos[0]) * gw.tile_s,
                                                    min(self.pos[1], self.drag_starting_pos[1]) * gw.tile_s))
            if isinstance(gw.cursor.held_structure, Farmland):
                self.create_farmland_field(gw)
            elif type(gw.cursor.held_structure) in {Road, Wall}:
                self.create_snapper_line(gw)
        self.surf.set_alpha(128)

    def create_farmland_field(self, gw):
        if self.rect.width == gw.tile_s or self.rect.height == gw.tile_s:
            self.handle_edge_cases(gw)
        else:
            for x in range(gw.tile_s, self.rect.width - gw.tile_s, gw.tile_s):
                for y in range(gw.tile_s, self.rect.height - gw.tile_s, gw.tile_s):
                    self.surf.blit(gw.cursor.held_structure.snapper_dict[('N', 'E', 'S', 'W')], (x, y))

            for edge, const_dimension, direction in zip(('ESW', 'NSW', 'NEW', 'NES'),
                                                        (0, self.rect.width - gw.tile_s,
                                                         self.rect.height - gw.tile_s, 0),
                                                        ('h', 'v', 'h', 'v')):
                if direction == 'h':
                    end = self.rect.width - gw.tile_s
                else:
                    end = self.rect.height - gw.tile_s

                for pos in range(gw.tile_s, end, gw.tile_s):
                    if direction == 'h':
                        blit_pos = (pos, const_dimension)
                    else:
                        blit_pos = (const_dimension, pos)
                    self.surf.blit(gw.cursor.held_structure.snapper_dict[tuple(edge)], blit_pos)

            for corner, blit_pos in zip(('SW', 'NW', 'NE', 'ES'),
                                        ((self.rect.width - gw.tile_s, 0),
                                         (self.rect.width - gw.tile_s, self.rect.height - gw.tile_s),
                                         (0, self.rect.height - gw.tile_s), (0, 0))):
                self.surf.blit(gw.cursor.held_structure.snapper_dict[tuple(corner)], blit_pos)

    def create_snapper_line(self, gw):
        self.sides_to_draw.clear()
        if self.rect.width == gw.tile_s or self.rect.height == gw.tile_s:
            self.handle_edge_cases(gw)
        else:
            if self.rect.width > self.rect.height:
                if self.pos[0] > self.drag_starting_pos[0]:
                    self.sides_to_draw.append("right")
                else:
                    self.sides_to_draw.append("left")
                if self.pos[1] > self.drag_starting_pos[1]:
                    self.sides_to_draw.append("top")
                else:
                    self.sides_to_draw.append("bottom")
            else:
                if self.pos[1] > self.drag_starting_pos[1]:
                    self.sides_to_draw.append("bottom")
                else:
                    self.sides_to_draw.append("top")
                if self.pos[0] > self.drag_starting_pos[0]:
                    self.sides_to_draw.append("left")
                else:
                    self.sides_to_draw.append("right")

            if "top" in self.sides_to_draw:
                horiz_segment_y = 0
            else:
                horiz_segment_y = self.rect.height - gw.tile_s
            if "right" in self.sides_to_draw:
                vert_segment_x = self.rect.width - gw.tile_s
            else:
                vert_segment_x = 0

            for x in range(gw.tile_s, self.rect.width - gw.tile_s, gw.tile_s):
                self.surf.blit(gw.cursor.held_structure.snapper_dict[('E', 'W')], (x, horiz_segment_y))
            self.surf.blit(gw.cursor.held_structure.snapper_dict[('E',)], (0, horiz_segment_y))
            self.surf.blit(gw.cursor.held_structure.snapper_dict[('W',)], (self.rect.width - gw.tile_s, horiz_segment_y))

            for y in range(gw.tile_s, self.rect.height - gw.tile_s, gw.tile_s):
                self.surf.blit(gw.cursor.held_structure.snapper_dict[('N', 'S')], (vert_segment_x, y))
            self.surf.blit(gw.cursor.held_structure.snapper_dict[('S',)], (vert_segment_x, 0))
            self.surf.blit(gw.cursor.held_structure.snapper_dict[('N',)], (vert_segment_x, self.rect.height - gw.tile_s))

            if self.sides_to_draw in [["top", "right"], ["right", "top"]]:
                self.surf.blit(pg.Surface((gw.tile_s, gw.tile_s)), (self.rect.width - gw.tile_s, 0))
                self.surf.blit(gw.cursor.held_structure.snapper_dict[('S', 'W')], (self.rect.width - gw.tile_s, 0))
            elif self.sides_to_draw in [["bottom", "right"], ["right", "bottom"]]:
                self.surf.blit(pg.Surface((gw.tile_s, gw.tile_s)), (self.rect.width - gw.tile_s,
                                                                    self.rect.height - gw.tile_s))
                self.surf.blit(gw.cursor.held_structure.snapper_dict[('N', 'W')], (self.rect.width - gw.tile_s,
                                                                                   self.rect.height - gw.tile_s))
            elif self.sides_to_draw in [["bottom", "left"], ["left", "bottom"]]:
                self.surf.blit(pg.Surface((gw.tile_s, gw.tile_s)), (0, self.rect.height - gw.tile_s))
                self.surf.blit(gw.cursor.held_structure.snapper_dict[('N', 'E')], (0, self.rect.height - gw.tile_s))
            elif self.sides_to_draw in [["top", "left"], ["left", "top"]]:
                self.surf.blit(pg.Surface((gw.tile_s, gw.tile_s)), (0, 0))
                self.surf.blit(gw.cursor.held_structure.snapper_dict[('E', 'S')], (0, 0))

    def handle_edge_cases(self, gw):
        if self.rect.width == gw.tile_s and self.rect.height == gw.tile_s:
            self.surf.blit(gw.cursor.held_structure.snapper_dict[()], (0, 0))
        elif self.rect.width == gw.tile_s:
            if self.pos[1] > self.drag_starting_pos[1]:
                self.sides_to_draw.append("bottom")
            else:
                self.sides_to_draw.append("top")
            self.surf.blit(gw.cursor.held_structure.snapper_dict[('S', )], (0, 0))
            self.surf.blit(gw.cursor.held_structure.snapper_dict[('N', )], (0, self.rect.height - gw.tile_s))
            for y in range(gw.tile_s, self.rect.height - gw.tile_s, gw.tile_s):
                self.surf.blit(gw.cursor.held_structure.snapper_dict[('N', 'S')], (0, y))
        elif self.rect.height == gw.tile_s:
            if self.pos[0] > self.drag_starting_pos[0]:
                self.sides_to_draw.append("right")
            else:
                self.sides_to_draw.append("left")
            self.surf.blit(gw.cursor.held_structure.snapper_dict[('E', )], (0, 0))
            self.surf.blit(gw.cursor.held_structure.snapper_dict[('W', )], (self.rect.width - gw.tile_s, 0))
            for x in range(gw.tile_s, self.rect.width - gw.tile_s, gw.tile_s):
                self.surf.blit(gw.cursor.held_structure.snapper_dict[('E', 'W')], (x, 0))


class Structure(pg.sprite.Sprite):
    def __init__(self, xy, gw, *args):
        super().__init__()
        self.surf = pg.Surface((gw.tile_s, gw.tile_s))
        self.image_path = ""
        # self.string_type_dict = {"house": House, "tower": Tower, "road": Road, "wall": Wall, "gate": Gate,
        #                          "obama": Pyramid, "farmland": Farmland}
        self.type_string_dict = {val: key for key, val in gw.string_type_dict.items()}

        self.surf_ratio = (1, 1)
        self.pos = xy.copy()
        self.covered_tiles = {(0, 0)}
        self.rect = self.surf.get_rect(bottomright=(gw.tile_s * (xy[0] + 1), gw.tile_s * (xy[1] + 1)))
        self.base_profit = 0
        self.profit = self.base_profit
        self.cooldown = gw.TICK_RATE * 24
        self.time_left = self.cooldown
        self.build_cost = 0
        self.orientation = 'v'
        self.unsuitable_tiles = {"water"}
        self.can_override = False

        if gw.surrounded_tiles[self.pos[0]][self.pos[1]] == 2:
            self.inside = True
        else:
            self.inside = False

    def get_profit(self, gw):
        self.time_left -= 1
        if self.time_left == 0:
            self.time_left = self.cooldown
            gw.time_manager.gold += self.profit

    def update_zoom(self, gw):
        self.surf = pg.transform.scale(self.surf, (self.surf_ratio[0] * gw.tile_s, self.surf_ratio[1] * gw.tile_s))
        self.rect = self.surf.get_rect(bottomright=(gw.tile_s * (self.pos[0] + 1), gw.tile_s * (self.pos[1] + 1)))

    def can_be_placed(self, gw, pos):
        if any([gw.tile_type_map[pos[0] + rel[0]][pos[1] + rel[1]] in self.unsuitable_tiles
                for rel in self.covered_tiles]):
            return False, "unsuitable_location_tile"

        if any([isinstance(gw.struct_map[pos[0] + rel[0]][pos[1] + rel[1]], Structure)
                for rel in gw.cursor.held_structure.covered_tiles]):
            return False, "unsuitable_location_structure"

        if gw.cursor.held_structure.build_cost >= gw.time_manager.gold:
            return False, "could_not_afford"

        return True, "was_built"

    def to_json(self):
        return {
            "type": self.type_string_dict[type(self)],
            "image_path": self.image_path,
            "rect": (self.rect.left, self.rect.top, self.rect.width, self.rect.height),
            "pos": self.pos,
            "profit": self.profit,
            "time_left": self.time_left,
            "inside": self.inside,
            "orientation": self.orientation,
        }

    def from_json(self, y):
        self.rect = pg.rect.Rect(y["rect"])
        self.profit = y["profit"]
        self.time_left = y["time_left"]
        self.inside = y["inside"]
        return self


class Tree(Structure):
    def __init__(self, xy, gw, *args):
        super().__init__(xy, gw)
        self.image_path = "assets/tree.png"
        self.surf = pg.transform.scale(pg.image.load(self.image_path).convert(), (gw.tile_s, gw.tile_s))
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)


class Mine(Structure):
    def __init__(self, xy, gw, *args):
        super().__init__(xy, gw)
        self.image_path = "assets/mine.png"
        self.surf = pg.transform.scale(pg.image.load(self.image_path).convert(), (gw.tile_s, gw.tile_s * 2))
        self.surf_ratio = (1, 2)
        self.rect = self.surf.get_rect(bottomright=(gw.tile_s * (xy[0] + 1), gw.tile_s * (xy[1] + 1)))
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)


class Sawmill(Structure):
    def __init__(self, xy, gw, *args):
        super().__init__(xy, gw)
        self.image_path = "assets/sawmill.png"
        self.surf = pg.transform.scale(pg.image.load(self.image_path).convert(), (gw.tile_s * 2, gw.tile_s * 2))
        self.surf_ratio = (2, 2)
        self.covered_tiles = {(0, 0), (-1, 0)}
        self.rect = self.surf.get_rect(bottomright=(gw.tile_s * (xy[0] + 1), gw.tile_s * (xy[1] + 1)))
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)


class Pyramid(Structure):
    def __init__(self, xy, gw, *args):
        super().__init__(xy, gw)
        self.image_path = "assets/obama.png"
        self.surf = pg.transform.scale(pg.image.load("assets/obama.png").convert(),
                                       (gw.tile_s * 2, gw.tile_s * 2))
        self.surf_ratio = (2, 2)
        self.covered_tiles = {(0, 0), (-1, 0)}
        self.rect = self.surf.get_rect(bottomright=(gw.tile_s * (xy[0] + 1), gw.tile_s * (xy[1] + 1)))
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)


class House(Structure):
    def __init__(self, xy, gw, *args):
        super().__init__(xy, gw)
        self.image_path = "assets/house" + str(randint(1, 2)) + ".png"
        self.surf = pg.transform.scale(pg.image.load(self.image_path).convert(),
                                       (gw.tile_s, gw.tile_s * 21 / 15))
        self.surf_ratio = (1, 21 / 15)
        self.rect = self.surf.get_rect(bottomright=(gw.tile_s * (xy[0] + 1), gw.tile_s * (xy[1] + 1)))
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.base_profit = 10
        self.profit = self.base_profit
        self.build_cost = 50

    def update_profit(self, gw):
        self.profit = self.base_profit
        visited = {tuple(self.pos)}
        nearby_houses = 0
        for xy in ((-1, 0), (0, 1), (1, 0), (0, -1)):
            if not gw.is_out_of_bounds(self.pos[0] + xy[0], self.pos[1] + xy[1]) and \
                    isinstance(gw.struct_map[self.pos[0] + xy[0]][self.pos[1] + xy[1]], Road):
                nearby_houses += self.detect_nearby_houses(gw, [self.pos[0] + xy[0], self.pos[1] + xy[1]], visited)
        self.profit += nearby_houses
        if self.inside:
            self.profit *= 2

    def detect_nearby_houses(self, gw, xy, visited):

        resolved = [[True for _ in range(gw.height_tiles)] for _ in range(gw.width_tiles)]
        required = {"roads"}
        distance = 0
        nearby = 0

        def _detect_nearby_houses(gw, resolved, xy, required, distance, visited):
            nonlocal nearby
            if distance >= 6:
                return
            for xy0 in gw.direction_to_xy_dict.values():
                if isinstance(gw.struct_map[xy[0] + xy0[0]][xy[1] + xy0[1]], House) and \
                        (xy[0] + xy0[0], xy[1] + xy0[1]) not in visited:
                    nearby += 1
                    visited.add((xy[0] + xy0[0], xy[1] + xy0[1]))

            resolved[xy[0]][xy[1]] = False
            for direction in gw.struct_map[xy[0]][xy[1]].neighbours:
                next = gw.direction_to_xy_dict[direction]
                if resolved[xy[0] + next[0]][xy[1] + next[1]] and \
                        bool(set(gw.struct_map[xy[0] + next[0]][xy[1] + next[1]].snapsto.values()) & required):
                    _detect_nearby_houses(gw, resolved, [xy[0] + next[0], xy[1] + next[1]],
                                          required, distance + 1, visited)

        _detect_nearby_houses(gw, resolved, xy, required, distance, visited)
        return nearby


class Tower(Structure):
    def __init__(self, xy, gw, *args):
        super().__init__(xy, gw)
        self.image_path = "assets/big_tower.png"
        self.surf = pg.transform.scale(pg.image.load(self.image_path).convert(), (gw.tile_s, 2 * gw.tile_s))
        self.surf_ratio = (1, 2)
        self.rect = self.surf.get_rect(bottomright=(gw.tile_s * (xy[0] + 1), gw.tile_s * (xy[1] + 1)))
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)


class Snapper(Structure):
    def __init__(self, xy, gw):
        super().__init__(xy, gw)
        self.snapsto = {}
        self.neighbours = set()
        self.snapper_dict_key = ""
        self.snapper_dict = {}
        self.direction_to_int_dict = {direction: i for i, direction in enumerate(('N', 'E', 'S', 'W'))}

    def update_edges(self, direction, add):
        if add == 1:
            self.neighbours.update(direction)
        elif add == -1 and direction in self.neighbours:
            self.neighbours.remove(direction)

        directions = tuple(sorted(self.neighbours, key=lambda x: self.direction_to_int_dict[x]))
        self.surf = self.snapper_dict[directions].copy()

    def can_be_snapped(self, gw, curr_pos, prev_pos):
        change = tuple([curr_pos[0] - prev_pos[0], curr_pos[1] - prev_pos[1]])
        if change not in gw.pos_change_dict.keys():
            return False, "unsuitable_change"

        if not (isinstance(gw.struct_map[curr_pos[0]][curr_pos[1]], Snapper) and
                isinstance(gw.struct_map[prev_pos[0]][prev_pos[1]], Snapper)):

            return False, "one_of_structures_cannot_snap"

        if not gw.struct_map[curr_pos[0]][curr_pos[1]].snapsto[gw.pos_change_dict[change][0]] == \
                gw.struct_map[prev_pos[0]][prev_pos[1]].snapsto[gw.pos_change_dict[change][1]]:
            return False, "didn't_match"

        if gw.pos_change_dict[change][0] in gw.struct_map[curr_pos[0]][curr_pos[1]].neighbours:
            return False, "already_snapped"

        return True, "was_snapped"

    def to_json(self):
        return {**super().to_json(), **{"snapper_dict_key": self.snapper_dict_key, "neighbours": list(self.neighbours)}}

    def from_json(self, y):
        super().from_json(y)
        self.snapper_dict_key = y["snapper_dict_key"]
        self.neighbours = set(y["neighbours"])
        self.update_edges('N', 0)
        return self


class Farmland(Snapper):
    def __init__(self, xy, gw, *args):
        super().__init__(xy, gw)
        self.image_path = ""
        self.snapper_dict_key = "farmlands"
        self.snapper_dict = gw.snapper_dict["farmlands"]
        self.surf = self.snapper_dict[()].copy()
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.snapsto = {snap: "roads" for snap in ('N', 'E', 'S', 'W')}
        self.unsuitable_tiles = {"water", "desert"}
        self.base_profit = 1
        self.profit = self.base_profit
        self.build_cost = 10
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)


class Road(Snapper):
    def __init__(self, xy, gw, *args):
        super().__init__(xy, gw)
        self.image_path = ""
        self.snapper_dict_key = "roads"
        self.snapper_dict = gw.snapper_dict["roads"]
        self.surf = self.snapper_dict[()].copy()
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.snapsto = {snap: "roads" for snap in ('N', 'E', 'S', 'W')}
        self.base_profit = -2
        self.profit = self.base_profit
        self.build_cost = 10


class Wall(Snapper):
    def __init__(self, xy, gw, *args):
        super().__init__(xy, gw)
        self.image_path = ""
        self.snapper_dict_key = "walls"
        self.snapper_dict = gw.snapper_dict["walls"]
        self.surf = self.snapper_dict[()].copy()
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.snapsto = {snap: "walls" for snap in ('N', 'E', 'S', 'W')}
        self.base_profit = -3
        self.profit = self.base_profit
        self.build_cost = 20


class Gate(Wall, Road):
    def __init__(self, xy, gw, orientation="v"):
        super().__init__(xy, gw)
        self.orientation = orientation
        self.image_path = ""
        if orientation == "v":
            self.snapper_dict_key = "vgates"
            self.snapper_dict = gw.snapper_dict["vgates"]
            self.snapsto = {'N': "roads", 'E': "walls", 'S': "roads", 'W': "walls"}
        else:
            self.snapper_dict_key = "hgates"
            self.snapper_dict = gw.snapper_dict["hgates"]
            self.snapsto = {'N': "walls", 'E': "roads", 'S': "walls", 'W': "roads"}
        self.surf = self.snapper_dict[()].copy()
        self.surf_ratio = (1, 20 / 15)
        self.rect = self.surf.get_rect(bottomright=(gw.tile_s * (xy[0] + 1), gw.tile_s * (xy[1] + 1)))
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.base_profit = -15
        self.profit = self.base_profit
        self.build_cost = 150
        self.can_override = True
        self.directions_to_connect_to = set()

    def can_build_gate_on_a_structure(self, gw):
        if (not isinstance(gw.struct_map[gw.cursor.pos[0]][gw.cursor.pos[1]], Wall) and
            not isinstance(gw.struct_map[gw.cursor.pos[0]][gw.cursor.pos[1]], Road)) or \
                isinstance(gw.struct_map[gw.cursor.pos[0]][gw.cursor.pos[1]], Gate):
            return False

        self.directions_to_connect_to.clear()

        for direction, direction_reverse, x, y in zip(('N', 'E', 'S', 'W'), ('S', 'W', 'N', 'E'),
                                                      (0, -1, 0, 1), (1, 0, -1, 0)):
            if not gw.is_out_of_bounds(gw.cursor.pos[0] + x, gw.cursor.pos[1] + y) and \
                    isinstance(gw.struct_map[gw.cursor.pos[0] + x][gw.cursor.pos[1] + y], Snapper) and \
                    direction in gw.struct_map[gw.cursor.pos[0] + x][gw.cursor.pos[1] + y].neighbours:
                if self.snapsto[direction_reverse] != \
                        gw.struct_map[gw.cursor.pos[0] + x][gw.cursor.pos[1] + y].snapsto[direction]:
                    return False
                self.directions_to_connect_to.add(direction_reverse)

        return True

    def can_be_placed(self, gw, is_lmb_held_down):
        was_built, message = super().can_be_placed(gw, is_lmb_held_down)
        if message != "unsuitable_location_structure":
            return was_built, message

        if not self.can_build_gate_on_a_structure(gw):
            return False, "unsuitable_location"

        return True, "was_overridden"

    def rotate(self, gw):
        if self.orientation == "v":
            self.orientation = "h"
            self.snapsto = {'N': "walls", 'E': "roads", 'S': "walls", 'W': "roads"}
        else:
            self.orientation = "v"
            self.snapsto = {'N': "roads", 'E': "walls", 'S': "roads", 'W': "walls"}
        self.surf = pg.transform.scale(pg.image.load("assets/" + self.orientation + "gates/gate.png").convert(),
                                       (gw.tile_s, gw.tile_s * 20 / 15))
        self.rect = self.surf.get_rect(bottomright=(gw.tile_s * (self.pos[0] + 1), gw.tile_s * (self.pos[1] + 1)))
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
