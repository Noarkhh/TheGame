import pygame as pg
from random import randint
from pygame.locals import RLEACCEL


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

        if gw.cursor.held_structure.build_cost > gw.time_manager.gold:
            return False, "couldn't_afford"

        return True, "was_built"

    def to_json(self):
        return {
            "type": self.type_string_dict[type(self)],
            "image_path": self.image_path,
            "rect": (self.rect.left, self.rect.top, self.rect.width, self.rect.height),
            "pos": self.pos,
            "profit": self.profit,
            "time_left": self.time_left,
            "orientation": self.orientation,
        }

    def from_json(self, y, gw):
        self.rect = pg.rect.Rect(y["rect"])
        self.profit = y["profit"]
        self.time_left = y["time_left"]
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
        self.sheet_key = ""
        self.direction_to_int_dict = {direction: i for i, direction in enumerate(('N', 'E', 'S', 'W'))}

    def update_edges(self, gw, direction, add):
        if add == 1:
            self.neighbours.update(direction)
        elif add == -1 and direction in self.neighbours:
            self.neighbours.remove(direction)

        directions = tuple(sorted(self.neighbours, key=lambda x: self.direction_to_int_dict[x]))
        self.surf = gw.spritesheet.get_snapper_surf(gw, directions, self.sheet_key, self.surf_ratio)

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
        return {**super().to_json(), **{"sheet_key": self.sheet_key, "neighbours": list(self.neighbours)}}

    def from_json(self, y, gw):
        super().from_json(y, gw)
        self.sheet_key = y["sheet_key"]
        self.neighbours = set(y["neighbours"])
        self.update_edges(gw, 'N', 0)
        return self


class Farmland(Snapper):
    def __init__(self, xy, gw, *args):
        super().__init__(xy, gw)
        self.image_path = ""
        self.sheet_key = "farmland"
        self.surf = gw.spritesheet.get_snapper_surf(gw, (), self.sheet_key, self.surf_ratio)
        self.snapsto = {snap: "roads" for snap in ('N', 'E', 'S', 'W')}
        self.unsuitable_tiles = {"water", "desert"}
        self.base_profit = 1
        self.profit = self.base_profit
        self.build_cost = 10


class Road(Snapper):
    def __init__(self, xy, gw, *args):
        super().__init__(xy, gw)
        self.image_path = ""
        self.sheet_key = "road"
        self.surf = gw.spritesheet.get_snapper_surf(gw, (), self.sheet_key, self.surf_ratio)
        self.snapsto = {snap: "roads" for snap in ('N', 'E', 'S', 'W')}
        self.unsuitable_tiles = {}
        self.base_profit = -2
        self.profit = self.base_profit
        self.build_cost = 10


class Bridge(Road):
    def __init__(self, xy, gw, *args):
        super().__init__(xy, gw)
        self.sheet_key = "bridge"
        self.surf = gw.spritesheet.get_snapper_surf(gw, (), self.sheet_key, self.surf_ratio)
        self.snapsto = {snap: "roads" for snap in ('N', 'E', 'S', 'W')}
        self.unsuitable_tiles = {"desert", "grassland"}
        self.base_profit = -10
        self.profit = self.base_profit
        self.build_cost = 30


class Wall(Snapper):
    def __init__(self, xy, gw, *args):
        super().__init__(xy, gw)
        self.image_path = ""
        self.sheet_key = "wall"
        self.surf = gw.spritesheet.get_snapper_surf(gw, (), self.sheet_key, self.surf_ratio)
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
            self.sheet_key = "vgate"
            self.snapsto = {'N': "roads", 'E': "walls", 'S': "roads", 'W': "walls"}
        else:
            self.sheet_key = "hgate"
            self.snapsto = {'N': "walls", 'E': "roads", 'S': "walls", 'W': "roads"}
        self.surf_ratio = (1, 20 / 15)
        self.surf = gw.spritesheet.get_snapper_surf(gw, (), self.sheet_key, self.surf_ratio)
        self.rect = self.surf.get_rect(bottomright=(gw.tile_s * (xy[0] + 1), gw.tile_s * (xy[1] + 1)))
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
            self.sheet_key = "hgate"
            self.snapsto = {'N': "walls", 'E': "roads", 'S': "walls", 'W': "roads"}
        else:
            self.orientation = "v"
            self.sheet_key = "vgate"
            self.snapsto = {'N': "roads", 'E': "walls", 'S': "roads", 'W': "walls"}
        self.surf = gw.spritesheet.get_snapper_surf(gw, (), self.sheet_key, self.surf_ratio)
        self.rect = self.surf.get_rect(bottomright=(gw.tile_s * (self.pos[0] + 1), gw.tile_s * (self.pos[1] + 1)))
