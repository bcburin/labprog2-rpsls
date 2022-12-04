from pathlib import Path
from random import choice

from game.client.models import MatchSummary, PlayerChoice
from game.models.game_config import GameConfig
from game.models.shape import Shape
from game.server.schemas import PlayerChoiceRequest


class GameBot:

    def __init__(self, player_name: str, total_rounds: int):
        self.player_name = player_name
        self.history: list[MatchSummary] = []
        self.past_winners = []
        self.current_round = 0
        self.total_rounds = total_rounds
        # Get game config
        config_path = Path.cwd().parent.joinpath('data').joinpath('gameconfig.json')
        self.game_config = GameConfig.load(path=config_path)

    def add_request_content(self, request: PlayerChoiceRequest):
        self.past_winners = request.past_winners
        self.current_round = request.current_round
        self.total_rounds = request.total_rounds
        # Find winner of last match
        winner = None
        if len(self.past_winners) != len(request.past_winners):
            winner = request.past_winners[-1]
        # Create last match summery
        last_match_summary = MatchSummary(
            winner=winner,
            player_choices=[
                PlayerChoice(
                    player_name=player_choice.player_name,
                    shape=player_choice.shape)
                for player_choice in request.player_choices]
        )
        # Add to history
        self.history.append(last_match_summary)

    def decide(self) -> str:
        # Find result of last match
        last_match = self.history[-1]
        # Find choice of opponent
        op_choice = None
        for player_choice in last_match.player_choices:
            if player_choice.player_name != self.player_name:
                op_choice = player_choice.shape
                break
        # If there is no information, chose random shape
        if op_choice is None:
            return choice(self.game_config.get_shapes()).name
        op_shape = Shape(name=op_choice)
        # Find shape that defeats opponent choice
        for shape in self.game_config.get_shapes():
            if op_shape in self.game_config.get_defeated_shapes(shape=shape):
                return shape.name
