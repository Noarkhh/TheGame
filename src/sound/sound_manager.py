from __future__ import annotations
import pygame as pg
from src.core.enums import Message
from typing import TYPE_CHECKING, Optional
from random import choice
if TYPE_CHECKING:
    from src.core.config import Config


class SoundManager:
    def __init__(self, config: Config) -> None:
        self.fx_config = config.get_fx_config()
        pg.mixer.set_num_channels(5)

        self.speech_channel = pg.mixer.Channel(0)
        self.fx_channels = [pg.mixer.Channel(i) for i in range(1, 5)]
        pg.mixer.set_num_channels(len(self.fx_channels) + 1)
        pg.mixer.set_reserved(1)
        for channel in self.fx_channels:
            channel.set_volume(0.5)
        self.speech_channel.set_volume(0.5)

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

    def play_sound(self, sound_name: str, channel: Optional[pg.mixer.Channel] = None) -> None:
        selected_sounds = self.sounds[sound_name]
        if isinstance(selected_sounds, list):
            sound_to_play: pg.mixer.Sound = choice(selected_sounds)
        else:
            sound_to_play = selected_sounds

        if channel is not None:
            channel.play(sound_to_play)
        else:
            sound_to_play.play()

    def play_speech(self, sound_name: str) -> None:
        self.play_sound(sound_name, self.speech_channel)

    def play_fx(self, sound_name: str) -> None:
        self.play_sound(sound_name, pg.mixer.find_channel(force=True))

    def handle_placement_sounds(self, play_failure_sounds: bool, play_success_sound: bool,
                                build_message: Message, snap_message: Message) -> None:
        if play_success_sound and (build_message.success() or snap_message.success()):
            self.play_fx("drawbridge_control")
        if play_failure_sounds and not (snap_message.success() or build_message.success()):
            if build_message == Message.NO_RESOURCES:
                self.play_speech("Resource_Need")
            elif snap_message not in (Message.NOT_ADJACENT, Message.ALREADY_SNAPPED) and \
                    (build_message in (Message.BAD_LOCATION_STRUCT, Message.BAD_LOCATION_TERRAIN) or
                     snap_message in (Message.BAD_CONNECTOR, Message.ONE_CANT_SNAP, Message.NOT_A_SNAPPER)):
                self.play_speech("Placement_Warning")





