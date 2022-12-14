from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any

from game.models.game_config import GameConfig
from game.models.player import Player
from game.models.player_state import PlayerState
from game.models.shape import Shape


@dataclass(frozen=True)
class GameState:
    config: GameConfig
    player_states: dict[Player, PlayerState]
    current_round: int
    past_winners: list[Player]

    @property
    def players(self) -> list[Player]:
        return list(self.player_states.keys())

    @staticmethod
    def get_initial_state(
            config: GameConfig,
            player_names: list[str] | None = None,
            current_round: int = 0,
            past_winners: list[Player] | None = None
    ) -> GameState:
        # Assert correct number of players
        if player_names and len(player_names) != config.num_players:
            raise ValueError(f'Invalid number of players: there must be exactly {config.num_players} players.')
        # Generate default names
        if player_names is None:
            player_names = []
            for i in range(config.num_players):
                player_names.append(f'Player{i+1}')
        # Create player states
        player_states = {Player(name=player_name): PlayerState() for player_name in player_names}
        # Create initial game state
        return GameState(
            config=config,
            player_states=player_states,
            current_round=current_round,
            past_winners=[] if not past_winners else past_winners
        )

    def get_player_choice(self, player) -> Shape | None:
        player_state = self.player_states[player]
        return player_state.choice

    def get_active_players(self):
        return [player for player, player_state in self.player_states.items() if player_state.active]

    def get_unready_players(self):
        return [player for player in self.get_active_players() if self.player_states[player].choice is None]

    def confront_two_players(self, player1, player2) -> int:
        player1_choice = self.get_player_choice(player=player1)
        player2_choice = self.get_player_choice(player=player2)
        player1_defeated_shapes = self.config.get_defeated_shapes(shape=player1_choice)
        return 1 if player2_choice in player1_defeated_shapes else 0

    def confront_all_players(self) -> dict[Player, int]:
        # Find players that are still active
        active_players = self.get_active_players()
        # Initialize map to count victories
        player_win_counts = {player: 0 for player in active_players}
        # Iterate all active players
        for player in active_players:
            for confronted_player in active_players:
                if confronted_player != player:
                    player_win_counts[player] += self.confront_two_players(player1=player, player2=confronted_player)
        return player_win_counts

    def is_ready_for_confrontation(self):
        for player in self.get_active_players():
            if self.get_player_choice(player=player) is None:
                return False
        return True

    def is_finished(self) -> bool:
        return len(self.past_winners) == self.config.rounds

    def get_winner(self) -> Player | None:
        if not self.is_finished():
            return None
        # Get player with most wins
        win_count = {player: 0 for player in self.players}
        for player in self.past_winners:
            win_count[player] += 1
        winner = max(win_count, key=win_count.get)
        return winner

    def is_end_of_round(self) -> bool:
        return len(self.get_active_players()) == 1

    def get_round_winner(self) -> Player | None:
        if not self.is_end_of_round():
            return None
        return self.get_active_players()[0]

    def get_next_state(self) -> GameState:
        if self.is_end_of_round():
            return self.get_next_round()
        if not self.is_ready_for_confrontation():
            return self
        # Get win count for each player
        player_win_counts = self.confront_all_players()
        # Get the highest win count
        max_count_player = max(player_win_counts, key=player_win_counts.get)
        # Find losers
        losers = [player for player in self.get_active_players()
                  if player_win_counts[player] != player_win_counts[max_count_player]]
        # Deactivate losers
        new_state = self.deactivated_players(players=losers)
        # Return next state
        return new_state

    def get_next_round(self) -> GameState:
        if not self.is_end_of_round():
            return self
        winners = deepcopy(self.past_winners)
        winners.append(self.get_active_players()[0])
        return GameState.get_initial_state(
            config=self.config,
            player_names=[player.name for player in self.players],
            current_round=self.current_round + 1,
            past_winners=winners
        )

    def updated_player_choice(self, player: Player, choice: Shape):
        player_state = self.player_states[player].updated_choice(new_choice=choice)
        player_states = deepcopy(self.player_states)
        player_states[player] = player_state
        return self.updated('player_states', player_states)

    def updated_player_choices(self, player_choices: dict[Player, Shape]) -> GameState:
        state = self
        for player, choice in player_choices.items():
            state = state.updated_player_choice(player, choice)
        return state

    def reset_choices(self) -> GameState:
        return self.updated_player_choices(player_choices={player: None for player in self.players})

    def deactivated_player(self, player: Player) -> GameState:
        player_state = self.player_states[player].deactivated()
        player_states = deepcopy(self.player_states)
        player_states[player] = player_state
        return self.updated('player_states', player_states)

    def deactivated_players(self, players) -> GameState:
        state = self
        for player in players:
            state = state.deactivated_player(player=player)
        return state

    def incremented_round(self) -> GameState:
        return self.updated('current_round', self.current_round + 1)

    def updated(self, attr: str, val: Any) -> GameState:
        return GameState(**{**self.__dict__, attr: val})

    def __str__(self) -> str:
        desc = f'Rounds: {self.current_round + 1}/{self.config.rounds}\n'
        desc += f'Past winners: {", ".join([player.name for player in self.past_winners])}\n' \
            if self.past_winners else ''
        desc += f'Player choices:\n'
        for player, player_state in self.player_states.items():
            desc += f'\t{player.name} - {player_state.choice}\n'
        return desc
