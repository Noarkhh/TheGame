from __future__ import annotations

import time
from collections import deque

import pygame as pg

from src.game_mechanics.game_time_clock import GameTimeClock


class TimeManager:
    frame_rate: int
    clock: pg.time.Clock

    def __init__(self, frame_rate: int) -> None:
        self.frame_rate = frame_rate
        self.clock = pg.time.Clock()
        self.game_time_clock = GameTimeClock()
        self.tps: float = 0
        self.mspt: float = 0
        self.tick_start: float = time.perf_counter()
        self.tick_start_no_delay: float = time.perf_counter()
        self.tick_end: float = time.perf_counter()
        self.tick_duration_record: deque[float] = deque([0] * 60)
        self.tick_duration_record_no_delay: deque[float] = deque([0] * 60)

    def tick(self) -> None:
        self.game_time_clock.tick()
        self.tick_end = time.perf_counter()
        self.update_tick_statistics()
        self.tick_start = time.perf_counter()

        self.clock.tick(self.frame_rate)

        self.tick_start_no_delay = time.perf_counter()

    def update_tick_statistics(self) -> None:
        self.tick_duration_record.pop()
        self.tick_duration_record.appendleft(self.tick_end - self.tick_start)
        self.tps = 60 / sum(self.tick_duration_record)

        self.tick_duration_record_no_delay.pop()
        self.tick_duration_record_no_delay.appendleft(self.tick_end - self.tick_start_no_delay)
        self.mspt = sum(self.tick_duration_record_no_delay) * 1000 / 60

    def get_tick_statistics_string(self) -> str:
        return f"TPS: {self.tps:0.2f} MSPT: {self.mspt:0.2f}"
