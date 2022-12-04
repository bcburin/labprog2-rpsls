from dataclasses import dataclass


@dataclass(frozen=True)
class PlayerChoice:
    player_name: str
    shape: str


@dataclass(frozen=True)
class MatchSummary:
    winner: str | None
    player_choices: list[PlayerChoice]
