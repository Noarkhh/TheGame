import os
from classes import *
from hud import *
from pygame.locals import (RLEACCEL,
                           K_t,
                           K_h,
                           K_r,
                           K_w,
                           K_g)


class GameWorld:
    """
    Class of a main object called gw (gameworld) used for storing data of the current state of the game
    as well as generating necessary data structures and setting up the game.

    Object gw is passed to all almost all functions, objects and methods as it contains most of
    the information about current state of the game.

    Attributes:

        SOUNDTRACK: Option to turn soundtrack on or off
        MOUSE_STEERING: Option to turn mouse steering on or off
        MOUSE_STEERING: Option to turn windowed mode on or off
        WINDOW_HEIGHT, WINDOWS_WIDTH: Window size in pixels
        TICK_RATE: Amount of game ticks per second
        STARTING_GOLD: starting gold

        screen: Main surface that is displayed
        snapper_dict: Dictionary of dictionaries for different Snappers
        sounds, tracks: Dictionaries that assign sounds and tracks to their corresponding names
        key_structure_dict: Dictionary that assigns classes of different structures to keys, that will
                            place instances of these classes
        string_type_dict: Dictionary that assigns classes of different structures to strings that represent them
        soundtrack_channel: Mixer channel used for soundtrack
        speech_channel: Mixer channel used for speech

        layout, layout_path: Image representing the terrain
        height_tiles, width_tiles: Map size in tiles
        tile_s: Size of a single tile in pixels
        width_pixels, height_pixels: Map size in pixels

        map_surf: Surface of the map terrain
        tile_type_map: 2-dimensional array of tile types
        surrounded_tiles: 2-dimensional array that indicates which tiles are inside walls
        struct_map: 2-dimensional array of all structures, main way to reference structures
        cursor: Object that handles the cursor
        wall_set: Set of tuples of coordinates of all walls

        entities: Sprite group of all sprites with expanded rendering functionality
        structs: Sprite group of all structures
        buttons: Set of all buttons
        time_manager: Object that tracks all global variables
        background: Object that holds and handles the part of map currently being displayed

        hud: Object that handles HUD
    """

    def __init__(self):
        self.SOUNDTRACK = False
        self.MOUSE_STEERING = True
        self.WINDOWED = True
        self.WINDOW_HEIGHT = 720
        self.WINDOW_WIDTH = 1080
        self.TICK_RATE = 60
        self.STARTING_GOLD = 300000000

        self.screen = self.set_window()

        self.layout_path = "assets/maps/desert_delta_L.png"
        self.layout = pg.image.load(self.layout_path).convert()
        self.height_tiles = self.layout.get_height()
        self.width_tiles = self.layout.get_width()
        self.tile_s = 30
        self.width_pixels = self.width_tiles * self.tile_s
        self.height_pixels = self.height_tiles * self.tile_s

        self.snapper_dict = self.fill_snappers_dict()
        self.sounds, self.tracks = self.load_sounds()
        self.key_structure_dict = {K_h: House, K_t: Tower, K_r: Road, K_w: Wall, K_g: Gate, pg.K_p: Pyramid,
                                   pg.K_m: Mine}
        self.string_type_dict = {"house": House, "tower": Tower, "road": Road, "wall": Wall, "gate": Gate,
                                 "obama": Pyramid, "farmland": Farmland, "mine": Mine}
        self.soundtrack_channel = pg.mixer.Channel(5)
        self.speech_channel = pg.mixer.Channel(3)

        self.map_surf, self.tile_type_map = self.load_map()
        self.surrounded_tiles = [[0 for _ in range(self.height_tiles)] for _ in range(self.width_tiles)]
        self.struct_map = [[0 for _ in range(self.height_tiles)] for _ in range(self.width_tiles)]
        self.cursor = Cursor(self)
        self.wall_set = set()
        self.entities = Entities()
        self.structs = pg.sprite.Group()
        self.buttons = set()
        self.time_manager = TimeManager(self)
        self.button_handler = ButtonHandler(self)
        self.background = Background(self)

        self.hud = Hud(self)

    def set_window(self):
        """
        Initializes display, caption and icon

            :return: Screen surface
        """
        if self.WINDOWED:
            screen = pg.display.set_mode([self.WINDOW_WIDTH, self.WINDOW_HEIGHT])
        else:
            screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
            self.WINDOW_WIDTH, self.WINDOW_HEIGHT = pg.display.get_surface().get_size()
        pg.display.set_caption("Twierdza: Zawodzie")
        pg.display.set_icon(pg.image.load("assets/icon.png").convert())
        return screen

    def fill_snappers_dict(self):
        """
        Fills dictionaries that assign different version of a Snapper sprite to tuples of directions that the
        sprite has connections with.

            :return: Dictionary of dictionaries for different Snappers
        """
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
        """
        Converts an image representing the layout of terrain to map of tile types and generates a
        background surface.

            :return: Surface of the map terrain, 2-dimensional array of tile types
        """
        color_to_type = {(0, 255, 0, 255): "grassland", (0, 0, 255, 255): "water", (255, 255, 0, 255): "desert"}
        tile_dict = {name: pg.transform.scale(pg.image.load("assets/tiles/" + name + "_tile.png").convert(),
                                              (60, 60)) for name in color_to_type.values()}

        background = pg.Surface((self.width_tiles * 60, self.height_tiles * 60))
        tile_map = [[0 for _ in range(self.height_tiles)] for _ in range(self.width_tiles)]

        for x in range(self.width_tiles):
            for y in range(self.height_tiles):
                tile_color = tuple(self.layout.get_at((x, y)))
                background.blit(tile_dict[color_to_type[tile_color]], (x * 60, y * 60))
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
        """
        Loads sound effects and sountrack to dictionaries

            :return: dictionaries of sounds and tracks
        """
        fx_dir = os.listdir("assets/fx")
        soundtrack_dir = os.listdir("assets/soundtrack")
        sounds = {file[:-4]: pg.mixer.Sound("assets/fx/" + file) for file in fx_dir}
        if self.SOUNDTRACK:
            tracks = [pg.mixer.Sound("assets/soundtrack/" + file) for file in soundtrack_dir]
        else:
            tracks = []
        for track in tracks:
            track.set_volume(0.4)
        for name, sound in sounds.items():
            if not name.startswith("woodrollover"):
                sound.set_volume(0.7)

        return sounds, tracks

    def is_out_of_bounds(self, x, y):
        """
        Determines whether given coordinates are in bounds of the map.

            :param x: X coordinate
            :param y: Y coordinate
        """
        if x < 0: return True
        if x > self.width_tiles - 1: return True
        if y < 0: return True
        if y > self.height_tiles - 1: return True
        return False

    def to_json(self):
        """
        Serializes all relevant data to be suitable for JSON save file.

            :return: Dictionary of serialized relevant data
        """
        return {
            "layout_path": self.layout_path,
            "cursor": self.cursor.to_json(),
            "struct_map": [[struct.to_json() if isinstance(struct, Structure) else 0 for struct in x]
                           for x in self.struct_map],
            "reality": self.time_manager.to_json(),
            "structs": [struct.to_json() for struct in self.structs],
            "entities": [entity.to_json() for entity in self.entities],
            "wall_set": tuple(self.wall_set),
            "gold": self.time_manager.gold
        }

    def from_json(self, json_dict):
        """
        Converts serialized data from JSON save file to actual game contents

            :param json_dict: dictionary of JSON save file
        """
        self.tile_s = 30
        self.entities.empty()
        self.structs.empty()
        self.buttons.clear()
        self.cursor.hold = None

        self.layout_path = json_dict["layout_path"]
        self.layout = pg.image.load(self.layout_path).convert()
        self.height_tiles = self.layout.get_height()
        self.width_tiles = self.layout.get_width()
        self.width_pixels = self.width_tiles * self.tile_s
        self.height_pixels = self.height_tiles * self.tile_s
        self.surrounded_tiles = [[0 for _ in range(self.height_tiles)] for _ in range(self.width_tiles)]
        self.struct_map = [[0 for _ in range(self.height_tiles)] for _ in range(self.width_tiles)]
        self.map_surf, self.tile_type_map = self.load_map()
        self.background = Background(self)

        self.hud = Hud(self)

        for i, x in enumerate(json_dict["struct_map"]):
            for j, y in enumerate(x):
                self.struct_map[i][j] = 0
                if y != 0:
                    if self.string_type_dict[y["type"]] != Gate:
                        loaded_struct = self.string_type_dict[y["type"]](y["pos"], self)
                    else:
                        loaded_struct = self.string_type_dict[y["type"]](y["pos"], self, y["orient"])
                    loaded_struct.from_json(y)
                    self.struct_map[i][j] = loaded_struct
                    self.structs.add(loaded_struct)
                    self.entities.add(loaded_struct)

        self.time_manager.from_json(json_dict["reality"])
        self.wall_set = {tuple(elem) for elem in json_dict["wall_set"]}
        self.time_manager.gold = json_dict["gold"]


class Hud:
    def __init__(self, gw):
        self.are_debug_stats_displayed = True
        self.is_build_menu_open = False

        self.global_statistics = GlobalStatistics(gw)
        self.tile_statistics = TileStatistics(gw)
        self.build_menu = BuildMenu(gw)
        self.minimap = Minimap(gw)
        self.top_bar = TopBar(gw)
        self.pause_menu = PauseMenu(gw)
