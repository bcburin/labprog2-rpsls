from uuid import UUID

from pydantic import BaseModel


class JoinRequest(BaseModel):
    player_name: str


class JoinResponse(BaseModel):
    player_name: str
    players: list[str]
    game_id: UUID


class PlayerChoiceInfo(BaseModel):
    player_name: str
    shape: str | None


class GameStateInfo(BaseModel):
    current_round: int
    total_rounds: int
    past_winners: list[str]
    player_choices: list[PlayerChoiceInfo]


class PlayerChoiceBase(BaseModel):
    player_name: str
    game_id: UUID
    match_number: int


class PlayerChoiceRequest(PlayerChoiceBase, GameStateInfo):
    options: list[str]


class PlayerChoiceResponse(PlayerChoiceBase):
    shape: str


class EndOfGameMessage(GameStateInfo):
    winner: str

