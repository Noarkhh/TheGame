import pygame as pg
import os
from random import randint
from collections import defaultdict
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
                           K_g,
                           K_q)

SOUNDTRACK = False
MOUSE_STEERING = False
LAYOUT = pg.image.load("assets/maps/desert_river.png")
HEIGHT_TILES = LAYOUT.get_height()
WIDTH_TILES = LAYOUT.get_width()
TILE_S = 30
WIDTH_PIXELS = WIDTH_TILES * TILE_S
HEIGHT_PIXELS = HEIGHT_TILES * TILE_S
WINDOW_HEIGHT = 720
WINDOW_WIDTH = 1080
TICK_RATE = 60
TICK = 0


class Background(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.surf = generate_map()[0]
        self.rect = self.surf.get_rect()

    def move_screen(self):
        if cursor.rect.right + self.rect.left > WINDOW_WIDTH:
            self.rect.move_ip(-TILE_S / 1.5, 0)
        if cursor.rect.left + self.rect.left < 0:
            self.rect.move_ip(TILE_S / 1.5, 0)
        if cursor.rect.bottom + self.rect.top > WINDOW_HEIGHT:
            self.rect.move_ip(0, -TILE_S / 1.5)
        if cursor.rect.top + self.rect.top < 0:
            self.rect.move_ip(0, TILE_S / 1.5)


class Entities(pg.sprite.Group):
    def give_y(self, sprite):
        return sprite.pos[1]

    def draw(self, surface):
        sprites = self.sprites()
        for spr in sorted(sprites, key=lambda spr: spr.pos[1]):
            surface.blit(spr.surf, spr.rect)
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
        self.time = [0, 0]

    def update_global_stats(self):
        self.stat_window.fill((0, 0, 0))
        self.stat_window.blit(self.font.render("time: " + str(self.time[0]) + ":00  Day " + str(self.time[1]), False,
                                               (255, 255, 255), (0, 0, 0)), (0, 0))
        self.stat_window.blit(self.font.render("gold: " + str(vault.gold), False, (255, 255, 255), (0, 0, 0)), (0, 26))

        self.stat_window.set_colorkey((0, 0, 0), RLEACCEL)

    def get_time(self):
        self.tick += 1
        if self.tick >= TICK_RATE:
            self.tick = 0
            self.time[0] += 1
            if self.time[0] >= 24:
                self.time[0] = 0
                self.time[1] += 1


class TileStatistics(Statistics):
    def __init__(self):
        super().__init__()
        self.rect = self.stat_window.get_rect(bottomright=(WINDOW_WIDTH - 2, WINDOW_HEIGHT - 2))

    def update_tile_stats(self, xy, struct_map, tile_type_map):
        def blit_stat(stat):
            nonlocal stat_height
            stat_surf = self.font.render(stat, False, (255, 255, 255), (0, 0, 0))
            stat_rect = stat_surf.get_rect(bottom=self.stat_window.get_height() - stat_height,
                                           right=self.stat_window.get_width())
            self.stat_window.blit(stat_surf, stat_rect)
            stat_height += self.font_size + 4

        self.stat_window.fill((0, 0, 0))
        stat_height = 4

        if isinstance(struct_map[xy[0]][xy[1]], Structure):
            blit_stat("time left: " + str("{:.2f}".format(struct_map[xy[0]][xy[1]].time_left / TICK_RATE)) + "s")
            blit_stat("cooldown: " + str(struct_map[xy[0]][xy[1]].cooldown / TICK_RATE) + "s")
            blit_stat("profit: " + str(struct_map[xy[0]][xy[1]].profit) + "g")
            blit_stat("inside: " + str(struct_map[xy[0]][xy[1]].inside))
            blit_stat(str(type(struct_map[xy[0]][xy[1]]))[17:-2])
        blit_stat(tile_type_map[xy[0]][xy[1]])
        blit_stat(str(xy))
        self.stat_window.set_colorkey((0, 0, 0), RLEACCEL)


class Vault:
    def __init__(self):
        self.gold = 100000


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
        self.rect = surf.get_rect(bottomright=(TILE_S * (xy[0] + 1), TILE_S * (xy[1] + 1)))

    def update(self, xy, surf):
        self.position = xy
        self.rect.right = TILE_S * (xy[0] + 1)
        self.rect.bottom = TILE_S * (xy[1] + 1)
        self.surf = surf
        self.surf.set_alpha(128)


class Tile(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()


class Structure(pg.sprite.Sprite):
    def __init__(self, xy):
        super().__init__()
        self.surf = pg.Surface((TILE_S, TILE_S))
        self.surf.fill((0, 0, 0))
        self.pos = xy.copy()
        self.rect = self.surf.get_rect(bottomright=(TILE_S * (xy[0] + 1), TILE_S * (xy[1] + 1)))
        self.profit = 0
        self.cooldown = TICK_RATE * 24
        self.time_left = self.cooldown
        self.cost = 0
        self.inside = False

    def get_profit(self):
        self.time_left -= 1
        if self.time_left == 0:
            self.time_left = self.cooldown
            vault.gold += self.profit


class House(Structure):
    def __init__(self, xy):
        super().__init__(xy)
        self.surf = pg.transform.scale(pg.image.load("assets/hut1.png").convert(), (TILE_S, TILE_S))
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.cooldown = TICK_RATE * 6
        self.time_left = self.cooldown
        self.profit = 10
        self.cost = 50


class Tower(Structure):
    def __init__(self, xy):
        super().__init__(xy)
        self.surf = pg.transform.scale(pg.image.load("assets/big_tower.png").convert(), (TILE_S, 2 * TILE_S))
        self.rect = self.surf.get_rect(bottomright=(TILE_S * (xy[0] + 1), TILE_S * (xy[1] + 1)))
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)


class Snapper(Structure):
    def __init__(self, xy):
        super().__init__(xy)
        self.neighbours = set()

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
    def __init__(self, xy):
        super().__init__(xy)
        self.snapper_dict = roads_dict
        self.surf = pg.transform.scale(pg.image.load("assets/roads/road.png").convert(), (TILE_S, TILE_S))
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.snapsto = {snap: "roads" for snap in ('N', 'E', 'S', 'W')}
        self.cooldown = TICK_RATE * 48
        self.time_left = self.cooldown
        self.profit = -3
        self.cost = 10


class Wall(Snapper):
    def __init__(self, xy):
        super().__init__(xy)
        self.snapper_dict = walls_dict
        self.surf = pg.transform.scale(pg.image.load("assets/walls/wall.png").convert(), (TILE_S, TILE_S))
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.snapsto = {snap: "walls" for snap in ('N', 'E', 'S', 'W')}
        self.cooldown = TICK_RATE * 48
        self.time_left = self.cooldown
        self.profit = -3
        self.cost = 20


class Gate(Wall, Road):
    def __init__(self, xy, orientation="v"):
        super().__init__(xy)
        self.orient = orientation
        self.surf = pg.transform.scale(pg.image.load("assets/" + self.orient + "gates/gate.png").convert(),
                                       (TILE_S, TILE_S))
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        if orientation == "v":
            self.snapper_dict = vgates_dict
            self.snapsto = {'N': "roads", 'E': "walls", 'S': "roads", 'W': "walls"}
        else:
            self.snapper_dict = hgates_dict
            self.snapsto = {'N': "walls", 'E': "roads", 'S': "walls", 'W': "roads"}

        self.cooldown = TICK_RATE * 24
        self.time_left = self.cooldown
        self.profit = -15
        self.cost = 150

    def rotate(self):
        if self.orient == "v":
            self.orient = "h"
        else:
            self.orient = "v"
        self.surf = pg.transform.scale(pg.image.load("assets/" + self.orient + "gates/gate.png").convert(),
                                       (TILE_S, TILE_S))
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)


# def detect_wall_loops(xy):
#     def find_connected_nodes(A, node_xy, direction_to_xy_dict, required, current_walls, origin, i):
#         # print(current_walls, node_xy)
#         current_walls.append(node_xy)
#         if len(struct_map[node_xy[0]][node_xy[1]].neighbours) >= 3:
#             return current_walls, node_xy, True
#
#         if len(struct_map[node_xy[0]][node_xy[1]].neighbours) <= 1 or A[node_xy[0]][node_xy[1]] == False:
#             return 0, 0, False
#         A[node_xy[0]][node_xy[1]] = False
#
#         for direction in struct_map[node_xy[0]][node_xy[1]].neighbours:
#             next = direction_to_xy_dict[direction]
#             if A[node_xy[0] + next[0]][node_xy[1] + next[1]] and \
#                     bool(set(struct_map[node_xy[0] + next[0]][node_xy[1] + next[1]].snapsto.values()) & required) and \
#                     ((node_xy[0] + next[0], node_xy[1] + next[1]) != origin or i <= 0):
#                 return find_connected_nodes(A, (node_xy[0] + next[0], node_xy[1] + next[1]), direction_to_xy_dict,
#                                      required, current_walls, origin, i-1)
#         return 0, 0, False
#
#     def DFScycle(graph, v, e, visited_v, visited_e, cycle):
#         global cycle_start
#         global flag
#         flag = True
#         cycle_start = None
#         visited_v.add(v)
#         if e is not None:
#             visited_e.add(e)
#
#         for neighbour_v, neighbour_e in graph[v]:
#             if neighbour_e not in visited_e:
#                 if neighbour_v not in visited_v:
#                     if DFScycle(graph, neighbour_v, neighbour_e, visited_v, visited_e, cycle):
#                         if flag:
#                             cycle.append(neighbour_e)
#                         if v == cycle_start:
#                             flag = False
#                         return True
#                 else:
#                     cycle_start = neighbour_v
#                     cycle.append(neighbour_e)
#                     visited_e.add(neighbour_e)
#                     return True
#         return False
#
#     A = [[True if isinstance(y, Wall) else 0 for y in x] for x in struct_map]
#     B = [[1 if isinstance(y, Wall) and len(y.neighbours) >= 3 else 0 for y in x] for x in struct_map]
#     walls_in_edge = []
#     node_list = []
#     for xi, x in enumerate(B):
#         for yj, y in enumerate(x):
#             if y == 1:
#                 node_list.append((xi, yj))
#
#     edge_dict = {}
#     edge_list = []
#     graph = defaultdict(list)
#     required = set(struct_map[xy[0]][xy[1]].snapsto.values())
#     direction_to_xy_dict = {'N': (0, -1), 'E': (1, 0), 'S': (0, 1), 'W': (-1, 0)}
#
#     i = 0
#     for node in node_list:
#         for direction in struct_map[node[0]][node[1]].neighbours:
#             current_walls = walls_in_edge.copy()
#             current_walls.append(node)
#             edge, second_node, found = (find_connected_nodes(A, (node[0] + direction_to_xy_dict[direction][0],
#                                      node[1] + direction_to_xy_dict[direction][1]),
#                                  direction_to_xy_dict, required, current_walls, node, 2))
#
#             if found:
#                 if node[0] > second_node[0]:
#                     node_pair = (node, second_node)
#                 elif node[0] < second_node[0]:
#                     node_pair = (second_node, node)
#                 else:
#                     if node[1] > second_node[1]:
#                         node_pair = (node, second_node)
#                     else:
#                         node_pair = (second_node, node)
#                 if node_pair != tuple(edge):
#                     edge_dict[(node_pair, i)] = edge
#                     graph[node].append((second_node, (node_pair, i)))
#                     graph[second_node].append((node, (node_pair, i)))
#
#                     edge_list.append([(node_pair, i), "white"])
#                     i += 1
#
#     visited_e = set()
#     all_cycles = list()
#     for node in node_list:
#         # for _ in range(len(struct_map[node[0]][node[1]].neighbours)):
#         visited_v = set()
#         visited_e = set()
#         cycle = list()
#         DFScycle(graph, node, None, visited_v, visited_e, cycle)
#         if cycle not in all_cycles:
#             all_cycles.append(cycle)
#
#     for cycle in all_cycles:
#         print(cycle)
#     return graph


def detect_surrounded_tiles(xy):
    def get_wall_network(wall_map, xy, direction_to_xy_dict, required, network_list):
        wall_map[xy[0]][xy[1]] = True
        network_list.append(xy)
        for direction in struct_map[xy[0]][xy[1]].neighbours:
            next = direction_to_xy_dict[direction]
            if not wall_map[xy[0] + next[0]][xy[1] + next[1]] and \
                    bool(set(struct_map[xy[0] + next[0]][xy[1] + next[1]].snapsto.values()) & required):
                get_wall_network(wall_map, [xy[0] + next[0], xy[1] + next[1]],
                                 direction_to_xy_dict, required, network_list)

    def get_extremes(network_list):
        bottom_top_dict = defaultdict(list)
        right_left_dict = defaultdict(list)
        for elem in network_list:
            bottom_top_dict[elem[0]].append(elem)
            right_left_dict[elem[1]].append(elem)

        for curr_dict, k in ((bottom_top_dict, 1), (right_left_dict, 0)):
            for stripe, cands in curr_dict.items():
                max_y = max(cands, key=lambda xy: xy[k])
                min_y = min(cands, key=lambda xy: xy[k])
                curr_dict[stripe] = [max_y, min_y]

        return bottom_top_dict, right_left_dict

    def mark_safe_stripes(bottom_top_dict, right_left_dict, surrounded_tiles):
        for x, stripe in bottom_top_dict.items():
            for y in range(stripe[1][1], stripe[0][1] + 1):
                surrounded_tiles[x][y] += 1

        for y, stripe in right_left_dict.items():
            for x in range(stripe[1][0], stripe[0][0] + 1):
                surrounded_tiles[x][y] += 1
        return surrounded_tiles

    required = set(struct_map[xy[0]][xy[1]].snapsto.values())
    direction_to_xy_dict = {'N': (0, -1), 'E': (1, 0), 'S': (0, 1), 'W': (-1, 0)}
    wall_map = [[False for _ in range(HEIGHT_TILES)] for _ in range(WIDTH_TILES)]
    surrounded_tiles = [[0 for _ in range(HEIGHT_TILES)] for _ in range(WIDTH_TILES)]
    network_list = []

    get_wall_network(wall_map, xy, direction_to_xy_dict, required, network_list)
    bottom_top_dict, right_left_dict = get_extremes(network_list)
    return mark_safe_stripes(bottom_top_dict, right_left_dict, surrounded_tiles)


def count_road_network(xy):
    A = [[True for _ in range(HEIGHT_TILES)] for _ in range(WIDTH_TILES)]
    count = 0
    direction_to_xy_dict = {'N': (0, -1), 'E': (1, 0), 'S': (0, 1), 'W': (-1, 0)}
    required = set(struct_map[xy[0]][xy[1]].snapsto.values())

    def _count_road_network(A, xy, direction_to_xy_dict, required):
        nonlocal count
        count += 1
        A[xy[0]][xy[1]] = False
        for direction in struct_map[xy[0]][xy[1]].neighbours:
            next = direction_to_xy_dict[direction]
            if A[xy[0] + next[0]][xy[1] + next[1]] and \
                    bool(set(struct_map[xy[0] + next[0]][xy[1] + next[1]].snapsto.values()) & required):
                _count_road_network(A, [xy[0] + next[0], xy[1] + next[1]], direction_to_xy_dict, required)

    _count_road_network(A, xy, direction_to_xy_dict, required)
    return count


def fill_snappers_dicts():
    roads_dict, walls_dict, vgates_dict, hgates_dict = {}, {}, {}, {}
    for snapper_dict, snapper_dir in ((roads_dict, "assets/roads"), (walls_dict, "assets/walls"),
                                      (vgates_dict, "assets/vgates"), (hgates_dict, "assets/hgates")):
        directory = os.listdir(snapper_dir)
        dir_cut = []

        for name in directory:
            dir_cut.append(tuple(name[4:-4]))

        for file, name in zip(directory, dir_cut):
            snapper_dict[name] = pg.transform.scale(pg.image.load(snapper_dir + "/" + file).convert(), (TILE_S, TILE_S))
            snapper_dict[name].set_colorkey((255, 255, 255), RLEACCEL)
    return roads_dict, walls_dict, vgates_dict, hgates_dict


def pos_oob(x, y):
    if x < 0: return True
    if x > WIDTH_TILES - 1: return True
    if y < 0: return True
    if y > HEIGHT_TILES - 1: return True
    return False


def gate_placement_logic():
    if (isinstance(struct_map[cursor.pos[0]][cursor.pos[1]], Wall) or
        isinstance(struct_map[cursor.pos[0]][cursor.pos[1]], Road)) and \
            not isinstance(struct_map[cursor.pos[0]][cursor.pos[1]], Gate):
        new_friends = set()
        if cursor.hold.orient == "v":
            err_table = (Wall, Road, Wall, Road)
            neighbour_table = (Road, Wall, Road, Wall)
        else:
            err_table = (Road, Wall, Road, Wall)
            neighbour_table = (Wall, Road, Wall, Road)
        for direction, x, y, friend in zip(('N', 'E', 'S', 'W'), (0, -1, 0, 1), (1, 0, -1, 0), err_table):
            if not pos_oob(cursor.pos[0] + x, cursor.pos[1] + y) and \
                    type(struct_map[cursor.pos[0] + x][cursor.pos[1] + y]) == friend and \
                    direction in struct_map[cursor.pos[0] + x][cursor.pos[1] + y].neighbours:
                return False, None

        for direction, direction_rev, x, y, friend in zip(('N', 'E', 'S', 'W'), ('S', 'W', 'N', 'E'),
                                                          (0, -1, 0, 1), (1, 0, -1, 0), neighbour_table):
            if not pos_oob(cursor.pos[0] + x, cursor.pos[1] + y) and \
                    isinstance(struct_map[cursor.pos[0] + x][cursor.pos[1] + y], friend) and \
                    direction in struct_map[cursor.pos[0] + x][cursor.pos[1] + y].neighbours:
                new_friends.add(direction_rev)
        return True, new_friends
    else:
        return False, None


def place_structure(prev_pos):
    global surrounded_tiles
    if isinstance(cursor.hold, Structure):
        built, snapped = False, False
        if tile_type_map[cursor.pos[0]][cursor.pos[1]] != "sea" or isinstance(cursor.hold, Road):
            if cursor.hold.cost <= vault.gold:
                if not isinstance(struct_map[cursor.pos[0]][cursor.pos[1]], Structure):

                    if isinstance(cursor.hold, Gate):
                        new_struct = type(cursor.hold)(cursor.pos, cursor.hold.orient)
                    else:
                        new_struct = type(cursor.hold)(cursor.pos)
                    # structs_group_dict[type(cursor.hold)].add(new_struct)
                    structs.add(new_struct)
                    entities.add(new_struct)
                    struct_map[cursor.pos[0]][cursor.pos[1]] = new_struct
                    built = True

                elif isinstance(cursor.hold, Gate):
                    passed, new_friends = gate_placement_logic()
                    if passed:
                        new_struct = type(cursor.hold)(cursor.pos, cursor.hold.orient)
                        # structs_group_dict[type(cursor.hold)].add(new_struct)
                        structs.add(new_struct)
                        entities.add(new_struct)
                        struct_map[cursor.pos[0]][cursor.pos[1]].kill()
                        struct_map[cursor.pos[0]][cursor.pos[1]] = new_struct
                        struct_map[cursor.pos[0]][cursor.pos[1]].update_edges(tuple(new_friends), True)
                        built = True
                    elif not place_hold:
                        speech_channel.play(sounds["Placement_Warning16"])
            elif not place_hold:
                speech_channel.play(sounds["Resource_Need" + str(randint(17, 19))])
        elif not isinstance(struct_map[cursor.pos[0]][cursor.pos[1]], Snapper) and not place_hold:
            speech_channel.play(sounds["Placement_Warning16"])

        change = tuple([a - b for a, b in zip(cursor.pos, prev_pos)])
        pos_change_dict = {(0, 1): ('N', 'S'), (-1, 0): ('E', 'W'), (0, -1): ('S', 'N'), (1, 0): ('W', 'E')}

        if isinstance(cursor.hold, Snapper) and change in pos_change_dict.keys() and place_hold and \
                isinstance(struct_map[cursor.pos[0]][cursor.pos[1]], Snapper) and \
                isinstance(struct_map[prev_pos[0]][prev_pos[1]], Snapper):
            if struct_map[cursor.pos[0]][cursor.pos[1]].snapsto[pos_change_dict[change][0]] == \
                    struct_map[prev_pos[0]][prev_pos[1]].snapsto[pos_change_dict[change][1]]:
                struct_map[cursor.pos[0]][cursor.pos[1]].update_edges(pos_change_dict[change][0], True)
                struct_map[prev_pos[0]][prev_pos[1]].update_edges(pos_change_dict[change][1], True)
                snapped = True

        if built or snapped:
            sounds["drawbridge_control"].play()
        if built:
            vault.gold -= new_struct.cost
            if isinstance(new_struct, Wall):
                surrounded_tiles = detect_surrounded_tiles(cursor.pos)
                for x in surrounded_tiles:
                    print(x)
                print("\n\n")
    return


def remove_structure():
    if isinstance(struct_map[cursor.pos[0]][cursor.pos[1]], Structure):
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
    if SOUNDTRACK:
        tracks = [pg.mixer.Sound("assets/soundtrack/" + file) for file in soundtrack_dir]
    else:
        tracks = []
    for track in tracks:
        track.set_volume(0.4)
    for sound in sounds.values():
        sound.set_volume(0.7)

    return sounds, tracks


def play_soundtrack():
    if not soundtrack_channel.get_busy():
        soundtrack_channel.play(tracks[randint(0, 13)])


if __name__ == "__main__":
    global surrounded_tiles
    surrounded_tiles = [[0 for _ in range(HEIGHT_TILES)] for _ in range(WIDTH_TILES)]

    pg.init()
    pg.mixer.init()

    sounds, tracks = load_sounds()
    soundtrack_channel = pg.mixer.Channel(5)
    speech_channel = pg.mixer.Channel(3)

    # screen = pg.display.set_mode([WIDTH_PIXELS, HEIGHT_PIXELS])
    screen = pg.display.set_mode([WINDOW_WIDTH, WINDOW_HEIGHT])
    cursor = Cursor()
    tile_statistics = TileStatistics()
    global_statistics = GlobalStatistics()
    vault = Vault()
    struct_map = [[0 for _ in range(HEIGHT_TILES)] for _ in range(WIDTH_TILES)]

    roads_dict, walls_dict, vgates_dict, hgates_dict = fill_snappers_dicts()
    prev_pos = (0, 0)
    map_surf, tile_type_map = generate_map()
    background = Background()

    pg.display.set_caption("Twierdza: Zawodzie")

    entities = Entities()
    # houses = pg.sprite.Group()
    # towers = pg.sprite.Group()
    # roads = pg.sprite.Group()
    # walls = pg.sprite.Group()
    structs = pg.sprite.Group()
    # gates = pg.sprite.Group()
    # entities = pg.sprite.Group()

    clock = pg.time.Clock()
    key_structure_dict = {K_h: House, K_t: Tower, K_r: Road, K_w: Wall, K_g: Gate}
    # structs_group_dict = {House: houses, Tower: towers, Road: roads, Wall: walls, Gate: gates}
    running = True
    # ------ MAIN LOOP -------
    while running:

        pressed_keys = pg.key.get_pressed()
        # checking events
        if MOUSE_STEERING:
            cursor.update_mouse(pg.mouse.get_pos())
        else:
            cursor.update_arrows(pressed_keys)

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

                if event.key == K_ESCAPE:
                    running = False

                if event.key == K_q and isinstance(cursor.hold, Gate):
                    cursor.hold.rotate()

                if event.key == pg.K_c and isinstance((struct_map[cursor.pos[0]][cursor.pos[1]]), Snapper):
                    print(count_road_network(cursor.pos))

                if event.key == pg.K_j and isinstance((struct_map[cursor.pos[0]][cursor.pos[1]]), Wall):
                    for x in surrounded_tiles:
                        print(x)

        if pressed_keys[K_SPACE] or pg.mouse.get_pressed(num_buttons=3)[0]:  # placing down held structure
            place_structure(prev_pos)
            place_hold = True
        else:
            place_hold = False

        prev_pos = tuple(cursor.pos)
        if pressed_keys[K_x]:  # removing a structure
            remove_structure()

        background.move_screen()

        for struct in structs:
            struct.get_profit()
            if surrounded_tiles[struct.pos[0]][struct.pos[1]] == 2:
                struct.inside = True
        if vault.gold < 0:
            running = False

        entities.draw(background.surf)

        if cursor.hold is not None:
            structure_ghost.update(cursor.pos, cursor.hold.surf)
            background.surf.blit(structure_ghost.surf, structure_ghost.rect)

        background.surf.blit(cursor.surf, cursor.rect)

        if SOUNDTRACK:
            play_soundtrack()
        if randint(1, 100000) == 1: sounds["Random_Events13"].play()

        screen.fill((0, 0, 0))
        screen.blit(background.surf, background.rect)

        global_statistics.get_time()
        global_statistics.update_global_stats()
        screen.blit(global_statistics.stat_window, global_statistics.rect)

        tile_statistics.update_tile_stats(cursor.pos, struct_map, tile_type_map)
        screen.blit(tile_statistics.stat_window, tile_statistics.rect)

        background.surf.blit(map_surf, (0, 0))
        pg.display.flip()
        clock.tick(TICK_RATE)
    pg.quit()
