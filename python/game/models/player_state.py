from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from game.models.player import Player
from game.models.shape import Shape


@dataclass(frozen=True)
class PlayerState:
    choice: Shape | None = None
    active: bool = True

    def updated_choice(self, new_choice: Shape) -> PlayerState:
        return self.updated('choice', new_choice)

    def deactivated(self) -> PlayerState:
        return self.updated('active', False)

    def updated(self, attr: str, val: Any) -> PlayerState:
        return PlayerState(**{**self.__dict__, attr: val})
