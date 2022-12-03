from __future__ import annotations

from dataclasses import dataclass
from json import load
from pathlib import Path

from game.models.player import Player
from game.models.shape import Shape


@dataclass(frozen=True)
class GameConfig:
    num_players: int
    rules: dict[Shape, set[Shape]]
    rounds: int

    def get_shapes(self) -> list[Shape]:
        return list(self.rules.keys())

    def get_defeated_shapes(self, shape: Shape):
        return self.rules[shape]

    @classmethod
    def load(cls, path) -> GameConfig:
        with open(path) as config_file:
            config_dict = load(config_file)
            num_players = config_dict['numplayers']
            rules = {
                Shape(name=shape_name):
                    set([Shape(name=other_shape_name) for other_shape_name in other_shapes])
                for shape_name, other_shapes in config_dict['rules'].items()
            }
            rounds = config_dict['rounds']
        return cls(num_players=num_players, rules=rules, rounds=rounds)


if __name__ == '__main__':
    json_path = Path.cwd().parent.parent.parent.joinpath('data').joinpath('gameconfig.json')
    game_config = GameConfig.load(path=json_path)
    print()
