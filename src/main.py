from __future__ import annotations
from src.placeholder import *


def main():
    pg.init()
    pg.mixer.init()
    pg.time.Clock()

    screen = pg.display.set_mode([500, 500])
    config = Config()
    sizes = Sizes(config)
    map_manager = MapManager(sizes)
    spritesheet = Spritesheet(sizes)
    treasury = Treasury(config)
    struct_manager = StructManager(sizes, map_manager, spritesheet, treasury)

    structs = [House(Vector(1, 1)), Wall(Vector(1, 4)), Mine(Vector(0, 1), is_ghost=True), Gate(Vector(5, 5))]
    print(struct_manager.structs.sprites())

    map_manager.struct_map[(5, 5)] = structs[1]

    running = True
    while running:

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

            struct_manager.structs.draw(screen)

        pg.display.flip()

    pg.quit()


if __name__ == "__main__":
    main()
