from game_managment import *
from hud import *
from gameworld import GameWorld
from placeholder import *

def main():
    pg.init()
    pg.mixer.init()
    gw = GameWorld()
    clock = pg.time.Clock()

    gw.speech_channel.play(gw.sounds["General_Startgame"])
    gw.running = True
    # ------ MAIN LOOP -------
    while gw.running:

        pressed_keys = pg.key.get_pressed()

        if gw.button_handler.hovered_button is None:
            gw.cursor.update(gw)

        for event in pg.event.get():
            handle_events(gw, event)

        if gw.cursor.is_lmb_pressed and gw.button_handler.hovered_button is None:
            if not gw.cursor.is_in_demolish_mode:
                if gw.cursor.held_structure is not None:
                    if gw.cursor.is_in_drag_build_mode and type(gw.cursor.held_structure) in {Farmland, Road, Wall}:
                        if not gw.cursor.is_lmb_held_down:
                            gw.cursor.is_dragging = True
                            gw.cursor.ghost.drag_starting_pos = gw.cursor.pos.copy()
                    else:
                        place_structure(gw, gw.cursor.is_lmb_held_down)
                else:
                    gw.scene.move_velocity = (-gw.cursor.mouse_change[0], -gw.cursor.mouse_change[1])
            else:
                if not gw.cursor.is_lmb_held_down:
                    gw.cursor.is_dragging = True
                    gw.cursor.ghost.drag_starting_pos = gw.cursor.pos.copy()
            gw.cursor.is_lmb_held_down = True

        if not gw.cursor.is_lmb_pressed or gw.cursor.held_structure is not None or gw.cursor.is_in_demolish_mode:
            gw.scene.move_screen_border(gw)

        if not gw.cursor.is_lmb_pressed and gw.scene.to_decrement > 0:
            gw.scene.move_velocity = (gw.scene.move_velocity[0] - gw.scene.move_velocity_decrement[0],
                                      gw.scene.move_velocity[1] - gw.scene.move_velocity_decrement[1])
            gw.scene.to_decrement -= 1

        for struct in gw.structs:
            struct.get_profit(gw)

        if gw.time_manager.gold < -50:
            gw.running = False

        gw.entities.draw(gw.scene)
        if gw.button_handler.hovered_button is None:
            gw.cursor.draw(gw)

        if gw.SOUNDTRACK and not gw.soundtrack_channel.get_busy():
            gw.soundtrack_channel.play(gw.tracks[randint(0, 13)])

        if randint(1, 200000) == 1:
            gw.sounds["Random_Events13"].play()

        gw.scene.move_screen_drag(gw)
        gw.screen.blit(gw.scene.surf_rendered, (0, 0))

        if gw.hud.are_debug_stats_displayed:
            gw.hud.global_statistics.update_global_stats(gw)
            gw.hud.tile_statistics.update_tile_stats(gw.cursor.pos, gw)
        if gw.hud.build_menu.is_build_menu_open:
            gw.screen.blit(gw.hud.build_menu.surf, gw.hud.build_menu.rect)

        gw.screen.blit(gw.hud.toolbar.surf, gw.hud.toolbar.rect)
        gw.hud.minimap.update_minimap(gw)
        gw.hud.top_bar.update(gw)

        gw.button_handler.handle_hovered_buttons(gw, gw.buttons)

        gw.time_manager.time_lapse(gw)
        gw.scene.surf_rendered.blit(gw.scene.surf_raw.subsurface(gw.scene.rect), (0, 0))
        pg.display.flip()

        clock.tick(gw.TICK_RATE)
    time.sleep(0.1)
    pg.quit()


def testing():
    pg.init()

    screen = pg.display.set_mode([500, 500])

    sizes = Sizes(Config())
    spritesheet = Spritesheet(sizes)
    struct_manager = StructManager(sizes)
    res_man = ResourceManager()
    house1 = House(Vector(1, 1), sizes.tile, spritesheet, res_man)
    wall1 = Wall(Vector(1, 4), sizes.tile, spritesheet, res_man)
    mine1 = Mine(Vector(0, 1), sizes.tile, spritesheet, res_man)
    wall1.add_neighbour(Direction.E)
    wall1.add_neighbour(Direction.N)
    wall1.add_neighbour(Direction.W)
    wall1.add_neighbour(Direction.S)
    print(house1.cost, house1.profit)

    running = True
    while running:

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

        screen.blit(house1.surf, house1.rect)
        screen.blit(wall1.surf, wall1.rect)
        screen.blit(mine1.surf, mine1.rect)

        pg.display.flip()

    pg.quit()


if __name__ == "__main__":
    # main()

    pg.init()
    pg.mixer.init()
    # gw = GameWorld()
    map1 = Map([[1, 4, 3, 6],
                [3, 5, 7, 4],
                [3, 2, 5, 3],
                [1, 1, 1, 0]])
    pos1 = Vector(3, 2)
    pos2 = Vector(0, 1)
    # print(map1)
    # print(map1[0, 1])
    # print(-Direction.E)
    pos2 += pos1
    # struct = Structure(pos1, None)
    # print(struct)
    # pos1 = Vector(4, 4)
    # print(struct)
    print(sorted((Direction.N, Direction.S, Direction.E, Direction.W)))
    print(pos1 - pos2)
    print(TileTypes.GRASSLAND)
    dir_set = DirectionSet((Direction.N, Direction.S))
    testing()
