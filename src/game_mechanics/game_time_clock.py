from __future__ import annotations


class GameTimeClock:
    def __init__(self) -> None:
        self.minutes: int = 0
        self.hours: int = 12
        self.days: int = 1
        self.weeks: int = 1
        self.display_state_changed: bool = True

    def tick(self) -> None:
        self.minutes += 1
        if self.minutes < 60:
            return
        self.minutes = 0
        self.hours += 1
        self.display_state_changed = True
        if self.hours < 24:
            return
        self.hours = 0
        self.days += 1
        if self.days < 8:
            return
        self.days = 1
        self.weeks += 1

    def get_date_string(self) -> str:
        return f"{'0' if self.hours < 10 else ''}{self.hours}:00, Day {self.days}, Week {self.weeks}"
