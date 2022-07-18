from functions import *
from hud import *
from gameworld import GameWorld
from pygame.locals import (KEYDOWN,
                           QUIT,
                           K_ESCAPE,
                           K_n,
                           K_x,
                           K_r,
                           K_F3)

if __name__ == "__main__":

    pg.init()
    pg.mixer.init()
    gw = GameWorld()
    clock = pg.time.Clock()

    is_lmb_held_down = False

    gw.speech_channel.play(gw.sounds["General_Startgame"])
    gw.running = True
    # ------ MAIN LOOP -------
    while gw.running:

        pressed_keys = pg.key.get_pressed()

        if gw.button_handler.hovered_button is None:
            gw.cursor.update(gw)

        for event in pg.event.get():
            if event.type == QUIT:
                gw.running = False
            if event.type == KEYDOWN:

                if event.key in gw.key_structure_dict:  # picking up a chosen structure
                    gw.cursor.held_structure = gw.key_structure_dict[event.key]([0, 0], gw)
                    gw.cursor.ghost = Ghost(gw)
                    gw.sounds["menusl_" + str(randint(1, 3))].play()
                    gw.cursor.change_mode(gw, None, "demolish", "off")

                if event.key == K_n:
                    gw.cursor.held_structure = None

                if event.key == K_r and isinstance(gw.cursor.held_structure, Gate):
                    gw.cursor.held_structure.rotate(gw)

                if event.key == pg.K_c and isinstance((gw.struct_map[gw.cursor.pos[0]][gw.cursor.pos[1]]), House):
                    gw.struct_map[gw.cursor.pos[0]][gw.cursor.pos[1]].update_profit(gw)

                if event.key == pg.K_j:
                    # make_field(gw, [85, 55], [95, 65])
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

            button_press_result = gw.button_handler.handle_button_press(gw, event)

        if pg.mouse.get_pressed(num_buttons=3)[0] and gw.button_handler.hovered_button is None:
            if not gw.cursor.is_in_demolish_mode and gw.cursor.held_structure is not None:
                if not (gw.cursor.is_in_drag_build_mode and isinstance(gw.cursor.held_structure, Snapper)):
                    place_structure(gw, is_lmb_held_down)
                else:
                    gw.cursor.is_dragging = True
                    if not is_lmb_held_down:
                        gw.cursor.ghost.drag_starting_pos = gw.cursor.pos.copy()

            elif gw.cursor.is_in_demolish_mode:
                remove_structure(gw)
            is_lmb_held_down = True
        else:
            is_lmb_held_down = False
            if gw.cursor.is_dragging:
                make_field(gw, gw.cursor.ghost.drag_starting_pos, gw.cursor.pos)
                gw.cursor.is_dragging = False

        gw.scene.move_screen(gw)

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
