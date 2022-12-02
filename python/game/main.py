from pathlib import Path

from game.models.game_config import GameConfig
from game.models.game_state import GameState
from game.models.player import Player
from game.models.shape import Shape


def choose_shape(config: GameConfig, player: Player) -> Shape:
    shapes = config.get_shapes()
    shape_opts = {i+1: shape for i, shape in enumerate(shapes)}
    print()
    for i, shape in shape_opts.items():
        print(f'{i} - {shape.name}')
    print()
    opt = input(f'{player.name}: ')
    chosen_shape = shape_opts[int(opt)]
    return chosen_shape


if __name__ == '__main__':
    # Get game configurations
    config_path = Path.cwd().parent.joinpath('data').joinpath('gameconfig.json')
    game_config = GameConfig.load(path=config_path)
    # Get initial game state
    game_state = GameState.get_initial_state(config=game_config)
    # Run game
    while not game_state.is_finished():
        if game_state.is_end_of_round():
            round_winner = game_state.get_round_winner()
            print(f'{round_winner.name} wins this round!')
        player_choices = {player: choose_shape(player=player, config=game_config)
                          for player in game_state.get_active_players()}
        game_state = game_state.updated_player_choices(player_choices=player_choices)
        game_state = game_state.get_next_state()
    # Display winner
    winner = game_state.get_winner()
    print(f'{winner.name} wins!')
