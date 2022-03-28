import pygame as pg
from random import randint
import time
from pygame.locals import (RLEACCEL,
                           K_UP,
                           K_DOWN,
                           K_LEFT,
                           K_RIGHT)


class Background(pg.sprite.Sprite):
    def __init__(self, gw):
        super().__init__()
        self.surf = gw.map_surf.copy()
        self.surf_raw = gw.map_surf.copy()
        self.surf_rendered = self.surf.subsurface((0, 0, gw.WINDOW_WIDTH, gw.WINDOW_HEIGHT))
        self.rect = self.surf_rendered.get_rect()

    def move_screen(self, gw, cursor):
        if cursor.rect.right >= self.rect.right <= gw.width_pixels - gw.tile_s / 2:
            self.rect.move_ip(gw.tile_s / 2, 0)
        if cursor.rect.left <= self.rect.left >= 0 + gw.tile_s / 2:
            self.rect.move_ip(-gw.tile_s / 2, 0)
        if cursor.rect.bottom >= self.rect.bottom <= gw.height_pixels - gw.tile_s / 2:
            self.rect.move_ip(0, gw.tile_s / 2)
        if cursor.rect.top <= self.rect.top >= 0 + gw.tile_s / 2:
            self.rect.move_ip(0, -gw.tile_s / 2)
        self.surf_rendered = self.surf.subsurface(self.rect)


class Entities(pg.sprite.Group):
    def give_y(self, sprite):
        return sprite.pos[1]

    def draw(self, background):
        sprites = self.sprites()
        for spr in sorted(sprites, key=lambda spr: spr.pos[1]):
            if spr.rect.colliderect(background.rect):
                background.surf.blit(spr.surf, spr.rect)
        self.lostsprites = []


class Statistics:
    def __init__(self):
        self.font_size = 24
        self.font = pg.font.SysFont('consolas', self.font_size)
        self.stat_window = pg.Surface((self.font_size * 20, self.font_size * 10))
        self.stat_window.fill((0, 0, 0))


class GlobalStatistics(Statistics):
    def __init__(self):
        super().__init__()
        self.rect = self.stat_window.get_rect(topleft=(2, 2))
        self.tick = 0
        self.time = [0, 0, 0]
        self.elapsed = 1
        self.start = time.time()
        self.end = 0

    def update_global_stats(self, gw):
        self.stat_window.fill((0, 0, 0))
        self.stat_window.blit(self.font.render(
            "Time: " + str(self.time[0]) + ":00, Day " + str(self.time[1] + 1) + ", Week " + str(self.time[2] + 1),
            False, (255, 255, 255), (0, 0, 0)), (0, 0))
        self.stat_window.blit(self.font.render("Gold: " + str(gw.vault.gold) + "g",
                                               False, (255, 255, 255), (0, 0, 0)), (0, 26))
        self.stat_window.blit(self.font.render("TPS: " + str(round(self.elapsed * gw.TICK_RATE, 2)),
                                               False, (255, 255, 255), (0, 0, 0)), (0, 52))
        self.stat_window.set_colorkey((0, 0, 0), RLEACCEL)

        # layer = pg.Surface((200, 80))
        # layer.fill((0, 0, 0))
        # layer.set_alpha(100)
        # layer.blit(self.stat_window, (0, 0))
        # self.stat_window = layer

    def get_time(self, gw):
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


class TileStatistics(Statistics):
    def __init__(self, gw):
        super().__init__()
        self.rect = self.stat_window.get_rect(bottomright=(gw.WINDOW_WIDTH - 2, gw.WINDOW_HEIGHT - 2))

    def update_tile_stats(self, xy, gw):
        def blit_stat(stat):
            nonlocal stat_height
            stat_surf = self.font.render(stat, False, (255, 255, 255), (0, 0, 0))
            stat_rect = stat_surf.get_rect(bottom=self.stat_window.get_height() - stat_height,
                                           right=self.stat_window.get_width())
            self.stat_window.blit(stat_surf, stat_rect)
            stat_height += self.font_size + 4

        self.stat_window.fill((0, 0, 0))
        stat_height = 4

        if isinstance(gw.struct_map[xy[0]][xy[1]], Structure):
            blit_stat("time left: " + str("{:.2f}".format(gw.struct_map[xy[0]][xy[1]].time_left / gw.TICK_RATE)) + "s")
            blit_stat("cooldown: " + str(gw.struct_map[xy[0]][xy[1]].cooldown / gw.TICK_RATE) + "s")
            blit_stat("profit: " + str(gw.struct_map[xy[0]][xy[1]].profit) + "g")
            blit_stat("inside: " + str(gw.struct_map[xy[0]][xy[1]].inside))
            blit_stat(str(type(gw.struct_map[xy[0]][xy[1]]))[17:-2])
        blit_stat(gw.tile_type_map[xy[0]][xy[1]])
        blit_stat(str(xy))
        self.stat_window.set_colorkey((0, 0, 0), RLEACCEL)


class Vault:
    def __init__(self):
        self.gold = 100000


class Cursor(pg.sprite.Sprite):
    def __init__(self, gw):
        super().__init__()
        self.windup = [0 for _ in range(4)]
        self.cooldown = [0 for _ in range(4)]
        self.surf = pg.transform.scale(pg.image.load("assets/cursor3.png").convert(), (gw.tile_s, gw.tile_s))
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.surf.get_rect()
        self.pos = [0, 0]
        self.hold = None

    def update_arrows(self, gw, pressed_keys):
        cooltime = 20
        key_list = [True if pressed_keys[key] else False for key in (K_UP, K_DOWN, K_LEFT, K_RIGHT)]
        iter_list = [(key, sign, xy) for key, sign, xy in zip(key_list, (-1, 1, -1, 1), (1, 1, 0, 0))]
        for i, elem in enumerate(iter_list):
            if elem[0]:
                if self.cooldown[i] <= self.windup[i]:
                    if self.windup[i] < cooltime - 8:
                        self.windup[i] += 8
                    else:
                        self.windup[i] = cooltime
                    self.pos[elem[2]] += elem[1]
                    self.cooldown[i] = cooltime
                    self.windup[i] -= 2
            else:
                self.windup[i] = 0
                self.cooldown[i] = 0
        bruh = False
        if self.pos[0] < 0:
            self.pos[0] = 0
            bruh = True
        if self.pos[0] > gw.WIDTH_TILES - 1:
            self.pos[0] = gw.WIDTH_TILES - 1
            bruh = True
        if self.pos[1] < 0:
            self.pos[1] = 0
            bruh = True
        if self.pos[1] > gw.HEIGHT_TILES - 1:
            self.pos[1] = gw.HEIGHT_TILES - 1
            bruh = True
        if bruh:
            gw.speech_channel.play(gw.sounds["Insult" + str(randint(1, 20))])

        self.cooldown = [x - 1 if x > 0 else 0 for x in self.cooldown]
        self.rect.x = self.pos[0] * gw.tile_s
        self.rect.y = self.pos[1] * gw.tile_s

    def update_mouse(self, gw, xy, bg):
        self.pos[0] = (xy[0] + bg.rect.x) // gw.tile_s
        self.pos[1] = (xy[1] + bg.rect.y) // gw.tile_s
        self.rect.x = self.pos[0] * gw.tile_s
        self.rect.y = self.pos[1] * gw.tile_s


class Ghost(pg.sprite.Sprite):
    def __init__(self, xy, gw, surf):
        super().__init__()
        self.surf = surf
        self.surf.set_alpha(128)
        self.position = xy
        self.rect = surf.get_rect(bottomright=(gw.tile_s * (xy[0] + 1), gw.tile_s * (xy[1] + 1)))

    def update(self, gw, xy, surf):
        self.position = xy
        self.rect.right = gw.tile_s * (xy[0] + 1)
        self.rect.bottom = gw.tile_s * (xy[1] + 1)
        self.surf = surf
        self.surf.set_alpha(128)


class Structure(pg.sprite.Sprite):
    def __init__(self, xy, gw):
        super().__init__()
        self.surf = pg.Surface((gw.tile_s, gw.tile_s))
        self.surf.fill((0, 0, 0))
        self.pos = xy.copy()
        self.rect = self.surf.get_rect(bottomright=(gw.tile_s * (xy[0] + 1), gw.tile_s * (xy[1] + 1)))
        self.profit = 0
        self.cooldown = gw.TICK_RATE * 24
        self.time_left = self.cooldown
        self.cost = 0
        self.inside = False

    def get_profit(self, vault):
        self.time_left -= 1
        if self.time_left == 0:
            self.time_left = self.cooldown
            vault.gold += self.profit


class Tree(Structure):
    def __init__(self, xy, gw):
        super().__init__(xy, gw)
        self.surf = pg.transform.scale(pg.image.load("assets/tree.png").convert(), (gw.tile_s, gw.tile_s))
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)


class Cactus(Structure):
    def __init__(self, xy, gw):
        super().__init__(xy, gw)
        self.surf = pg.transform.scale(pg.image.load("assets/cactus.png").convert(), (gw.tile_s, gw.tile_s))
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)


class Pyramid(Structure):
    def __init__(self, xy, gw):
        super().__init__(xy, gw)
        self.surf = pg.transform.scale(pg.image.load("assets/obama.png").convert(),
                                       (gw.tile_s * 4, gw.tile_s * 4))
        self.rect = self.surf.get_rect(bottomright=(gw.tile_s * (xy[0] + 1), gw.tile_s * (xy[1] + 1)))
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)


class House(Structure):
    def __init__(self, xy, gw):
        super().__init__(xy, gw)
        self.surf = pg.transform.scale(pg.image.load("assets/house" + str(randint(1, 2)) + ".png").convert(),
                                       (gw.tile_s, gw.tile_s * 21 / 15))
        self.rect = self.surf.get_rect(bottomright=(gw.tile_s * (xy[0] + 1), gw.tile_s * (xy[1] + 1)))
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.profit = 10
        self.cost = 50


class Tower(Structure):
    def __init__(self, xy, gw):
        super().__init__(xy, gw)
        self.surf = pg.transform.scale(pg.image.load("assets/big_tower.png").convert(), (gw.tile_s, 2 * gw.tile_s))
        self.rect = self.surf.get_rect(bottomright=(gw.tile_s * (xy[0] + 1), gw.tile_s * (xy[1] + 1)))
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)


class Snapper(Structure):
    def __init__(self, xy, gw):
        super().__init__(xy, gw)
        self.snapsto = {}
        self.neighbours = set()
        self.snapper_dict = {}

    def update_edges(self, direction, add):
        if add:
            self.neighbours.update(direction)
        elif direction in self.neighbours:
            self.neighbours.remove(direction)

        def assign_value(direct):
            if direct == 'N': return 0
            if direct == 'E': return 1
            if direct == 'S': return 2
            if direct == 'W': return 3

        directions = tuple(sorted(self.neighbours, key=assign_value))
        self.surf = self.snapper_dict[directions]


class Road(Snapper):
    def __init__(self, xy, gw):
        super().__init__(xy, gw)
        self.snapper_dict = gw.snapper_dict["roads"]
        self.surf = self.snapper_dict[()].copy()
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.snapsto = {snap: "roads" for snap in ('N', 'E', 'S', 'W')}
        self.profit = -3
        self.cost = 10


class Wall(Snapper):
    def __init__(self, xy, gw):
        super().__init__(xy, gw)
        self.snapper_dict = gw.snapper_dict["walls"]
        self.surf = self.snapper_dict[()].copy()
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.snapsto = {snap: "walls" for snap in ('N', 'E', 'S', 'W')}
        self.profit = -3
        self.cost = 20


class Gate(Wall, Road):
    def __init__(self, xy, gw, orientation="v"):
        super().__init__(xy, gw)
        self.orient = orientation
        if orientation == "v":
            self.snapper_dict = gw.snapper_dict["vgates"]
            self.snapsto = {'N': "roads", 'E': "walls", 'S': "roads", 'W': "walls"}
        else:
            self.snapper_dict = gw.snapper_dict["hgates"]
            self.snapsto = {'N': "walls", 'E': "roads", 'S': "walls", 'W': "roads"}
        self.surf = self.snapper_dict[()].copy()
        self.rect = self.surf.get_rect(bottomright=(gw.tile_s * (xy[0] + 1), gw.tile_s * (xy[1] + 1)))
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.profit = -15
        self.cost = 150

    def rotate(self, gw):
        if self.orient == "v":
            self.orient = "h"
            self.snapsto = {'N': "walls", 'E': "roads", 'S': "walls", 'W': "roads"}
        else:
            self.orient = "v"
            self.snapsto = {'N': "roads", 'E': "walls", 'S': "roads", 'W': "walls"}
        self.surf = pg.transform.scale(pg.image.load("assets/" + self.orient + "gates/gate.png").convert(),
                                       (gw.tile_s, gw.tile_s * 20 / 15))
        self.rect = self.surf.get_rect(bottomright=(gw.tile_s * (self.pos[0] + 1), gw.tile_s * (self.pos[1] + 1)))
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)