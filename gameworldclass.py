import os
from classes import *
from pygame.locals import (RLEACCEL,
                           K_t,
                           K_h,
                           K_r,
                           K_w,
                           K_g)


class GameWorld:
    def __init__(self):
        self.SOUNDTRACK = False
        self.MOUSE_STEERING = True
        self.LAYOUT = pg.image.load("assets/maps/desert_delta_L.png")
        self.HEIGHT_TILES = self.LAYOUT.get_height()
        self.WIDTH_TILES = self.LAYOUT.get_width()
        self.WINDOW_HEIGHT = 720
        self.WINDOW_WIDTH = 1080
        self.WINDOWED = True
        self.TICK_RATE = 60
        self.TICK = 0

        self.tile_s = 30
        self.width_pixels = self.WIDTH_TILES * self.tile_s
        self.height_pixels = self.HEIGHT_TILES * self.tile_s
        self.wall_set = set()
        self.key_structure_dict = {K_h: House, K_t: Tower, K_r: Road, K_w: Wall, K_g: Gate, pg.K_p: Pyramid}
        self.entities = Entities()
        self.structs = pg.sprite.Group()
        self.vault = Vault()
        self.soundtrack_channel = pg.mixer.Channel(5)
        self.speech_channel = pg.mixer.Channel(3)

        self.screen = self.set_window()
        self.snapper_dict = self.fill_snappers_dict()
        self.map_surf, self.tile_type_map = self.load_map()
        self.surrounded_tiles = [[0 for _ in range(self.HEIGHT_TILES)] for _ in range(self.WIDTH_TILES)]
        self.struct_map = [[0 for _ in range(self.HEIGHT_TILES)] for _ in range(self.WIDTH_TILES)]
        self.sounds, self.tracks = self.load_sounds()

    def set_window(self):
        if self.WINDOWED:
            screen = pg.display.set_mode([self.WINDOW_WIDTH, self.WINDOW_HEIGHT])
        else:
            screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
            self.WINDOW_WIDTH, self.WINDOW_HEIGHT = pg.display.get_surface().get_size()
        pg.display.set_caption("Twierdza: Zawodzie")
        pg.display.set_icon(pg.image.load("assets/icon.png").convert())
        return screen

    def fill_snappers_dict(self):
        snapper_dict = {}
        for curr_dict_name, snapper_dir, height in (("walls", "assets/walls", self.tile_s),
                                                    ("roads", "assets/roads", self.tile_s),
                                                    ("vgates", "assets/vgates", self.tile_s * 20 / 15),
                                                    ("hgates", "assets/hgates", self.tile_s * 20 / 15)):
            directory = os.listdir(snapper_dir)
            dir_cut = []
            curr_dict = {}
            for name in directory:
                dir_cut.append(tuple(name[4:-4]))
            for file, name in zip(directory, dir_cut):
                curr_dict[name] = pg.transform.scale(pg.image.load(snapper_dir + "/" + file).convert(),
                                                     (self.tile_s, height))
                curr_dict[name].set_colorkey((255, 255, 255), RLEACCEL)
            snapper_dict[curr_dict_name] = curr_dict
        return snapper_dict

    def load_map(self):
        color_to_type = {(0, 255, 0, 255): "grassland", (0, 0, 255, 255): "sea", (255, 255, 0, 255): "desert"}
        tile_dict = {name: pg.transform.scale(pg.image.load("assets/tiles/" + name + "_tile.png").convert(),
                                              (self.tile_s, self.tile_s)) for name in color_to_type.values()}

        background = pg.Surface((self.WIDTH_TILES * self.tile_s, self.HEIGHT_TILES * self.tile_s))
        tile_map = [[0 for _ in range(self.HEIGHT_TILES)] for _ in range(self.WIDTH_TILES)]

        for x in range(self.WIDTH_TILES):
            for y in range(self.HEIGHT_TILES):
                tile_color = tuple(self.LAYOUT.get_at((x, y)))
                background.blit(tile_dict[color_to_type[tile_color]], (x * self.tile_s, y * self.tile_s))
                tile_map[x][y] = color_to_type[tile_color]
                # if tile_map[x][y] == "grassland" and randint(1, 16) == 1:
                #     self.struct_map[x][y] = Tree([x, y])
                #     gw.structs.add(self.struct_map[x][y])
                #     gw.entities.add(self.struct_map[x][y])
                # elif tile_map[x][y] == "desert" and randint(1, 25) == 1:
                #     gw.struct_map[x][y] = Cactus([x, y])
                #     gw.structs.add(gw.struct_map[x][y])
                #     gw.entities.add(gw.struct_map[x][y])

        return background, tile_map

    def load_sounds(self):
        fx_dir = os.listdir("assets/fx")
        soundtrack_dir = os.listdir("assets/soundtrack")
        sounds = {file[:-4]: pg.mixer.Sound("assets/fx/" + file) for file in fx_dir}
        if self.SOUNDTRACK:
            tracks = [pg.mixer.Sound("assets/soundtrack/" + file) for file in soundtrack_dir]
        else:
            tracks = []
        for track in tracks:
            track.set_volume(0.4)
        for sound in sounds.values():
            sound.set_volume(0.7)

        return sounds, tracks
