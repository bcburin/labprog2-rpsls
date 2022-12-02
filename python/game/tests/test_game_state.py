from pathlib import Path
from unittest import TestCase, main

from game.models.game_config import GameConfig
from game.models.game_state import GameState


class TestGameState(TestCase):

    @staticmethod
    def load_game_config() -> GameConfig:
        json_path = Path.cwd().parent.parent.parent.joinpath('data').joinpath('gameconfig.json')
        return GameConfig.load(path=json_path)

    @staticmethod
    def get_initial_state() -> GameState:
        config = TestGameState.load_game_config()
        return GameState.get_initial_state(config=config)

    def test_initial_state(self):
        game_state = self.get_initial_state()
        player1 = game_state.players[0]
        player2 = game_state.players[1]
        self.assertTrue(player1.name == 'Player1')
        self.assertTrue(player2.name == 'Player2')
        self.assertTrue(game_state.player_states[player1].player == player1)
        self.assertTrue(game_state.player_states[player2].player == player2)
        self.assertTrue(game_state.player_states[player1].choice is None)
        self.assertTrue(game_state.player_states[player2].choice is None)
        self.assertTrue(game_state.player_states[player1].active)
        self.assertTrue(game_state.player_states[player2].active)


if __name__ == '__main__':
    main()
