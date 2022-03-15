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

HEIGHT_TILES = 12
WIDTH_TILES = 18
TILE_SIZE = 60
TICK_RATE = 20


class Cursor(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.windup = [0 for _ in range(4)]
        self.cooldown = [0 for _ in range(4)]
        self.surf = pg.image.load("assets/cursor3.png").convert()
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.surf.get_rect()
        self.position = [0, 0]
        self.holding = None

    def update(self, pressed_keys):
        cooltime = 10
        key_list = [True if pressed_keys[key] else False for key in (K_UP, K_DOWN, K_LEFT, K_RIGHT)]
        iter_list = [(key, sign, xy) for key, sign, xy in zip(key_list, (-1, 1, -1, 1), (1, 1, 0, 0))]
        for i, elem in enumerate(iter_list):
            if elem[0]:
                if self.cooldown[i] <= self.windup[i]:
                    if self.windup[i] < cooltime: self.windup[i] += 4
                    self.position[elem[2]] += elem[1]
                    self.cooldown[i] = cooltime
            else:
                self.windup[i] = 0
                self.cooldown[i] = 0

        if self.position[0] < 0:
            self.position[0] = 0
            bruh_se.play()
        if self.position[0] > WIDTH_TILES - 1:
            self.position[0] = WIDTH_TILES - 1
            bruh_se.play()
        if self.position[1] < 0:
            self.position[1] = 0
            bruh_se.play()
        if self.position[1] > HEIGHT_TILES - 1:
            self.position[1] = HEIGHT_TILES - 1
            bruh_se.play()

        self.cooldown = [x - 1 if x > 0 else 0 for x in self.cooldown]
        self.rect.x = self.position[0] * TILE_SIZE
        self.rect.y = self.position[1] * TILE_SIZE


class Ghost(pg.sprite.Sprite):
    def __init__(self, xy, surf):
        super().__init__()
        self.surf = surf
        self.surf.set_alpha(128)
        self.position = xy
        self.rect = surf.get_rect(top=(TILE_SIZE * xy[1]), left=(TILE_SIZE * xy[0]))

    def update(self, xy):
        self.position = xy
        self.rect.x = xy[0] * TILE_SIZE
        self.rect.y = xy[1] * TILE_SIZE


class Structure(pg.sprite.Sprite):
    def __init__(self, xy):
        super().__init__()
        self.surf = pg.Surface((60, 60))
        self.surf.fill((0, 0, 0))
        self.position = xy
        self.rect = self.surf.get_rect(top=(TILE_SIZE * xy[1]), left=(TILE_SIZE * xy[0]))


class House(Structure):
    def __init__(self, xy):
        super().__init__(xy)
        self.surf = pg.image.load("assets/hut1.png").convert()
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
        self.surf = pg.image.load("assets/tower.png").convert()
        self.surf.set_colorkey((0, 0, 0), RLEACCEL)


class Road(Structure):
    def __init__(self, xy):
        super().__init__(xy)
        self.neighbours = set()
        self.surf = pg.transform.scale(pg.image.load("assets/roads/road0.png").convert(), (60, 60))
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
        roads_list[name] = pg.transform.scale(pg.image.load("assets/roads/" + file).convert(), (60, 60))
        roads_list[name].set_colorkey((255, 255, 255), RLEACCEL)

    return roads_list


if __name__ == "__main__":
    pg.init()
    pg.mixer.init()
    boom_se = pg.mixer.Sound("assets/boom sound effect.ogg")
    bruh_se = pg.mixer.Sound("assets/bruh sound effect.ogg")
    violin_se = pg.mixer.Sound("assets/violin screech sound effect.ogg")

    screen = pg.display.set_mode([1080, 720])
    cursor = Cursor()
    game_board = [[0 for _ in range(HEIGHT_TILES)] for _ in range(WIDTH_TILES)]


    # print(directions_list)
    roads_list = fill_roads_list()

    background = pg.image.load("assets/background.png").convert()
    houses = pg.sprite.Group()
    towers = pg.sprite.Group()
    roads = pg.sprite.Group()
    structures = pg.sprite.Group()
    all_sprites = pg.sprite.Group()
    all_sprites.add(cursor)

    clock = pg.time.Clock()
    key_structure_dict = {K_h: House, K_t: Tower, K_r: Road}
    structure_group_dict = {House: houses, Tower: towers, Road: roads}
    # i = 0
    running = True
    # ------ MAIN LOOP -------
    while running:

        # checking events
        for event in pg.event.get():
            if event.type == QUIT:
                running = False
            if event.type == KEYDOWN:

                if event.key in key_structure_dict:  # picking up a chosen structure
                    cursor.holding = key_structure_dict[event.key]([0, 0])
                    structure_ghost = Ghost(cursor.position, cursor.holding.surf)
                    violin_se.play()
                if event.key == K_n:
                    cursor.holding = None
                if event.key == K_SPACE:  # placing down held structure
                    if isinstance(cursor.holding, Structure):
                        if game_board[cursor.position[0]][cursor.position[1]] not in structures:
                            new_structure = type(cursor.holding)(cursor.position)
                            structure_group_dict[type(cursor.holding)].add(new_structure)
                            structures.add(new_structure)
                            all_sprites.add(new_structure)
                            game_board[new_structure.position[0]][new_structure.position[1]] = new_structure
                            boom_se.play()

                            if isinstance(new_structure, Road):
                                for direction, direction_rev, x, y in zip(('N', 'E', 'S', 'W'), ('S', 'W', 'N', 'E'),
                                                          (0, -1, 0, 1), (1, 0, -1, 0)):
                                    if isinstance(game_board[cursor.position[0] + x][cursor.position[1] + y], Road):
                                        game_board[cursor.position[0] + x][cursor.position[1] + y].\
                                                   update_edges(direction, roads_list)
                                        new_structure.update_edges(direction_rev, roads_list)
                            else:
                                cursor.holding = None
                        else:
                            bruh_se.play()

                if event.key == K_ESCAPE:
                    running = False

        pressed_keys = pg.key.get_pressed()

        cursor.update(pressed_keys)
        screen.blit(background, (0, 0))
        for entity in structures:
            screen.blit(entity.surf, entity.rect)

        if cursor.holding is not None:
            structure_ghost.update(cursor.position)
            screen.blit(structure_ghost.surf, structure_ghost.rect)
        screen.blit(cursor.surf, cursor.rect)

        # screen.blit(roads_list[directions_list[i]], (180, 180))
        # i += 1

        pg.display.flip()
        clock.tick(TICK_RATE)
    pg.quit()
