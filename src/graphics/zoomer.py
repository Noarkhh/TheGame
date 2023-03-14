from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from src.core.enums import Tile

if TYPE_CHECKING:
    from src.entities.entities import Entities
    from src.graphics.scene import Scene
    from src.game_mechanics.map_container import MapContainer
    from src.core.cursor import Cursor
    from src.ui.elements.minimap import Minimap
    from src.ui.ui import UI
    from src.ui.button import Button


class Zoomer:
    entities: Entities
    scene: Scene
    map_container: MapContainer
    cursor: Cursor
    minimap: Minimap

    def __init__(self, entities: Entities, scene: Scene, map_container: MapContainer, cursor: Cursor, ui: UI) -> None:
        self.entities = entities
        self.scene = scene
        self.map_container = map_container
        self.cursor = cursor
        self.minimap = ui.minimap

        ui.toolbar.assign_function("zoom_in", self.change_zoom, (2,))
        ui.toolbar.assign_function("zoom_out", self.change_zoom, (0.5,))

    def change_zoom(self, factor: float, button: Optional[Button] = None) -> None:
        if (Tile.size <= 15 and factor < 1) or (Tile.size >= 120 and factor > 1):
            return
        Tile.size = int(Tile.size * factor)

        self.entities.update_zoom()
        self.scene.update_zoom(factor)
        self.map_container.update_zoom(factor)
        self.minimap.update_zoom()

