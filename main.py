import pygame as pg
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
                           K_h)

HEIGHT_TILES = 12
WIDTH_TILES = 18
TILE_SIZE = 60


class Cursor(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.windup = [0 for _ in range(4)]
        self.cooldown = [0 for _ in range(4)]
        self.surf = pg.image.load("assets/cursor2.png").convert()
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
        self.position = [xy[0], xy[1]]
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
        self.position = [xy[0], xy[1]]
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


def render_background():
    background = pg.image.load("assets/background.png").convert()
    screen.blit(background, (0, 0))


if __name__ == "__main__":
    pg.init()
    pg.mixer.init()
    boom_se = pg.mixer.Sound("assets/boom sound effect.ogg")
    bruh_se = pg.mixer.Sound("assets/bruh sound effect.ogg")
    violin_se = pg.mixer.Sound("assets/violin screech sound effect.ogg")

    screen = pg.display.set_mode([1080, 720])
    cursor = Cursor()
    game_board = [[0 for _ in range(HEIGHT_TILES)] for _ in range(WIDTH_TILES)]
    print(game_board)
    houses = pg.sprite.Group()
    towers = pg.sprite.Group()
    structures = pg.sprite.Group()
    all_sprites = pg.sprite.Group()
    all_sprites.add(cursor)

    clock = pg.time.Clock()
    key_structure_dict = {K_h: House, K_t: Tower}
    structure_group_dict = {House: houses, Tower: towers}

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

                if event.key == K_SPACE:  # placing down held structure
                    if isinstance(cursor.holding, Structure):
                        if game_board[cursor.position[0]][cursor.position[1]] not in structures:
                            new_structure = type(cursor.holding)(cursor.position)
                            structure_group_dict[type(cursor.holding)].add(new_structure)
                            structures.add(new_structure)
                            all_sprites.add(new_structure)
                            game_board[new_structure.position[0]][new_structure.position[1]] = new_structure
                            boom_se.play()
                            cursor.holding = None
                        else: bruh_se.play()
                if event.key == K_ESCAPE:
                    running = False

        pressed_keys = pg.key.get_pressed()
        cursor.update(pressed_keys)
        render_background()
        for entity in structures:
            screen.blit(entity.surf, entity.rect)
        if cursor.holding is not None:
            structure_ghost.update(cursor.position)
            screen.blit(structure_ghost.surf, structure_ghost.rect)
        screen.blit(cursor.surf, cursor.rect)

        pg.display.flip()
        clock.tick(20)
    pg.quit()
