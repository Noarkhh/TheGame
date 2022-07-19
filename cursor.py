import pygame as pg
from pygame import RLEACCEL
from structures import Farmland, Road, Wall


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
        self.surf_demolish_raw = self.surf_demolish.copy()

        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.surf_demolish.set_colorkey((255, 255, 255), RLEACCEL)
        self.surf_demolish.set_alpha(128)
        self.surf_demolish_raw.set_colorkey((255, 255, 255), RLEACCEL)
        self.surf_demolish_raw.set_alpha(128)

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
