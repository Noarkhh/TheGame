from __future__ import annotations
import pygame as pg
from src.core_classes import Message
from typing import TYPE_CHECKING
from random import choice
if TYPE_CHECKING:
    from src.config import Config


class SoundManager:
    def __init__(self, config: Config) -> None:
        self.fx_config = config.get_fx_config()
        self.sounds: dict[str, pg.mixer.Sound | list[pg.mixer.Sound]] = {}
        self.load_sounds()

    def load_sounds(self) -> None:
        for sound_name, sound_specs in self.fx_config.items():
            variants = sound_specs.get("variants", 1)
            volume = sound_specs.get("volume", 100) / 100
            if variants > 1:
                sound_list = []
                for v in range(1, variants + 1):
                    sound = pg.mixer.Sound(f"../assets/fx/{sound_name}{v}.wav")
                    sound.set_volume(volume)
                    sound_list.append(sound)
                self.sounds[sound_name] = sound_list
            else:
                sound = pg.mixer.Sound(f"../assets/fx/{sound_name}.wav")
                sound.set_volume(volume)
                self.sounds[sound_name] = sound

    def play_sound(self, sound_name: str):
        selected_sounds = self.sounds[sound_name]
        if isinstance(selected_sounds, list):
            choice(selected_sounds).play()
        else:
            selected_sounds.play()

    def handle_placement_sounds(self, play_failure_sounds: bool, play_success_sound: bool,
                                build_message: Message, snap_message: Message) -> None:
        if play_success_sound:
            if build_message.success() or snap_message.success():
                self.play_sound("draw")


