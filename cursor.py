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
        self.change = [0, 0]
        self.drag_starting_pos = [0, 0]
        self.held_structure = None
        self.ghost = None

    def update(self, gw):
        self.previous_pos = self.pos.copy()
        self.pos[0] = (pg.mouse.get_pos()[0] + gw.scene.rect.x) // gw.tile_s
        self.pos[1] = (pg.mouse.get_pos()[1] + gw.scene.rect.y) // gw.tile_s
        self.change = tuple([a - b for a, b in zip(self.pos, self.previous_pos)])
        self.rect.x = self.pos[0] * gw.tile_s
        self.rect.y = self.pos[1] * gw.tile_s

    def draw(self, gw):
        if not self.is_in_demolish_mode:
            gw.scene.surf.blit(self.surf, self.rect)
        if self.ghost is not None:
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

        if mode == "demolish":
            self.is_in_demolish_mode = mode_state
        if mode == "drag_build":
            self.is_in_drag_build_mode = mode_state

        if mode_state:
            mode_button.is_locked = True
            mode_button.is_held_down = True
            if mode == "demolish":
                self.held_structure = None
                self.ghost = Ghost(gw)
        else:
            if mode == "demolish":
                self.ghost = None
            mode_button.is_locked = False
            mode_button.is_held_down = False


class Ghost:
    def __init__(self, gw):
        if not gw.cursor.is_in_demolish_mode:
            self.surf = gw.cursor.held_structure.surf
        else:
            self.surf = gw.spritesheet.get_snapper_surf(gw, (), "demolish")
        self.surf.set_alpha(128)
        self.pos = gw.cursor.pos
        self.drag_starting_pos = gw.cursor.pos.copy()
        self.rect = self.surf.get_rect(bottomright=(gw.tile_s * (self.pos[0] + 1), gw.tile_s * (self.pos[1] + 1)))
        self.sides_to_draw = []
        self.main_axis = "horiz"
        self.is_listening_for_axis = True

    def update(self, gw):
        self.pos = gw.cursor.pos
        if not gw.cursor.is_dragging:
            if not gw.cursor.is_in_demolish_mode:
                self.surf = gw.cursor.held_structure.surf
            else:
                self.surf = gw.spritesheet.get_snapper_surf(gw, (), "demolish")
            self.rect = self.surf.get_rect(bottomright=(gw.tile_s * (self.pos[0] + 1), gw.tile_s * (self.pos[1] + 1)))

        else:
            self.surf = pg.Surface(((abs(self.pos[0] - self.drag_starting_pos[0]) + 1) * gw.tile_s,
                                    (abs(self.pos[1] - self.drag_starting_pos[1]) + 1) * gw.tile_s))
            self.surf.set_colorkey((0, 0, 0), RLEACCEL)
            self.rect = self.surf.get_rect(topleft=(min(self.pos[0], self.drag_starting_pos[0]) * gw.tile_s,
                                                    min(self.pos[1], self.drag_starting_pos[1]) * gw.tile_s))
            if gw.cursor.is_in_demolish_mode:
                self.draw_area(gw, "demolish")
            elif isinstance(gw.cursor.held_structure, Farmland):
                self.draw_area(gw, "farmland")
            elif type(gw.cursor.held_structure) in {Road, Wall}:
                self.create_snapper_line(gw)
        self.surf.set_alpha(128)

    def draw_area(self, gw, name):
        if self.rect.width == gw.tile_s or self.rect.height == gw.tile_s:
            self.handle_edge_cases(gw, name)
        else:
            for x in range(gw.tile_s, self.rect.width - gw.tile_s, gw.tile_s):
                for y in range(gw.tile_s, self.rect.height - gw.tile_s, gw.tile_s):
                    self.surf.blit(gw.spritesheet.get_snapper_surf(gw, ('N', 'E', 'S', 'W'), name), (x, y))

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
                    self.surf.blit(gw.spritesheet.get_snapper_surf(gw, tuple(edge), name), blit_pos)

            for corner, blit_pos in zip(('SW', 'NW', 'NE', 'ES'),
                                        ((self.rect.width - gw.tile_s, 0),
                                         (self.rect.width - gw.tile_s, self.rect.height - gw.tile_s),
                                         (0, self.rect.height - gw.tile_s), (0, 0))):
                self.surf.blit(gw.spritesheet.get_snapper_surf(gw, tuple(corner), name), blit_pos)

    def create_snapper_line(self, gw):
        self.sides_to_draw.clear()
        name = gw.cursor.held_structure.sheet_key
        if self.rect.size == (gw.tile_s, gw.tile_s):
            self.is_listening_for_axis = True
        elif self.is_listening_for_axis:
            if gw.cursor.change in {(1, 0), (-1, 0)}:
                self.main_axis = "horiz"
            elif gw.cursor.change in {(0, 1), (0, -1)}:
                self.main_axis = "vert"
            self.is_listening_for_axis = False
        if self.rect.width == gw.tile_s or self.rect.height == gw.tile_s:
            self.handle_edge_cases(gw, name)
        else:
            if self.main_axis == "horiz":
                if self.pos[0] > self.drag_starting_pos[0]:
                    self.sides_to_draw.append("right")
                else:
                    self.sides_to_draw.append("left")
                if self.pos[1] > self.drag_starting_pos[1]:
                    self.sides_to_draw.append("top")
                else:
                    self.sides_to_draw.append("bottom")
            elif self.main_axis == "vert":
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
                self.surf.blit(gw.spritesheet.get_snapper_surf(gw, ('E', 'W'), name), (x, horiz_segment_y))
            self.surf.blit(gw.spritesheet.get_snapper_surf(gw, ('E',), name), (0, horiz_segment_y))
            self.surf.blit(gw.spritesheet.get_snapper_surf(gw, ('W',), name), (self.rect.width - gw.tile_s,
                                                                                     horiz_segment_y))

            for y in range(gw.tile_s, self.rect.height - gw.tile_s, gw.tile_s):
                self.surf.blit(gw.spritesheet.get_snapper_surf(gw, ('N', 'S'), name), (vert_segment_x, y))
            self.surf.blit(gw.spritesheet.get_snapper_surf(gw, ('S',), name), (vert_segment_x, 0))
            self.surf.blit(gw.spritesheet.get_snapper_surf(gw, ('N',), name), (vert_segment_x,
                                                                                     self.rect.height - gw.tile_s))

            if self.sides_to_draw in [["top", "right"], ["right", "top"]]:
                self.surf.blit(pg.Surface((gw.tile_s, gw.tile_s)), (self.rect.width - gw.tile_s, 0))
                self.surf.blit(gw.spritesheet.get_snapper_surf(gw, ('S', 'W'), name), (self.rect.width - gw.tile_s, 0))
            elif self.sides_to_draw in [["bottom", "right"], ["right", "bottom"]]:
                self.surf.blit(pg.Surface((gw.tile_s, gw.tile_s)), (self.rect.width - gw.tile_s,
                                                                    self.rect.height - gw.tile_s))
                self.surf.blit(gw.spritesheet.get_snapper_surf(gw, ('N', 'W'), name), (self.rect.width - gw.tile_s,
                                                                                   self.rect.height - gw.tile_s))
            elif self.sides_to_draw in [["bottom", "left"], ["left", "bottom"]]:
                self.surf.blit(pg.Surface((gw.tile_s, gw.tile_s)), (0, self.rect.height - gw.tile_s))
                self.surf.blit(gw.spritesheet.get_snapper_surf(gw, ('N', 'E'), name), (0, self.rect.height - gw.tile_s))
            elif self.sides_to_draw in [["top", "left"], ["left", "top"]]:
                self.surf.blit(pg.Surface((gw.tile_s, gw.tile_s)), (0, 0))
                self.surf.blit(gw.spritesheet.get_snapper_surf(gw, ('E', 'S'), name), (0, 0))

    def handle_edge_cases(self, gw, name):
        if self.rect.size == (gw.tile_s, gw.tile_s):
            self.surf.blit(gw.spritesheet.get_snapper_surf(gw, (), name), (0, 0))
        elif self.rect.width == gw.tile_s:
            if self.pos[1] > self.drag_starting_pos[1]:
                self.sides_to_draw.append("bottom")
            else:
                self.sides_to_draw.append("top")
            self.surf.blit(gw.spritesheet.get_snapper_surf(gw, ('S', ), name), (0, 0))
            self.surf.blit(gw.spritesheet.get_snapper_surf(gw, ('N', ), name), (0, self.rect.height - gw.tile_s))
            for y in range(gw.tile_s, self.rect.height - gw.tile_s, gw.tile_s):
                self.surf.blit(gw.spritesheet.get_snapper_surf(gw, ('N', 'S'), name), (0, y))
        elif self.rect.height == gw.tile_s:
            if self.pos[0] > self.drag_starting_pos[0]:
                self.sides_to_draw.append("right")
            else:
                self.sides_to_draw.append("left")
            self.surf.blit(gw.spritesheet.get_snapper_surf(gw, ('E', ), name), (0, 0))
            self.surf.blit(gw.spritesheet.get_snapper_surf(gw, ('W', ), name), (self.rect.width - gw.tile_s, 0))
            for x in range(gw.tile_s, self.rect.width - gw.tile_s, gw.tile_s):
                self.surf.blit(gw.spritesheet.get_snapper_surf(gw, ('E', 'W'), name), (x, 0))
