from __future__ import annotations
from src.game_mechanics.structures import *
from src.game_mechanics.map_manager import MapManager
from src.config import Config
from src.graphics.spritesheet import Spritesheet
from src.game_mechanics.treasury import Treasury
from src.game_mechanics.struct_manager import StructManager
from src.graphics.scene import Scene
from src.graphics.entities import Entities
from src.cursor import Cursor
from src.setup import Setup
from src.sound.sound_manager import SoundManager

from typing import Protocol
from random import randint

class _HasImageAndRect(Protocol):
    rect: pg.rect.Rect
    image: pg.surface.Surface


class _HasResource(Protocol):
    resource: Resource

IR = TypeVar("IR", bound=_HasImageAndRect)

class _SupportsMine(_HasResource, _HasImageAndRect, Protocol): ...


class Struct:
    rect: pg.rect.Rect
    image: pg.surface.Surface
    resource: Resource

    def __init__(self) -> None:
        self.image: pg.surface.Surface = pg.surface.Surface((0, 0))
        self.rect: pg.rect.Rect = self.image.get_rect()


def main() -> None:
    Setup()

    pg.init()
    pg.mixer.init()
    clock: pg.time.Clock = pg.time.Clock()

    config = Config()
    screen = pg.display.set_mode(config.window_size.to_tuple())
    map_manager = MapManager(config)
    cursor = Cursor()
    spritesheet = Spritesheet(config)
    entities = Entities(spritesheet=spritesheet)
    treasury = Treasury(config)
    sound_manager = SoundManager(config)
    struct_manager = StructManager(config, map_manager, treasury, sound_manager)
    scene = Scene(config, spritesheet, map_manager)

    structs = [House(Vector(1, 1)), Wall(Vector(1, 4)), Mine(Vector(0, 1), is_ghost=True), Gate(Vector(5, 5))]
    a: list[_SupportsMine] = [Struct()]

    class MyGroup(Generic[IR]):
        l: list[IR]

        def __init__(self, *args: IR):
            self.l = []
            if args:
                for arg in args:
                    self.l.append(arg)

        def add(self, spr: IR) -> None:
            self.l.append(spr)

    class MySprite(pg.sprite.Sprite):
        image: pg.surface.Surface
        # rect: pg.rect.Rect

    # b = pg.sprite.Group(MySprite())
    # b: pg.sprite.Group = pg.sprite.Group()
    # b.add(MySprite())

    # g: MySprite = MySprite()
    # h: MySprite = MySprite()
    # i: MyGroup[MySprite] = MyGroup()
    # i.add(g)
    # j = pg.sprite.Group[Structure]

    running = True
    while running:

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

        struct_manager.structs.draw(scene.map_image)
        scene.map_image.blit(cursor.image, cursor.rect)

        cursor.update(scene)
        screen.blit(scene.image, (0, 0))
        scene.move_screen_border(Vector(pg.mouse.get_pos()))

        scene.image.blit(scene.map_image_raw.subsurface(scene.rect), (0, 0))
        pg.display.flip()
        clock.tick(config.frame_rate)

    pg.quit()


if __name__ == "__main__":
    main()
