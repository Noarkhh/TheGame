from functions import *
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

    cursor = Cursor(gw)
    tile_statistics = TileStatistics(gw)
    global_statistics = GlobalStatistics()
    build_menu = BuildMenu(gw)
    minimap = Minimap(gw)

    prev_pos = (0, 0)

    clock = pg.time.Clock()
    press_hold, remove_hold = False, False
    display_stats, display_build_menu = True, True
    structure_ghost = None
    on_button = False
    curr_button, prev_button = None, None

    gw.speech_channel.play(gw.sounds["General_Startgame"])
    running = True
    # ------ MAIN LOOP -------
    while running:

        pressed_keys = pg.key.get_pressed()
        # checking events
        if gw.MOUSE_STEERING:
            on_button = False
            for button in gw.buttons:
                if button.rect.collidepoint(pg.mouse.get_pos()):
                    curr_button = button
                    on_button = True

            if not on_button:
                cursor.update(gw)
                curr_button = None
        else:
            cursor.update_arrows(gw, pressed_keys)

        for event in pg.event.get():
            if event.type == QUIT:
                running = False
            if event.type == KEYDOWN:

                if event.key in gw.key_structure_dict:  # picking up a chosen structure
                    cursor.hold = gw.key_structure_dict[event.key]([0, 0], gw)
                    cursor.ghost = Ghost(gw, cursor)
                    gw.sounds["menusl_" + str(randint(1, 3))].play()

                if event.key == K_n:
                    cursor.hold = None

                if event.key == K_ESCAPE:
                    running = False

                if event.key == K_q and isinstance(cursor.hold, Gate):
                    cursor.hold.rotate(gw)

                if event.key == pg.K_c and isinstance((gw.struct_map[cursor.pos[0]][cursor.pos[1]]), House):
                    gw.struct_map[cursor.pos[0]][cursor.pos[1]].update_profit(gw)

                if event.key == pg.K_j and isinstance((gw.struct_map[cursor.pos[0]][cursor.pos[1]]), Wall):
                    for x in gw.surrounded_tiles:
                        print(x)

                if event.key == K_F3:
                    display_stats = not display_stats

                if event.key == pg.K_KP_PLUS and gw.tile_s < 120:
                    zoom(gw, 2, cursor, minimap)

                if event.key == pg.K_KP_MINUS and gw.tile_s > 15:
                    zoom(gw, 0.5, cursor, minimap)

                if event.key == pg.K_e:
                    if display_build_menu:
                        gw.buttons.remove(build_menu.buttons)
                    else:
                        build_menu = BuildMenu(gw)
                    display_build_menu = not display_build_menu

        if pressed_keys[K_SPACE] or pg.mouse.get_pressed(num_buttons=3)[0]:  # placing down held structure
            if not on_button:
                place_structure(gw, cursor, prev_pos, press_hold)
            else:
                curr_button.press(gw, cursor, press_hold)
            press_hold = True
        else:
            press_hold = False

        if pressed_keys[K_x]:  # removing a structure
            if remove_structure(gw, cursor, remove_hold):
                remove_hold = True
        else:
            remove_hold = False
        prev_pos = tuple(cursor.pos)
        gw.background.move_screen(gw, cursor)

        for struct in gw.structs:
            struct.get_profit(gw)

        if gw.vault.gold < -50:
            running = False

        gw.entities.draw(gw.background)
        if curr_button is None:
            cursor.draw(gw)


        # if cursor.hold is not None:
        #     cursor.ghost.update(gw, cursor)
        #     gw.background.surf.blit(cursor.ghost.surf, cursor.ghost.rect)

        # gw.background.surf.blit(cursor.surf, cursor.rect)

        if gw.SOUNDTRACK and not gw.soundtrack_channel.get_busy():
            gw.soundtrack_channel.play(gw.tracks[randint(0, 13)])
        if randint(1, 200000) == 1: gw.sounds["Random_Events13"].play()

        gw.screen.blit(gw.background.surf_rendered, (0, 0))

        if display_stats:
            global_statistics.update_global_stats(gw)
            tile_statistics.update_tile_stats(cursor.pos, gw)
        if display_build_menu:
            gw.screen.blit(build_menu.surf, build_menu.rect)
        minimap.update_minimap(gw)
        if curr_button is not None:
            if not press_hold:
                if prev_button is not curr_button:
                    gw.sounds["woodrollover" + str(randint(2, 5))].play()
                curr_button.hovered(gw)
            else:
                curr_button.pressed(gw)
        prev_button = curr_button

        gw.background.surf_rendered.blit(gw.background.surf_raw.subsurface(gw.background.rect), (0, 0))
        pg.display.flip()

        clock.tick(gw.TICK_RATE)
    pg.quit()
