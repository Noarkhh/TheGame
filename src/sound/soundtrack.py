import os

import pygame as pg

from src.core.user_events import END_TRACK


class Soundtrack:
    def __init__(self) -> None:
        self.tracks = os.listdir("assets/soundtrack")
        self.current_track = 0
        pg.mixer.music.set_endevent(END_TRACK)
        self.volume = 0.3
        pg.mixer.music.set_volume(self.volume)

    def start(self) -> None:
        pg.mixer.music.load(f"assets/soundtrack/{self.tracks[self.current_track]}", "mp3")
        self.current_track = (self.current_track + 1) % len(self.tracks)
        self.queue_next_track()
        pg.mixer.music.play()

    def queue_next_track(self) -> None:
        pg.mixer.music.queue(f"assets/soundtrack/{self.tracks[self.current_track]}", "mp3")
        self.current_track = (self.current_track + 1) % len(self.tracks)

    def change_volume(self, amount: float) -> None:
        self.volume += amount
        self.volume = min(1.0, max(0.0, self.volume))
        pg.mixer.music.set_volume(self.volume)
