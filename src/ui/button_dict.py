from src.ui.button import Button


class ButtonDict(dict[str, Button]):

    def __getattr__(self, item: str) -> Button:
        return self[item]

    def __setattr__(self, key: str, value: Button) -> None:
        self[key] = value
