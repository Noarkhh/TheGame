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
    gw.surrounded_tiles[:] = [[0 for _ in range(gw.height_tiles)] for _ in range(gw.width_tiles)]
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


def make_field(gw):
    topleft_corner = [x // gw.tile_s for x in gw.cursor.ghost.rect.topleft]
    bottomright_corner = [x // gw.tile_s - 1 for x in gw.cursor.ghost.rect.bottomright]
    visited = [[False for _ in range(0, gw.cursor.ghost.rect.height, gw.tile_s)]
               for _ in range(0, gw.cursor.ghost.rect.width, gw.tile_s)]

    def should_be_included(pos):
        if gw.tile_type_map[pos[0]][pos[1]] in {"water", "desert"}:
            return False
        if pos[0] < topleft_corner[0] or pos[0] > bottomright_corner[0]:
            return False
        if pos[1] < topleft_corner[1] or pos[1] > bottomright_corner[1]:
            return False
        return True

    def _make_field(pos):
        visited[pos[0] - topleft_corner[0]][pos[1] - topleft_corner[1]] = True
        new_struct = None
        if gw.struct_map[pos[0]][pos[1]] == 0:
            new_struct = Farmland(pos, gw)
            gw.structs.add(new_struct)
            gw.entities.add(new_struct)
            gw.struct_map[pos[0]][pos[1]] = new_struct

        for direction in ([0, -1], [1, 0], [0, 1], [-1, 0]):
            if not gw.is_out_of_bounds(pos[0] + direction[0], pos[1] + direction[1]) and \
                    should_be_included((pos[0] + direction[0], pos[1] + direction[1])):
                if not visited[pos[0] + direction[0] - topleft_corner[0]][pos[1] + direction[1] - topleft_corner[1]] \
                        and (isinstance(gw.struct_map[pos[0] + direction[0]][pos[1] + direction[1]], Farmland) or
                             gw.struct_map[pos[0] + direction[0]][pos[1] + direction[1]] == 0):
                    _make_field([pos[0] + direction[0], pos[1] + direction[1]])

                if isinstance(gw.struct_map[pos[0] + direction[0]][pos[1] + direction[1]], Farmland):
                    gw.struct_map[pos[0] + direction[0]][pos[1] + direction[1]]. \
                        update_edges(gw, gw.xy_to_direction_dict[tuple([-x for x in direction])], 1)
                    if new_struct is not None:
                        new_struct.update_edges(gw, gw.xy_to_direction_dict[tuple(direction)], 1)

    can_be_placed, message = gw.cursor.held_structure.can_be_placed(gw, gw.cursor.ghost.drag_starting_pos)
    if can_be_placed or isinstance(gw.struct_map[gw.cursor.ghost.drag_starting_pos[0]][
                                       gw.cursor.ghost.drag_starting_pos[1]], Farmland):
        _make_field(gw.cursor.ghost.drag_starting_pos)
        gw.sounds["drawbridge_control"].play()
    elif not can_be_placed:
        if message.startswith("unsuitable_location"):
            gw.speech_channel.play(gw.sounds["Placement_Warning16"])
        elif message == "couldn't_afford":
            gw.speech_channel.play(gw.sounds["Resource_Need" + str(randint(17, 19))])


def make_snapper_line(gw):
    def place_structure(pos):
        new_struct = type(gw.cursor.held_structure)(pos, gw)
        if isinstance(new_struct, Road) and gw.tile_type_map[pos[0]][pos[1]] == "water":
            new_struct = Bridge(pos, gw)
        gw.structs.add(new_struct)
        gw.entities.add(new_struct)
        gw.struct_map[pos[0]][pos[1]] = new_struct
        gw.time_manager.gold -= new_struct.build_cost
        if isinstance(new_struct, Wall):
            gw.wall_set.add(tuple(pos))

    def build_segment(seg_number, orientation, length):
        if orientation == "vert":
            if seg_number == 0:
                step = (0, step_dict[gw.cursor.ghost.sides_to_draw[0]])
            else:
                step = (0, -step_dict[gw.cursor.ghost.sides_to_draw[1]])
        else:
            if seg_number == 0:
                step = (step_dict[gw.cursor.ghost.sides_to_draw[0]], 0)
            else:
                step = (-step_dict[gw.cursor.ghost.sides_to_draw[1]], 0)

        for i in range(length):
            can_be_placed, build_message = gw.cursor.held_structure.can_be_placed(gw, curr_pos)
            if can_be_placed:
                place_structure(curr_pos)
                sound_info_dict["was_built"] = True
            can_be_snapped, snap_message = gw.cursor.held_structure.can_be_snapped(gw, curr_pos, [curr_pos[0] - step[0], curr_pos[1] - step[1]])
            if can_be_snapped:
                sound_info_dict["was_built"] = True
            if not can_be_placed:
                if build_message != "unsuitable_location_structure":
                    if build_message == "couldn't_afford":
                        sound_info_dict["couldn't_afford"] = True
                    if build_message == "unsuitable_location_tile":
                        sound_info_dict["unsuitable_location"] = True
                    return False
                else:
                    if not can_be_snapped and snap_message != "already_snapped" and (i > 0 or seg_number > 0):
                        sound_info_dict["unsuitable_location"] = True
                        return False
            if not can_be_snapped and i > 0 and snap_message != "already_snapped":
                gw.struct_map[curr_pos[0]][curr_pos[1]].kill()
                gw.time_manager.gold += gw.struct_map[curr_pos[0]][curr_pos[1]].build_cost
                gw.wall_set.remove(tuple(curr_pos))
                gw.struct_map[curr_pos[0]][curr_pos[1]] = 0
                sound_info_dict["was_built"] = False
                sound_info_dict["unsuitable_location"] = True
                return False
            if i > 0 or seg_number == 1:
                gw.struct_map[curr_pos[0]][curr_pos[1]].update_edges(gw, gw.pos_change_dict[(step[0], step[1])][0], 1)
                gw.struct_map[curr_pos[0] - step[0]][curr_pos[1] - step[1]].update_edges(gw, gw.pos_change_dict[(step[0], step[1])][1], 1)
            curr_pos[1] += step[1]
            curr_pos[0] += step[0]

        return True

    width = gw.cursor.ghost.rect.width // gw.tile_s
    height = gw.cursor.ghost.rect.height // gw.tile_s
    step_dict = {"top": -1, "right": 1, "bottom": 1, "left": -1}
    curr_pos = gw.cursor.ghost.drag_starting_pos.copy()

    sound_info_dict = {"was_built": False, "couldn't_afford": False, "unsuitable_location": False}

    if len(gw.cursor.ghost.sides_to_draw) == 2:
        if gw.cursor.ghost.sides_to_draw[0] in {"left", "right"}:
            if build_segment(0, "horiz", width):
                curr_pos[0] -= step_dict[gw.cursor.ghost.sides_to_draw[0]]
                curr_pos[1] += -step_dict[gw.cursor.ghost.sides_to_draw[1]]
                build_segment(1, "vert", height - 1)

        elif gw.cursor.ghost.sides_to_draw[0] in {"top", "bottom"}:
            if build_segment(0, "vert", height):
                curr_pos[1] -= step_dict[gw.cursor.ghost.sides_to_draw[0]]
                curr_pos[0] += -step_dict[gw.cursor.ghost.sides_to_draw[1]]
                build_segment(1, "horiz", width - 1)

    elif len(gw.cursor.ghost.sides_to_draw) == 1:
        if gw.cursor.ghost.sides_to_draw[0] in {"left", "right"}:
            build_segment(0, "horiz", width)
        elif gw.cursor.ghost.sides_to_draw[0] in {"top", "bottom"}:
            build_segment(0, "vert", height)

    elif len(gw.cursor.ghost.sides_to_draw) == 0:
        can_be_placed, message = gw.cursor.held_structure.can_be_placed(gw, curr_pos)
        if can_be_placed:
            place_structure(curr_pos)
            sound_info_dict["was_built"] = True
        else:
            if message.startswith("unsuitable_location"):
                sound_info_dict["unsuitable_location"] = True
            elif message == "couldn't_afford":
                sound_info_dict["couldn't_afford"] = True

    if sound_info_dict["was_built"]:
        gw.sounds["drawbridge_control"].play()
    if sound_info_dict["couldn't_afford"]:
        gw.speech_channel.play(gw.sounds["Resource_Need" + str(randint(17, 19))])
    if sound_info_dict["unsuitable_location"]:
        gw.speech_channel.play(gw.sounds["Placement_Warning16"])


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
