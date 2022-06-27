from functions import *
from hud import *
from gameworld import GameWorld
from pygame.locals import (K_SPACE,
                           KEYDOWN,
                           QUIT,
                           K_ESCAPE,
                           K_n,
                           K_x,
                           K_q,
                           K_F3)

if __name__ == "__main__":

    pg.init()
    pg.mixer.init()
    gw = GameWorld()
    clock = pg.time.Clock()

    is_lmb_held_down, remove_hold = False, False

    gw.speech_channel.play(gw.sounds["General_Startgame"])
    running = True
    # ------ MAIN LOOP -------
    while running:

        pressed_keys = pg.key.get_pressed()

        if gw.button_handler.hovered_button is None:
            gw.cursor.update(gw)

        for event in pg.event.get():
            if event.type == QUIT:
                running = False
            if event.type == KEYDOWN:

                if event.key in gw.key_structure_dict:  # picking up a chosen structure
                    gw.cursor.held_structure = gw.key_structure_dict[event.key]([0, 0], gw)
                    gw.cursor.ghost = Ghost(gw)
                    gw.sounds["menusl_" + str(randint(1, 3))].play()

                if event.key == K_n:
                    gw.cursor.held_structure = None

                if event.key == K_q and isinstance(gw.cursor.held_structure, Gate):
                    gw.cursor.held_structure.rotate(gw)

                if event.key == pg.K_c and isinstance((gw.struct_map[gw.cursor.pos[0]][gw.cursor.pos[1]]), House):
                    gw.struct_map[gw.cursor.pos[0]][gw.cursor.pos[1]].update_profit(gw)

                if event.key == pg.K_j and isinstance((gw.struct_map[gw.cursor.pos[0]][gw.cursor.pos[1]]), Wall):
                    for x in gw.surrounded_tiles:
                        print(x)

                if event.key == K_F3:
                    gw.hud.are_debug_stats_displayed = not gw.hud.are_debug_stats_displayed

                if event.key == pg.K_KP_PLUS and gw.tile_s < 120:
                    zoom(gw, 2)

                if event.key == pg.K_KP_MINUS and gw.tile_s > 15:
                    zoom(gw, 0.5)

                if event.key == pg.K_e:
                    if gw.hud.is_build_menu_open:
                        gw.buttons.difference_update(gw.hud.build_menu.buttons)
                    else:
                        gw.hud.build_menu.load_menu(gw)
                    gw.hud.is_build_menu_open = not gw.hud.is_build_menu_open

                if event.key == K_ESCAPE:
                    running = run_pause_menu_loop(gw)
            if gw.button_handler.hovered_button is not None:
                button_press_result = gw.button_handler.handle_button_press(gw, event)

        if pg.mouse.get_pressed(num_buttons=3)[0] and gw.button_handler.hovered_button is None and \
                gw.cursor.held_structure is not None:
            place_structure(gw, is_lmb_held_down)
            is_lmb_held_down = True
        else:
            is_lmb_held_down = False

        if pressed_keys[K_x]:  # removing a structure
            if remove_structure(gw, remove_hold):
                remove_hold = True
        else:
            remove_hold = False
        gw.cursor.previous_pos = tuple(gw.cursor.pos)
        gw.background.move_screen(gw)

        for struct in gw.structs:
            struct.get_profit(gw)

        if gw.time_manager.gold < -50:
            running = False

        gw.entities.draw(gw.background)
        if gw.button_handler.hovered_button is None:
            gw.cursor.draw(gw)

        if gw.SOUNDTRACK and not gw.soundtrack_channel.get_busy():
            gw.soundtrack_channel.play(gw.tracks[randint(0, 13)])

        if randint(1, 200000) == 1:
            gw.sounds["Random_Events13"].play()

        gw.screen.blit(gw.background.surf_rendered, (0, 0))

        if gw.hud.are_debug_stats_displayed:
            gw.hud.global_statistics.update_global_stats(gw)
            gw.hud.tile_statistics.update_tile_stats(gw.cursor.pos, gw)
        if gw.hud.is_build_menu_open:
            gw.screen.blit(gw.hud.build_menu.surf, gw.hud.build_menu.rect)

        gw.hud.minimap.update_minimap(gw)
        gw.hud.top_bar.update(gw)

        gw.button_handler.handle_hovered_buttons(gw, gw.buttons)

        gw.time_manager.time_lapse(gw)
        gw.background.surf_rendered.blit(gw.background.surf_raw.subsurface(gw.background.rect), (0, 0))
        pg.display.flip()

        clock.tick(gw.TICK_RATE)
    time.sleep(0.1)
    pg.quit()
