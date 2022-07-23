from algorithms import *
from graphics import zoom
from pygame.locals import (KEYDOWN,
                           QUIT,
                           K_ESCAPE,
                           K_n,
                           K_x,
                           K_r,
                           K_F3)


class TimeManager:
    def __init__(self, gw):
        self.time = 0
        self.tick = 0
        self.time = [0, 0, 0]
        self.elapsed = 1
        self.start = time.time()
        self.end = 0
        self.tribute = 40
        self.gold = gw.STARTING_GOLD

    def time_lapse(self, gw):
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
                    gw.time_manager.gold -= self.tribute
                    gw.sounds["ignite_oil"].play()
                    self.tribute = int(self.tribute ** 1.2)

    def to_json(self):
        return {
            "time": self.time,
            "tribute": self.tribute
        }

    def from_json(self, json_dict):
        self.time = json_dict["time"]
        self.tribute = json_dict["tribute"]
        return self


def handle_events(gw, event):
    if event.type == QUIT:
        gw.running = False
    if event.type == pg.MOUSEBUTTONDOWN:
        if event.button == 1:
            gw.cursor.is_lmb_pressed = True
        if event.button == 2:
            if isinstance(gw.struct_map[gw.cursor.pos[0]][gw.cursor.pos[1]], Structure):
                gw.hud.build_menu.assign(gw, None, type(gw.struct_map[gw.cursor.pos[0]][gw.cursor.pos[1]]))
                gw.sounds["menusl_" + str(randint(1, 3))].play()
        if event.button == 3:
            gw.cursor.is_lmb_pressed = False
            gw.cursor.is_lmb_held_down = False
            gw.cursor.is_dragging = False

    if event.type == pg.MOUSEBUTTONUP:
        if event.button == 1:
            gw.cursor.is_lmb_pressed = False
            gw.cursor.is_lmb_held_down = False
            if gw.cursor.is_dragging:
                if gw.cursor.is_in_demolish_mode:
                    remove_area(gw)
                elif isinstance(gw.cursor.held_structure, Farmland):
                    make_field(gw)
                else:
                    make_snapper_line(gw)
                gw.cursor.is_dragging = False

    if event.type == KEYDOWN:
        if event.key in gw.key_structure_dict:
            gw.hud.build_menu.assign(gw, None, gw.key_structure_dict[event.key])
            gw.sounds["menusl_" + str(randint(1, 3))].play()

        if event.key == K_n:
            gw.cursor.held_structure = None

        if event.key == K_r and isinstance(gw.cursor.held_structure, Gate):
            gw.cursor.held_structure.rotate(gw)

        if event.key == pg.K_c and isinstance(gw.struct_map[gw.cursor.pos[0]][gw.cursor.pos[1]], House):
            gw.struct_map[gw.cursor.pos[0]][gw.cursor.pos[1]].update_profit(gw)

        if event.key == pg.K_j:
            gw.cursor.change_mode(gw, None, "drag_build", "toggle")

        if event.key == K_F3:
            gw.hud.are_debug_stats_displayed = not gw.hud.are_debug_stats_displayed

        if event.key == pg.K_KP_PLUS:
            zoom(gw, None, 2)

        if event.key == pg.K_KP_MINUS:
            zoom(gw, None, 0.5)

        if event.key == K_x:
            gw.cursor.change_mode(gw, None, "demolish", "toggle")

        if event.key == pg.K_e:
            gw.hud.build_menu.toggle_build_menu(gw)

        if event.key == K_ESCAPE:
            gw.hud.pause_menu.run_pause_menu_loop(gw)

    gw.button_handler.handle_button_press(gw, event)


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

    was_built, build_message = gw.cursor.held_structure.can_be_placed(gw, gw.cursor.pos)
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
            gw.struct_map[gw.cursor.pos[0]][gw.cursor.pos[1]].update_edges(gw, tuple(
                gw.cursor.held_structure.directions_to_connect_to), 1)

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
        was_snapped, snap_message = gw.cursor.held_structure.can_be_snapped(gw, gw.cursor.pos, gw.cursor.previous_pos)
    else:
        was_snapped, snap_message = False, "not_a_snapper"

    if was_snapped and is_lmb_held_down:
        gw.struct_map[gw.cursor.pos[0]][gw.cursor.pos[1]].update_edges(gw, gw.pos_change_dict[gw.cursor.change][0], 1)
        gw.struct_map[gw.cursor.previous_pos[0]][gw.cursor.previous_pos[1]].update_edges(gw, gw.pos_change_dict[
            gw.cursor.change][1], 1)

    if was_snapped and not was_built:
        detect_surrounded_tiles(gw)
        for struct in gw.structs:
            if gw.surrounded_tiles[struct.pos[0]][struct.pos[1]] == 2:
                struct.inside = True
            else:
                struct.inside = False

    if was_built or was_snapped:
        gw.sounds["drawbridge_control"].play()

    if (was_snapped and gw.cursor.held_structure is Road) or \
            (was_built and (isinstance(new_struct, House) or isinstance(new_struct, Road))):
        for x in gw.struct_map[max(0, gw.cursor.pos[0] - 7):min(gw.width_tiles, gw.cursor.pos[0] + 8)]:
            for y in x[max(0, gw.cursor.pos[1] - 7):min(gw.width_tiles, gw.cursor.pos[1] + 8)]:
                if isinstance(y, House):
                    y.update_profit(gw)


def remove_structure(gw, pos):
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
    if not isinstance(gw.struct_map[pos[0]][pos[1]], Structure):
        return False
    if isinstance(gw.struct_map[pos[0]][pos[1]], Snapper):
        for direction, direction_rev, x, y in zip(('N', 'E', 'S', 'W'), ('S', 'W', 'N', 'E'),
                                                  (0, -1, 0, 1), (1, 0, -1, 0)):
            if not gw.is_out_of_bounds(pos[0] + x, pos[1] + y) and \
                    isinstance(gw.struct_map[pos[0] + x][pos[1] + y], Snapper) and \
                    gw.struct_map[pos[0]][pos[1]].snapsto[direction_rev] == \
                    gw.struct_map[pos[0] + x][pos[1] + y].snapsto[direction]:
                gw.struct_map[pos[0] + x][pos[1] + y].update_edges(gw, direction, -1)

    if isinstance(gw.struct_map[pos[0]][pos[1]], Wall):
        gw.wall_set.remove(tuple(pos))
    removed = True

    gw.struct_map[pos[0]][pos[1]].kill()
    covered_tiles = gw.struct_map[pos[0]][pos[1]].covered_tiles
    for rel in covered_tiles:
        gw.struct_map[pos[0] + rel[0]][pos[1] + rel[1]] = 0
    for struct in gw.structs:
        if gw.surrounded_tiles[struct.pos[0]][struct.pos[1]] == 2:
            struct.inside = True
        else:
            struct.inside = False
        if isinstance(struct, House) and \
                abs(struct.pos[0] - pos[0]) + abs(struct.pos[0] - pos[0]) <= 6:
            struct.update_profit(gw)
    return removed


def remove_area(gw):
    already_made_sound = False
    for x in range(gw.cursor.ghost.rect.left, gw.cursor.ghost.rect.right, gw.tile_s):
        for y in range(gw.cursor.ghost.rect.top, gw.cursor.ghost.rect.bottom, gw.tile_s):
            if remove_structure(gw, [x // gw.tile_s, y // gw.tile_s]) and not already_made_sound:
                gw.fx_channel.play(gw.sounds["buildingwreck_01"])
                already_made_sound = True
    detect_surrounded_tiles(gw)
