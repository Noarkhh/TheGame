from collections import defaultdict
from structures import *


def detect_surrounded_tiles(gw):
    """
    Function that detects which tiles are inside walls.
    The process is done in 4 steps for each separate wall network:

    1. Finding wall crossroads in a wall network or, if unable, determines if the network
       is a simple perimeter or a line. This step is required for step 2 to work correctly.
    2. Finding all walls in a network that are not dead ends and adding them to the wall network set.
    3. Finding the highest, lowest, leftmost and rightmost walls in a wall network and adding them to dictionaries
    4. Marking all tiles between highest and lowest walls in the network, repeating the process for
       leftmost and rightmost. If a tile has been marked both times, it is now considered surrounded.

    This sequence is repeated until there are no more walls left to check, the information
    is saved in gw.surrounded_tiles.

        :param gw: Gameworld object
    """

    def search_for_crossroads(gw, xy, prev, direction_to_xy_dict, required, network_set, open_network_set, wall_map):
        wall_map[xy[0]][xy[1]] = True
        network_set.add(xy)
        open_network_set.add(xy)
        if len(gw.struct_map[xy[0]][xy[1]].neighbours) >= 3:
            network_set.clear()
            open_network_set.clear()
            return xy, True, False
        if len(gw.struct_map[xy[0]][xy[1]].neighbours) == 1:
            return None, False, False

        for direction in gw.struct_map[xy[0]][xy[1]].neighbours:
            next = direction_to_xy_dict[direction]
            curr = tuple([a * -1 for a in next])
            if isinstance(gw.struct_map[xy[0] + next[0]][xy[1] + next[1]], Wall) and \
                    bool(set(gw.struct_map[xy[0] + next[0]][xy[1] + next[1]].snapsto.values()) & required):
                if not wall_map[xy[0] + next[0]][xy[1] + next[1]]:
                    start, found, perimeter = search_for_crossroads(gw, (xy[0] + next[0], xy[1] + next[1]), curr,
                                                                    direction_to_xy_dict, required, network_set,
                                                                    open_network_set, wall_map)
                    if found:
                        return start, True, perimeter
                elif next != prev:
                    return (xy[0] + next[0], xy[1] + next[1]), True, True
        return None, False, False

    def get_wall_network(gw, xy, direction_to_xy_dict, required, network_set, open_network_set, wall_map):
        wall_map[xy[0]][xy[1]] = True
        network_set.add(xy)
        open_network_set.add(xy)
        # print(xy, network_set)

        if len(gw.struct_map[xy[0]][xy[1]].neighbours) == 1:
            network_set.remove(xy)
            return True

        for direction in gw.struct_map[xy[0]][xy[1]].neighbours:
            next = direction_to_xy_dict[direction]
            # curr = tuple([a * -1 for a in next])
            # print(xy, next, prev)
            if bool(set(gw.struct_map[xy[0] + next[0]][xy[1] + next[1]].snapsto.values()) & required):
                if not wall_map[xy[0] + next[0]][xy[1] + next[1]]:
                    if get_wall_network(gw, (xy[0] + next[0], xy[1] + next[1]),
                                        direction_to_xy_dict, required, network_set, open_network_set, wall_map):
                        if len(gw.struct_map[xy[0]][xy[1]].neighbours) <= 2:
                            network_set.remove(xy)
                            # print("rm: ", xy)
                            return True
        return False

    def get_extremes(network_set):
        # print(network_set)
        bottom_top_dict = defaultdict(list)
        right_left_dict = defaultdict(list)
        for elem in network_set:
            bottom_top_dict[elem[0]].append(elem)
            right_left_dict[elem[1]].append(elem)

        for curr_dict, k in ((bottom_top_dict, 1), (right_left_dict, 0)):
            for stripe, cands in curr_dict.items():
                max_y = max(cands, key=lambda xy: xy[k])
                min_y = min(cands, key=lambda xy: xy[k])
                curr_dict[stripe] = [max_y, min_y]

        return bottom_top_dict, right_left_dict

    def mark_safe_stripes(gw, bottom_top_dict, right_left_dict):
        for x, stripe in bottom_top_dict.items():
            for y in range(stripe[1][1], stripe[0][1] + 1):
                gw.surrounded_tiles[x][y] += 1

        for y, stripe in right_left_dict.items():
            for x in range(stripe[1][0], stripe[0][0] + 1):
                gw.surrounded_tiles[x][y] += 1
        return

    required = {"walls"}
    direction_to_xy_dict = {'N': (0, -1), 'E': (1, 0), 'S': (0, 1), 'W': (-1, 0)}
    wall_map = [[False for _ in range(gw.height_tiles)] for _ in range(gw.width_tiles)]
    gw.surrounded_tiles[0:-1] = [[0 for _ in range(gw.height_tiles)] for _ in range(gw.width_tiles)]
    wall_set_copy = gw.wall_set.copy()

    while wall_set_copy:
        network_set = set()
        open_network_set = set()
        start, not_line, perimeter = search_for_crossroads(gw, tuple(wall_set_copy)[0], (0, 0),
                                                           direction_to_xy_dict, required, network_set,
                                                           open_network_set, wall_map)
        line = not not_line
        if not line:
            if not perimeter:
                for wall in gw.wall_set:
                    wall_map[wall[0]][wall[1]] = False
                get_wall_network(gw, tuple(start), direction_to_xy_dict,
                                 required, network_set, open_network_set, wall_map)
            bottom_top_dict, right_left_dict = get_extremes(network_set)
            mark_safe_stripes(gw, bottom_top_dict, right_left_dict)
        # wall_map = [[False for _ in range(gw.height_tiles)] for _ in range(gw.width_tiles)]
        for wall in gw.wall_set:
            wall_map[wall[0]][wall[1]] = False
        wall_set_copy -= open_network_set

    return


def count_road_network(gw, xy):
    """
    Function that counts how many roads are in a network with the selected road.

        :param gw: Gameworld object
        :param xy: Coordinates of the selected road
    """
    A = [[True for _ in range(gw.height_tiles)] for _ in range(gw.width_tiles)]
    count = 0
    direction_to_xy_dict = {'N': (0, -1), 'E': (1, 0), 'S': (0, 1), 'W': (-1, 0)}
    required = set(gw.struct_map[xy[0]][xy[1]].snapsto.values())

    def _count_road_network(gw, A, xy, direction_to_xy_dict, required):
        nonlocal count
        count += 1
        A[xy[0]][xy[1]] = False
        for direction in gw.struct_map[xy[0]][xy[1]].neighbours:
            next = direction_to_xy_dict[direction]
            if A[xy[0] + next[0]][xy[1] + next[1]] and \
                    bool(set(gw.struct_map[xy[0] + next[0]][xy[1] + next[1]].snapsto.values()) & required):
                _count_road_network(gw, A, [xy[0] + next[0], xy[1] + next[1]], direction_to_xy_dict, required)

    _count_road_network(gw, A, xy, direction_to_xy_dict, required)
    return count


def place_structure(gw, is_lmb_held_down):
    """
    Function responsible for placing structures on the map.
    The structure that will be tested for placement is the one held by the gw.cursor.
    The tile that the structure will be tested for placement on is the one that the gw.cursor's on.

    Logic:
    - The structure cannot be placed on water tiles unless it's a Road.
    - The structure cannot be placed if it can't be afforded.
    - The structure cannot be placed on another structure unless the structure that is
      being placed is a Gate and it's being placed on a Road or a Wall.
      > If the latter is the case, then the gate and the structure it's being placed on
       have to be in the right orientation so that the placement is valid.

    - If the structure is a Snapper and the conditions are met, two neighbouring Snappers can connect.
      > The placement key had to be held down while the gw.cursor was moving between two tiles.
      > The snapper on the previous tile must be able to snap to the snapper on the current tile, and vice versa.
        The validity is determined by both snappers' attributes snapsto.

    If the requirements to place the structure have been met, it's added to gw.entities, gw.structs and
    corresponding tile in gw.struct_map now references it.
    If the requirements to snap two structure have been met, their sprites and neighbours attributes are updated.

    If a structure has been placed or two structures were snapped, a building sound effect is played.

        :param gw: Gameworld object
        :param is_lmb_held_down: A variable that indicates whether the place key is being held down
    """

    new_struct = None
    change = tuple([a - b for a, b in zip(gw.cursor.pos, gw.cursor.previous_pos)])
    pos_change_dict = {(0, 1): ('N', 'S'), (-1, 0): ('E', 'W'), (0, -1): ('S', 'N'), (1, 0): ('W', 'E')}

    was_built, build_message = gw.cursor.held_structure.can_be_placed(gw, is_lmb_held_down)
    if was_built:
        if build_message == "was_built":
            new_struct = type(gw.cursor.held_structure)(gw.cursor.pos, gw, gw.cursor.held_structure.orientation)
            gw.structs.add(new_struct)
            gw.entities.add(new_struct)
            for rel in new_struct.covered_tiles:
                gw.struct_map[gw.cursor.pos[0] + rel[0]][gw.cursor.pos[1] + rel[1]] = new_struct
        if build_message == "was_overridden":
            new_struct = type(gw.cursor.held_structure)(gw.cursor.pos, gw, gw.cursor.held_structure.orientation)
            gw.structs.add(new_struct)
            gw.entities.add(new_struct)

            gw.struct_map[gw.cursor.pos[0]][gw.cursor.pos[1]].kill()
            gw.struct_map[gw.cursor.pos[0]][gw.cursor.pos[1]] = new_struct
            gw.struct_map[gw.cursor.pos[0]][gw.cursor.pos[1]].update_edges(
                tuple(gw.cursor.held_structure.directions_to_connect_to), 1)

        gw.time_manager.gold -= gw.struct_map[gw.cursor.pos[0]][gw.cursor.pos[1]].build_cost
        if isinstance(gw.struct_map[gw.cursor.pos[0]][gw.cursor.pos[1]], Wall):
            gw.wall_set.add(tuple(gw.cursor.pos))

    else:
        if build_message == "could_not_afford" and not is_lmb_held_down:
            gw.speech_channel.play(gw.sounds["Resource_Need" + str(randint(17, 19))])
        if build_message.startswith("unsuitable_location") and not is_lmb_held_down and \
                not isinstance(gw.cursor.held_structure, Snapper):
            gw.speech_channel.play(gw.sounds["Placement_Warning16"])

    if isinstance(gw.cursor.held_structure, Snapper):
        was_snapped, snap_message = gw.cursor.held_structure.can_be_snapped(gw, is_lmb_held_down, change, pos_change_dict)
    else:
        was_snapped, snap_message = False, "not_a_snapper"

    if was_snapped and is_lmb_held_down:
        gw.struct_map[gw.cursor.pos[0]][gw.cursor.pos[1]].update_edges(pos_change_dict[change][0], 1)
        gw.struct_map[gw.cursor.previous_pos[0]][gw.cursor.previous_pos[1]].update_edges(pos_change_dict[change][1], 1)

    if was_snapped and not was_built:
        detect_surrounded_tiles(gw)
        for struct in gw.structs:
            if gw.surrounded_tiles[struct.pos[0]][struct.pos[1]] == 2:
                struct.inside = True
            else:
                struct.inside = False

    if was_built or was_snapped:
        gw.sounds["drawbridge_control"].play()

    if (was_snapped and isinstance(gw.cursor.held_structure, Road)) or \
            (was_built and (isinstance(new_struct, House) or isinstance(new_struct, Road))):
        for x in gw.struct_map[max(0, gw.cursor.pos[0] - 7):min(gw.width_tiles, gw.cursor.pos[0] + 8)]:
            for y in x[max(0, gw.cursor.pos[1] - 7):min(gw.width_tiles, gw.cursor.pos[1] + 8)]:
                if isinstance(y, House):
                    y.update_profit(gw)


def remove_structure(gw):
    """
    Function that is responsible for removing structures from the map.
    The structure that will be removed is the one that is on a tile that the gw.cursor's on.

    If the structure that's being removed is a Snapper, all its connected Snapper neighbours
    are updated so that they no longer connect to the tile that the Structure was on.

    The structure is removed from all sprite groups and gw.struct_map is no longer referencing it,
    the value at its coordinates is now set to 0.

    If the remove key is not being held down, a demolition sound effect is played.

        :param gw: Gameworld object
    """
    if isinstance(gw.struct_map[gw.cursor.pos[0]][gw.cursor.pos[1]], Structure):
        gw.fx_channel.play(gw.sounds["buildingwreck_01"])
        if isinstance(gw.struct_map[gw.cursor.pos[0]][gw.cursor.pos[1]], Snapper):
            for direction, direction_rev, x, y in zip(('N', 'E', 'S', 'W'), ('S', 'W', 'N', 'E'),
                                                      (0, -1, 0, 1), (1, 0, -1, 0)):
                if not gw.is_out_of_bounds(gw.cursor.pos[0] + x, gw.cursor.pos[1] + y) and \
                        isinstance(gw.struct_map[gw.cursor.pos[0] + x][gw.cursor.pos[1] + y], Snapper) and \
                        gw.struct_map[gw.cursor.pos[0]][gw.cursor.pos[1]].snapsto[direction_rev] == \
                        gw.struct_map[gw.cursor.pos[0] + x][gw.cursor.pos[1] + y].snapsto[direction]:
                    gw.struct_map[gw.cursor.pos[0] + x][gw.cursor.pos[1] + y].update_edges(direction, -1)

        if isinstance(gw.struct_map[gw.cursor.pos[0]][gw.cursor.pos[1]], Wall):
            gw.wall_set.remove(tuple(gw.cursor.pos))
            detect_surrounded_tiles(gw)
        removed = True

        gw.struct_map[gw.cursor.pos[0]][gw.cursor.pos[1]].kill()
        covered_tiles = gw.struct_map[gw.cursor.pos[0]][gw.cursor.pos[1]].covered_tiles
        for rel in covered_tiles:
            gw.struct_map[gw.cursor.pos[0] + rel[0]][gw.cursor.pos[1] + rel[1]] = 0
        for struct in gw.structs:
            if gw.surrounded_tiles[struct.pos[0]][struct.pos[1]] == 2:
                struct.inside = True
            else:
                struct.inside = False
            if isinstance(struct, House) and \
                    abs(struct.pos[0] - gw.cursor.pos[0]) + abs(struct.pos[0] - gw.cursor.pos[0]) <= 6:
                struct.update_profit(gw)
    else:
        removed = False
    return removed


def change_demolish_mode(gw, button, mode):
    if mode == "toggle":
        gw.cursor.is_in_demolish_mode = not gw.cursor.is_in_demolish_mode
    elif mode == "on":
        gw.cursor.is_in_demolish_mode = True
    elif mode == "off":
        gw.cursor.is_in_demolish_mode = False

    if gw.cursor.is_in_demolish_mode:
        gw.cursor.held_structure = None
        gw.hud.toolbar.demolish_button.is_locked = True
        gw.hud.toolbar.demolish_button.is_held_down = True
    else:
        gw.hud.toolbar.demolish_button.is_locked = False
        gw.hud.toolbar.demolish_button.is_held_down = False


def zoom(gw, button, factor):
    if (gw.tile_s <= 15 and factor < 1) or (gw.tile_s >= 120 and factor > 1):
        return

    gw.tile_s = int(gw.tile_s * factor)
    gw.width_pixels = int(gw.width_pixels * factor)
    gw.height_pixels = int(gw.height_pixels * factor)
    gw.scene.surf = pg.transform.scale(gw.scene.surf, (gw.width_pixels, gw.height_pixels))
    gw.scene.surf_raw = pg.transform.scale(gw.scene.surf_raw, (gw.width_pixels, gw.height_pixels))
    gw.cursor.surf = pg.transform.scale(gw.cursor.surf, (gw.tile_s, gw.tile_s))
    gw.hud.minimap.update_zoom(gw)

    if gw.cursor.held_structure is not None:
        gw.cursor.held_structure.surf = pg.transform.scale(gw.cursor.held_structure.surf, (
            gw.cursor.held_structure.surf_ratio[0] * gw.tile_s, gw.cursor.held_structure.surf_ratio[1] * gw.tile_s))
        gw.cursor.ghost.surf = pg.transform.scale(gw.cursor.held_structure.surf, (
            gw.cursor.held_structure.surf_ratio[0] * gw.tile_s, gw.cursor.held_structure.surf_ratio[1] * gw.tile_s))
        gw.cursor.ghost.rect = gw.cursor.ghost.surf.get_rect(bottomright=(gw.tile_s * (gw.cursor.ghost.pos[0] + 1),
                                                                          gw.tile_s * (gw.cursor.ghost.pos[1] + 1)))
    for struct in gw.structs:
        struct.update_zoom(gw)

    for h, snap in zip((1, 1, 20 / 15, 20 / 15), gw.snapper_dict.values()):
        for name, spr in snap.items():
            snap[name] = pg.transform.scale(spr, (gw.tile_s, gw.tile_s * h))

    if gw.scene.rect.centerx * factor + gw.scene.rect.width / 2 > gw.width_pixels:
        gw.scene.rect.right = gw.width_pixels
    elif gw.scene.rect.centerx * factor - gw.scene.rect.width / 2 < 0:
        gw.scene.rect.left = 0
    else:
        gw.scene.rect.centerx = int(gw.scene.rect.centerx * factor)

    if gw.scene.rect.centery * factor + gw.scene.rect.height / 2 > gw.height_pixels:
        gw.scene.rect.bottom = gw.height_pixels
    elif gw.scene.rect.centery * factor - gw.scene.rect.height / 2 < 0:
        gw.scene.rect.top = 0
    else:
        gw.scene.rect.centery = int(gw.scene.rect.centery * factor)

# def detect_wall_loops(xy):
#     def find_connected_nodes(A, node_xy, direction_to_xy_dict, required, current_walls, origin, i):
#         # print(current_walls, node_xy)
#         current_walls.append(node_xy)
#         if len(gw.struct_map[node_xy[0]][node_xy[1]].neighbours) >= 3:
#             return current_walls, node_xy, True
#
#         if len(gw.struct_map[node_xy[0]][node_xy[1]].neighbours) <= 1 or A[node_xy[0]][node_xy[1]] == False:
#             return 0, 0, False
#         A[node_xy[0]][node_xy[1]] = False
#
#         for direction in gw.struct_map[node_xy[0]][node_xy[1]].neighbours:
#             next = direction_to_xy_dict[direction]
#             if A[node_xy[0] + next[0]][node_xy[1] + next[1]] and \
#                     bool(set(gw.struct_map[node_xy[0] + next[0]][node_xy[1] + next[1]].snapsto.values()) & required) and \
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
#     A = [[True if isinstance(y, Wall) else 0 for y in x] for x in gw.struct_map]
#     B = [[1 if isinstance(y, Wall) and len(y.neighbours) >= 3 else 0 for y in x] for x in gw.struct_map]
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
#     required = set(gw.struct_map[xy[0]][xy[1]].snapsto.values())
#     direction_to_xy_dict = {'N': (0, -1), 'E': (1, 0), 'S': (0, 1), 'W': (-1, 0)}
#
#     i = 0
#     for node in node_list:
#         for direction in gw.struct_map[node[0]][node[1]].neighbours:
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
#         # for _ in range(len(gw.struct_map[node[0]][node[1]].neighbours)):
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
