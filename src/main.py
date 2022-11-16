from __future__ import annotations
from src.structures import *
from src.map import MapManager
from src.config import Config
from src.spritesheet import Spritesheet
from src.treasury import Treasury
from src.struct_manager import StructManager
from src.scene import Scene


def main() -> None:
    pg.init()
    pg.mixer.init()
    pg.time.Clock()

    config = Config()
    screen = pg.display.set_mode(config.window_size.to_tuple())
    map_manager = MapManager(config)
    spritesheet = Spritesheet()
    treasury = Treasury(config)
    struct_manager = StructManager(config, map_manager, spritesheet, treasury)
    scene = Scene(config, spritesheet, map_manager)

    structs = [House(Vector(1, 1)), Wall(Vector(1, 4)), Mine(Vector(0, 1), is_ghost=True), Gate(Vector(5, 5))]
    print(struct_manager.structs.sprites())


    running = True
    while running:

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

            screen.blit(scene.image, (0, 0))
            scene.move_screen_border(Vector(*pg.mouse.get_pos()))
            # struct_manager.structs.draw(screen)

        pg.display.flip()

    pg.quit()


if __name__ == "__main__":
    main()
