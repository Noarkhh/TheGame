from __future__ import annotations
from src.structures import *
from src.map import MapManager
from src.config import Config
from src.spritesheet import Spritesheet
from src.treasury import Treasury
from src.struct_manager import StructManager
from src.scene import Scene
from src.entities import Entities
from src.cursor import Cursor


def a(cls: Type, elem: object):
    return isinstance(elem, cls)


def main() -> None:
    pg.init()
    pg.mixer.init()
    clock = pg.time.Clock()

    config = Config()
    screen = pg.display.set_mode(config.window_size.to_tuple())
    map_manager = MapManager(config)
    entities = Entities()
    cursor = Cursor()
    spritesheet = Spritesheet()
    treasury = Treasury(config)
    struct_manager = StructManager(config, map_manager, spritesheet, treasury, entities)
    scene = Scene(config, spritesheet, map_manager)

    structs = [House(Vector(1, 1)), Wall(Vector(1, 4)), Mine(Vector(0, 1), is_ghost=True), Gate(Vector(5, 5))]
    print(struct_manager.structs.sprites())
    print(Vector(32, 44))

    running = True
    while running:

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

        struct_manager.structs.draw(scene.map_image)
        scene.map_image.blit(cursor.image, cursor.rect)

        cursor.update(scene)
        screen.blit(scene.image, (0, 0))
        print(cursor.rect.topleft, cursor.pos)
        scene.move_screen_border(Vector(pg.mouse.get_pos()))

        scene.image.blit(scene.map_image_raw.subsurface(scene.rect), (0, 0))
        pg.display.flip()
        clock.tick(config.tick_rate)

    pg.quit()


if __name__ == "__main__":
    main()
