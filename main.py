import pygame as pg
import os
from random import randint
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
                           K_n,
                           K_x,
                           K_w,
                           K_g)

MOUSE_STEERING = False
LAYOUT = pg.image.load("assets/desert_river.png")
HEIGHT_TILES = LAYOUT.get_height()
WIDTH_TILES = LAYOUT.get_width()
TILE_S = 45
WIDTH_PIXELS = WIDTH_TILES * TILE_S
HEIGHT_PIXELS = HEIGHT_TILES * TILE_S
TICK_RATE = 30


class Statistics:
    def __init__(self):
        self.font_size = 24
        self.stat_window = pg.Surface((self.font_size * 20, self.font_size * 10))
        self.stat_window.fill((0, 0, 0))
        self.font = pg.font.SysFont('consolas', self.font_size)
        self.rect = self.stat_window.get_rect(bottom=HEIGHT_PIXELS - 2, right=WIDTH_PIXELS - 4)

    def update_stats(self, xy, structure_map, tile_type_map):
        def blit_stat(stat):
            nonlocal stat_height
            stat_surf = self.font.render(stat, False, (255, 255, 255), (0, 0, 0))
            stat_rect = stat_surf.get_rect(bottom=self.stat_window.get_height() - stat_height,
                                           right=self.stat_window.get_width())
            self.stat_window.blit(stat_surf, stat_rect)
            stat_height += self.font_size + 4

        self.stat_window.fill((0, 0, 0))
        stat_height = 4

        if isinstance(structure_map[xy[0]][xy[1]], Structure):
            blit_stat(str(type(structure_map[xy[0]][xy[1]]))[17:-2])
        blit_stat(tile_type_map[xy[0]][xy[1]])
        blit_stat(str(xy))
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

    def update_arrows(self, pressed_keys):
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
        bruh = False
        if self.pos[0] < 0:
            self.pos[0] = 0
            bruh = True
        if self.pos[0] > WIDTH_TILES - 1:
            self.pos[0] = WIDTH_TILES - 1
            bruh = True
        if self.pos[1] < 0:
            self.pos[1] = 0
            bruh = True
        if self.pos[1] > HEIGHT_TILES - 1:
            self.pos[1] = HEIGHT_TILES - 1
            bruh = True
        if bruh:
            speech_channel.play(sounds["Insult" + str(randint(1, 20))])

        self.cooldown = [x - 1 if x > 0 else 0 for x in self.cooldown]
        self.rect.x = self.pos[0] * TILE_S
        self.rect.y = self.pos[1] * TILE_S

    def update_mouse(self, xy):
        self.pos[0] = xy[0] // TILE_S
        self.pos[1] = xy[1] // TILE_S
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


class Snapper(Structure):
    def __init__(self, xy):
        super().__init__(xy)
        self.neighbours = set()

    def update_edges(self, direction, add):
        if add:
            self.neighbours.add(direction)
        elif direction in self.neighbours:
            self.neighbours.remove(direction)

        def assign_value(direct):
            if direct == 'N': return 0
            if direct == 'E': return 1
            if direct == 'S': return 2
            if direct == 'W': return 3

        directions = tuple(sorted(self.neighbours, key=assign_value))
        if not directions:
            directions = ('0',)
        self.surf = self.snapper_dict[directions]


class Road(Snapper):
    def __init__(self, xy):
        super().__init__(xy)
        self.snapper_dict = roads_dict
        self.surf = pg.transform.scale(pg.image.load("assets/roads/road0.png").convert(), (TILE_S, TILE_S))
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)


class Wall(Snapper):
    def __init__(self, xy):
        super().__init__(xy)
        self.snapper_dict = walls_dict
        self.surf = pg.transform.scale(pg.image.load("assets/walls/wall0.png").convert(), (TILE_S, TILE_S))
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.isgate = ""
        self.hasroad = False

    def gate_upgrade(self):
        if self.neighbours == {'E', 'W'}:
            self.surf = pg.transform.scale(pg.image.load("assets/gateEW.png").convert(), (TILE_S, TILE_S))
            self.isgate = "EW"
            sounds["drawbridge_control"].play()
        elif self.neighbours == {'N', 'S'}:
            self.surf = pg.transform.scale(pg.image.load("assets/gateNS.png").convert(), (TILE_S, TILE_S))
            self.isgate = "NS"
            sounds["drawbridge_control"].play()
        else:
            speech_channel.play(sounds["Placement_Warning16"])
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)

    def add_road(self):
        self.surf = pg.transform.scale(pg.image.load("assets/gate" + self.isgate + "road.png").convert(),
                                       (TILE_S, TILE_S))
        self.hasroad = True
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)


def count_road_network(xy):
    A = [[True for _ in range(HEIGHT_TILES)] for _ in range(WIDTH_TILES)]
    count = 0
    direction_to_xy_dict = {'N': (0, -1), 'E': (1, 0), 'S': (0, 1), 'W': (-1, 0)}

    def _count_road_network(A, xy, direction_to_xy_dict):
        nonlocal count
        count += 1
        A[xy[0]][xy[1]] = False
        for direction in struct_map[xy[0]][xy[1]].neighbours:
            next = direction_to_xy_dict[direction]
            if A[xy[0] + next[0]][xy[1] + next[1]]:
                _count_road_network(A, [xy[0] + next[0], xy[1] + next[1]], direction_to_xy_dict)

    _count_road_network(A, xy, direction_to_xy_dict)
    return count


def fill_snappers_dicts():
    roads_dict, walls_dict = {}, {}
    for snapper_dict, snapper_dir in ((roads_dict, "assets/roads"), (walls_dict, "assets/walls")):
        directory = os.listdir(snapper_dir)
        dir_cut = []

        for name in directory:
            dir_cut.append(tuple(name[4:-4]))

        for file, name in zip(directory, dir_cut):
            snapper_dict[name] = pg.transform.scale(pg.image.load(snapper_dir + "/" + file).convert(), (TILE_S, TILE_S))
            snapper_dict[name].set_colorkey((255, 255, 255), RLEACCEL)
    return roads_dict, walls_dict


def pos_oob(x, y):
    if x < 0: return True
    if x > WIDTH_TILES - 1: return True
    if y < 0: return True
    if y > HEIGHT_TILES - 1: return True
    return False


def place_structure(prev_pos):
    if isinstance(cursor.hold, Structure):
        built = False
        if struct_map[cursor.pos[0]][cursor.pos[1]] not in structs and \
                (tile_type_map[cursor.pos[0]][cursor.pos[1]] != "sea" or isinstance(cursor.hold, Road)):
            new_struct = type(cursor.hold)(cursor.pos)
            structs_group_dict[type(cursor.hold)].add(new_struct)
            structs.add(new_struct)
            all_sprites.add(new_struct)
            struct_map[cursor.pos[0]][cursor.pos[1]] = new_struct
            built = True
        elif not isinstance(struct_map[cursor.pos[0]][cursor.pos[1]], Snapper) and not place_hold:
            speech_channel.play(sounds["Placement_Warning16"])

        change = tuple([a - b for a, b in zip(cursor.pos, prev_pos)])
        pos_change_dict = {(0, 1): ('N', 'S'), (-1, 0): ('E', 'W'), (0, -1): ('S', 'N'), (1, 0): ('W', 'E')}

        if isinstance(cursor.hold, Snapper) and change in pos_change_dict.keys() and place_hold and \
                isinstance(struct_map[cursor.pos[0]][cursor.pos[1]], Snapper) and \
                isinstance(struct_map[prev_pos[0]][prev_pos[1]], Snapper):

            if type(struct_map[cursor.pos[0]][cursor.pos[1]]) == type(struct_map[prev_pos[0]][prev_pos[1]]):
                struct_map[cursor.pos[0]][cursor.pos[1]].update_edges(pos_change_dict[change][0], True)
                struct_map[prev_pos[0]][prev_pos[1]].update_edges(pos_change_dict[change][1], True)
                built = True
            elif isinstance(struct_map[prev_pos[0]][prev_pos[1]], Road) and \
                    isinstance(struct_map[cursor.pos[0]][cursor.pos[1]], Wall) and \
                    struct_map[cursor.pos[0]][cursor.pos[1]].isgate:

                struct_map[cursor.pos[0]][cursor.pos[1]].add_road()
                struct_map[prev_pos[0]][prev_pos[1]].update_edges(pos_change_dict[change][1], True)
                built = True
            elif isinstance(struct_map[prev_pos[0]][prev_pos[1]], Wall) and \
                    isinstance(struct_map[cursor.pos[0]][cursor.pos[1]], Road) and \
                    struct_map[prev_pos[0]][prev_pos[1]].isgate:

                struct_map[prev_pos[0]][prev_pos[1]].add_road()
                struct_map[cursor.pos[0]][cursor.pos[1]].update_edges(pos_change_dict[change][0], True)
                built = True
        if built:
            sounds["drawbridge_control"].play()
    return


def remove_structure():
    if struct_map[cursor.pos[0]][cursor.pos[1]] in structs:
        sounds["buildingwreck_01"].play()

        for direction, x, y in zip(('N', 'E', 'S', 'W'), (0, -1, 0, 1), (1, 0, -1, 0)):
            if not pos_oob(cursor.pos[0] + x, cursor.pos[1] + y) and \
                    isinstance(struct_map[cursor.pos[0] + x][cursor.pos[1] + y], Snapper) and \
                    (type(struct_map[cursor.pos[0] + x][cursor.pos[1] + y]) ==
                     type(struct_map[cursor.pos[0]][cursor.pos[1]]) or
                     isinstance(struct_map[cursor.pos[0]][cursor.pos[1]], Wall)):
                struct_map[cursor.pos[0] + x][cursor.pos[1] + y].update_edges(direction, False)

        struct_map[cursor.pos[0]][cursor.pos[1]].kill()
        struct_map[cursor.pos[0]][cursor.pos[1]] = 0


def generate_map():
    color_to_type = {(0, 255, 0, 255): "grassland", (0, 0, 255, 255): "sea", (255, 255, 0, 255): "desert"}
    tile_dict = {name: pg.transform.scale(pg.image.load("assets/tiles/" + name + "_tile.png").convert(),
                                          (TILE_S, TILE_S)) for name in color_to_type.values()}

    background = pg.Surface((WIDTH_TILES * TILE_S, HEIGHT_TILES * TILE_S))
    tile_map = [[0 for _ in range(HEIGHT_TILES)] for _ in range(WIDTH_TILES)]

    for x in range(WIDTH_TILES):
        for y in range(HEIGHT_TILES):
            tile_color = tuple(LAYOUT.get_at((x, y)))
            background.blit(tile_dict[color_to_type[tile_color]], (x * TILE_S, y * TILE_S))
            tile_map[x][y] = color_to_type[tile_color]
    return background, tile_map


def load_sounds():
    fx_dir = os.listdir("assets/fx")
    soundtrack_dir = os.listdir("assets/soundtrack")
    sounds = {file[:-4]: pg.mixer.Sound("assets/fx/" + file) for file in fx_dir}
    tracks = [pg.mixer.Sound("assets/soundtrack/" + file) for file in soundtrack_dir]
    for track in tracks:
        track.set_volume(0.4)
    for sound in sounds.values():
        sound.set_volume(0.7)

    return sounds, tracks


def play_soundtrack():
    if not soundtrack_channel.get_busy():
        soundtrack_channel.play(tracks[randint(0, 13)])


if __name__ == "__main__":
    pg.init()
    pg.mixer.init()

    sounds, tracks = load_sounds()
    soundtrack_channel = pg.mixer.Channel(5)
    speech_channel = pg.mixer.Channel(3)

    screen = pg.display.set_mode([WIDTH_PIXELS, HEIGHT_PIXELS])
    cursor = Cursor()
    statistics = Statistics()
    struct_map = [[0 for _ in range(HEIGHT_TILES)] for _ in range(WIDTH_TILES)]

    roads_dict, walls_dict = fill_snappers_dicts()
    prev_pos = (0, 0)
    background, tile_type_map = generate_map()

    pg.display.set_caption("Twierdza: Zawodzie")

    houses = pg.sprite.Group()
    towers = pg.sprite.Group()
    roads = pg.sprite.Group()
    walls = pg.sprite.Group()
    structs = pg.sprite.Group()
    all_sprites = pg.sprite.Group()

    all_sprites.add(cursor)

    clock = pg.time.Clock()
    key_structure_dict = {K_h: House, K_t: Tower, K_r: Road, K_w: Wall}
    structs_group_dict = {House: houses, Tower: towers, Road: roads, Wall: walls}
    running = True
    # ------ MAIN LOOP -------
    while running:

        pressed_keys = pg.key.get_pressed()
        # checking events
        for event in pg.event.get():
            if event.type == QUIT:
                running = False
            if event.type == KEYDOWN:

                if event.key in key_structure_dict:  # picking up a chosen structure
                    cursor.hold = key_structure_dict[event.key]([0, 0])
                    structure_ghost = Ghost(cursor.pos, cursor.hold.surf)
                    sounds["menusl_" + str(randint(1, 3))].play()
                    # violin_se.play()

                if event.key == K_n:
                    cursor.hold = None

                if event.key == K_g and isinstance(struct_map[cursor.pos[0]][cursor.pos[1]], Wall):
                    struct_map[cursor.pos[0]][cursor.pos[1]].gate_upgrade()

                if event.key == K_ESCAPE:
                    running = False

                if event.key == pg.K_c:
                    print(count_road_network(cursor.pos))

        if pressed_keys[K_SPACE] or pg.mouse.get_pressed(num_buttons=3)[0]:  # placing down held structure
            place_structure(prev_pos)
            place_hold = True
        else:
            place_hold = False

        prev_pos = tuple(cursor.pos)
        if pressed_keys[K_x]:  # removing a structure
            remove_structure()
        if MOUSE_STEERING:
            cursor.update_mouse(pg.mouse.get_pos())
        else:
            cursor.update_arrows(pressed_keys)
        screen.blit(background, (0, 0))
        # print(prev_pos, cursor.pos)

        for entity in structs:
            screen.blit(entity.surf, entity.rect)

        if cursor.hold is not None:
            structure_ghost.update(cursor.pos)
            screen.blit(structure_ghost.surf, structure_ghost.rect)

        screen.blit(cursor.surf, cursor.rect)
        statistics.update_stats(cursor.pos, struct_map, tile_type_map)
        screen.blit(statistics.stat_window, statistics.rect)

        play_soundtrack()
        if randint(1, 100000) == 1: sounds["Random_Events13"].play()
        pg.display.flip()
        clock.tick(TICK_RATE)
    pg.quit()
