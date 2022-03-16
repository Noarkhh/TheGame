import pygame as pg
import os
from pygame.locals import (RLEACCEL,
                           K_UP,
                           K_DOWN,
                           K_LEFT,
                           K_RIGHT,
                           K_SPACE,
                           KEYDOWN,
                           QUIT,
                           K_ESCAPE,
                           K_t,
                           K_h,
                           K_r,
                           K_n)

LAYOUT = pg.image.load("assets/layout2.png")
HEIGHT_TILES = LAYOUT.get_height()
WIDTH_TILES = LAYOUT.get_width()
TILE_S = 30
WIDTH_PIXELS = WIDTH_TILES * TILE_S
HEIGHT_PIXELS = HEIGHT_TILES * TILE_S
TICK_RATE = 20


class Statistics:
    def __init__(self):
        self.stat_window = pg.Surface((200, 120))
        self.stat_window.fill((0, 0, 0))
        self.font = pg.font.SysFont('consolas', 26)
        self.rect = self.stat_window.get_rect(bottom=HEIGHT_PIXELS - 2, right=WIDTH_PIXELS - 4)

    def update_stats(self, xy, structure_map, tile_type_map):
        self.stat_window.fill((0, 0, 0))
        stat_height = 0
        if isinstance(structure_map[xy[0]][xy[1]], Structure):
            struct_stat_surf = self.font.render(str(type(structure_map[xy[0]][xy[1]])),
                                                True, (255, 255, 255), (0, 0, 0))
            stat_rect = struct_stat_surf.get_rect(bottom=120, right=200)
            self.stat_window.blit(struct_stat_surf, stat_rect)
            # stat_rect.move_ip(0, 30)
            stat_height += 30
        tile_stat_surf = self.font.render(tile_type_map[xy[0]][xy[1]], True, (255, 255, 255), (0, 0, 0))
        stat_rect = tile_stat_surf.get_rect(bottom=120 - stat_height, right=200)
        self.stat_window.blit(tile_stat_surf, stat_rect)
        self.stat_window.set_colorkey((0, 0, 0), RLEACCEL)


class Cursor(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.windup = [0 for _ in range(4)]
        self.cooldown = [0 for _ in range(4)]
        self.surf = pg.transform.scale(pg.image.load("assets/cursor3.png").convert(), (TILE_S, TILE_S))
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.surf.get_rect()
        self.pos = [0, 0]
        self.hold = None

    def update(self, pressed_keys):
        cooltime = 10
        key_list = [True if pressed_keys[key] else False for key in (K_UP, K_DOWN, K_LEFT, K_RIGHT)]
        iter_list = [(key, sign, xy) for key, sign, xy in zip(key_list, (-1, 1, -1, 1), (1, 1, 0, 0))]
        for i, elem in enumerate(iter_list):
            if elem[0]:
                if self.cooldown[i] <= self.windup[i]:
                    if self.windup[i] < cooltime: self.windup[i] += 4
                    self.pos[elem[2]] += elem[1]
                    self.cooldown[i] = cooltime
            else:
                self.windup[i] = 0
                self.cooldown[i] = 0

        if self.pos[0] < 0:
            self.pos[0] = 0
            bruh_se.play()
        if self.pos[0] > WIDTH_TILES - 1:
            self.pos[0] = WIDTH_TILES - 1
            bruh_se.play()
        if self.pos[1] < 0:
            self.pos[1] = 0
            bruh_se.play()
        if self.pos[1] > HEIGHT_TILES - 1:
            self.pos[1] = HEIGHT_TILES - 1
            bruh_se.play()

        self.cooldown = [x - 1 if x > 0 else 0 for x in self.cooldown]
        self.rect.x = self.pos[0] * TILE_S
        self.rect.y = self.pos[1] * TILE_S


class Ghost(pg.sprite.Sprite):
    def __init__(self, xy, surf):
        super().__init__()
        self.surf = surf
        self.surf.set_alpha(128)
        self.position = xy
        self.rect = surf.get_rect(top=(TILE_S * xy[1]), left=(TILE_S * xy[0]))

    def update(self, xy):
        self.position = xy
        self.rect.x = xy[0] * TILE_S
        self.rect.y = xy[1] * TILE_S


class Tile(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()


class Structure(pg.sprite.Sprite):
    def __init__(self, xy):
        super().__init__()
        self.surf = pg.Surface((60, 60))
        self.surf.fill((0, 0, 0))
        self.pos = xy
        self.rect = self.surf.get_rect(top=(TILE_S * xy[1]), left=(TILE_S * xy[0]))


class House(Structure):
    def __init__(self, xy):
        super().__init__(xy)
        self.surf = pg.transform.scale(pg.image.load("assets/hut1.png").convert(), (TILE_S, TILE_S))
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.taxed = False
        self.debt = 10

    def tax(self):
        pg.draw.circle(self.surf, (255, max(355 - 10 * self.debt, 0), 0), (30, 30), self.debt)
        self.debt += 5
        self.taxed = True


class Tower(Structure):
    def __init__(self, xy):
        super().__init__(xy)
        self.surf = pg.transform.scale(pg.image.load("assets/tower.png").convert(), (TILE_S, TILE_S))
        self.surf.set_colorkey((0, 0, 0), RLEACCEL)


class Road(Structure):
    def __init__(self, xy):
        super().__init__(xy)
        self.neighbours = set()
        self.surf = pg.transform.scale(pg.image.load("assets/roads/road0.png").convert(), (TILE_S, TILE_S))
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)

    def update_edges(self, direction, roads_list):
        self.neighbours.add(direction)

        # print(self.neighbours)

        def assign_value(direct):
            if direct == 'N': return 0
            if direct == 'E': return 1
            if direct == 'S': return 2
            if direct == 'W': return 3

        directions = tuple(sorted(self.neighbours, key=assign_value))

        self.surf = roads_list[directions]


def fill_roads_list():
    directory = os.listdir("assets/roads")
    dir_cut = []
    directions_list = [('0',), ('N',), ('E',), ('S',), ('W',), ('N', 'E'), ('E', 'S'), ('S', 'W'), ('N', 'W'),
                       ('N', 'S'), ('E', 'W'), ('N', 'E', 'S'), ('E', 'S', 'W'),
                       ('N', 'S', 'W'), ('N', 'E', 'W'), ('N', 'E', 'S', 'W')]
    roads_list = {directions_list[i]: pg.Surface((60, 60)) for i in range(16)}

    for name in directory:
        dir_cut.append(tuple(name[4:-4]))

    for file, name in zip(directory, dir_cut):
        roads_list[name] = pg.transform.scale(pg.image.load("assets/roads/" + file).convert(), (TILE_S, TILE_S))
        roads_list[name].set_colorkey((255, 255, 255), RLEACCEL)

    return roads_list


def pos_oob(x, y):
    if x < 0: return True
    if x > WIDTH_TILES - 1: return True
    if y < 0: return True
    if y > HEIGHT_TILES - 1: return True
    return False


def place_structure():
    if isinstance(cursor.hold, Structure):
        if structure_map[cursor.pos[0]][cursor.pos[1]] not in structures \
                and tile_type_map[cursor.pos[0]][cursor.pos[1]] != "sea":
            new_structure = type(cursor.hold)(cursor.pos)
            structure_group_dict[type(cursor.hold)].add(new_structure)
            structures.add(new_structure)
            all_sprites.add(new_structure)
            structure_map[new_structure.pos[0]][new_structure.pos[1]] = new_structure
            boom_se.play()
            if isinstance(new_structure, Road):
                for direction, direction_rev, x, y in zip(('N', 'E', 'S', 'W'), ('S', 'W', 'N', 'E'),
                                                          (0, -1, 0, 1), (1, 0, -1, 0)):
                    if not pos_oob(cursor.pos[0] + x, cursor.pos[1] + y) \
                            and isinstance(structure_map[cursor.pos[0] + x][cursor.pos[1] + y], Road):
                        structure_map[cursor.pos[0] + x][cursor.pos[1] + y].update_edges(direction, roads_list)
                        new_structure.update_edges(direction_rev, roads_list)
            # else:
            #     cursor.holding = None
        else:
            bruh_se.play()
    return


def generate_map():
    color_to_type = {(0, 255, 0, 255): "grassland", (0, 0, 255, 255): "sea"}
    tile_dict = {"grassland": pg.transform.scale(pg.image.load("assets/tiles/grassland_tile.png").convert(),
                                                 (TILE_S, TILE_S)),
                 "sea": pg.transform.scale(pg.image.load("assets/tiles/sea_tile.png").convert(),
                                           (TILE_S, TILE_S))}
    background = pg.Surface((WIDTH_TILES * TILE_S, HEIGHT_TILES * TILE_S))
    tile_map = [[0 for _ in range(HEIGHT_TILES)] for _ in range(WIDTH_TILES)]

    for x in range(WIDTH_TILES):
        for y in range(HEIGHT_TILES):
            tile_color = tuple(LAYOUT.get_at((x, y)))
            background.blit(tile_dict[color_to_type[tile_color]], (x * TILE_S, y * TILE_S))
            tile_map[x][y] = color_to_type[tile_color]
    return background, tile_map


if __name__ == "__main__":
    pg.init()
    pg.mixer.init()
    boom_se = pg.mixer.Sound("assets/boom sound effect.ogg")
    bruh_se = pg.mixer.Sound("assets/bruh sound effect.ogg")
    violin_se = pg.mixer.Sound("assets/violin screech sound effect.ogg")

    screen = pg.display.set_mode([WIDTH_PIXELS, HEIGHT_PIXELS])
    cursor = Cursor()
    statistics = Statistics()
    structure_map = [[0 for _ in range(HEIGHT_TILES)] for _ in range(WIDTH_TILES)]

    roads_list = fill_roads_list()

    background = generate_map()[0]
    tile_type_map = generate_map()[1]
    pg.display.set_caption("Twierdza: Zawodzie")

    houses = pg.sprite.Group()
    towers = pg.sprite.Group()
    roads = pg.sprite.Group()
    structures = pg.sprite.Group()
    all_sprites = pg.sprite.Group()
    all_sprites.add(cursor)

    clock = pg.time.Clock()
    key_structure_dict = {K_h: House, K_t: Tower, K_r: Road}
    structure_group_dict = {House: houses, Tower: towers, Road: roads}
    running = True
    # ------ MAIN LOOP -------
    while running:

        # checking events
        for event in pg.event.get():
            if event.type == QUIT:
                running = False
            if event.type == KEYDOWN:

                if event.key in key_structure_dict:  # picking up a chosen structure
                    cursor.hold = key_structure_dict[event.key]([0, 0])
                    structure_ghost = Ghost(cursor.pos, cursor.hold.surf)
                    violin_se.play()

                if event.key == K_n:
                    cursor.hold = None

                if event.key == K_SPACE:  # placing down held structure
                    place_structure()

                if event.key == K_ESCAPE:
                    running = False

        pressed_keys = pg.key.get_pressed()

        cursor.update(pressed_keys)
        screen.blit(background, (0, 0))
        for entity in structures:
            screen.blit(entity.surf, entity.rect)

        if cursor.hold is not None:
            structure_ghost.update(cursor.pos)
            screen.blit(structure_ghost.surf, structure_ghost.rect)
        screen.blit(cursor.surf, cursor.rect)
        statistics.update_stats(cursor.pos, structure_map, tile_type_map)
        screen.blit(statistics.stat_window, statistics.rect)
        pg.display.flip()
        clock.tick(TICK_RATE)
    pg.quit()
