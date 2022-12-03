from asyncio import Queue
from pathlib import Path
from socket import socket, gethostbyname, gethostname, AF_INET, SOCK_STREAM
from threading import Thread, active_count
from uuid import uuid1, UUID

from game.models.game_config import GameConfig
from game.models.game_state import GameState
from game.models.shape import Shape
from game.server.models import PlayerConnection
from game.server.schemas import JoinRequest, JoinResponse, \
    PlayerChoiceRequest, PlayerChoiceResponse, PlayerChoiceInfo, EndOfGameRequest


class GameServer:

    FORMAT = 'utf-8'

    def __init__(self, host: str, port: int, game_config: GameConfig):
        self.server = socket(AF_INET, SOCK_STREAM)
        self.server.bind((host, port))
        self.queue = Queue[PlayerConnection]()
        self.game_config = game_config
        print('[STARTING] Server is starting.')

    def start(self):
        self.server.listen()
        print(f'[LISTENING] Server is listening on {HOST}.')
        while True:
            # Handle server queue of waiting players
            queue_thread = Thread(target=self.handle_queue)
            queue_thread.start()
            # Handle incoming requests
            conn, addr = self.server.accept()
            thread = Thread(target=self.handle_player, args=(conn, addr))
            thread.start()
            # Log active connection
            print(f'[ACTIVE CONNECTIONS] {active_count() - 1}.')

    def handle_player(self, conn: socket, addr: str):
        print(f'[NEW_CONNECTION] {addr} connected.')
        # Read player request
        request_raw = conn.recv(1024).decode(self.FORMAT)
        request = JoinRequest.parse_raw(request_raw)
        # Add player to queue
        player_conn = PlayerConnection(player_name=request.player_name, conn=conn, addr=addr)
        self.queue.put_nowait(player_conn)

    def handle_queue(self):
        while True:
            if self.queue.qsize() > 1:
                player_conn1 = self.queue.get_nowait()
                player_conn2 = self.queue.get_nowait()
                thread = Thread(target=self.handle_game, args=(player_conn1, player_conn2))
                thread.start()

    def request_player_choice(
            self, player_conn: PlayerConnection, game_id: UUID, match_number: int, game_state: GameState
    ) -> Shape | None:
        # Send request
        request = PlayerChoiceRequest(
            player_name=player_conn.player_name,
            game_id=game_id,
            match_number=match_number,
            options=[shape.name for shape in self.game_config.rules.keys()],
            current_round=game_state.current_round+1,
            total_rounds=game_state.config.rounds,
            past_winners=[player.name for player in game_state.past_winners],
            player_choices=[
                PlayerChoiceInfo(
                    player_name=player.name, shape=player_state.choice.name if player_state.choice else None
                ) for player, player_state in game_state.player_states.items()]
        )
        player_conn.conn.send(request.json().encode(self.FORMAT))
        # Receive client response
        response_raw = player_conn.conn.recv(1024).decode(self.FORMAT)
        response = PlayerChoiceResponse.parse_raw(response_raw)
        # Assert request and response match
        if any([request.game_id != response.game_id,
                request.match_number != response.match_number,
                request.player_name != response.player_name]):
            return None
        # Parse response
        for shape in self.game_config.rules.keys():
            if shape.name == response.shape:
                return shape

    def handle_game(self, player_conn1: PlayerConnection, player_conn2: PlayerConnection):
        players = [player_conn1.player_name, player_conn2.player_name]
        game_id = uuid1()
        # Generate responses
        response1 = JoinResponse(player_name=player_conn1.player_name, players=players, game_id=game_id)
        response2 = JoinResponse(player_name=player_conn2.player_name, players=players, game_id=game_id)
        # Send responses
        player_conn1.conn.send(response1.json().encode(self.FORMAT))
        player_conn2.conn.send(response2.json().encode(self.FORMAT))
        # Get initial game state
        game_state = GameState.get_initial_state(
            config=self.game_config, player_names=[player_conn1.player_name, player_conn2.player_name])
        # Map player objects to connections
        players_map = {game_state.players[0]: player_conn1, game_state.players[1]: player_conn2}
        # Run game
        math_number = 1
        while not game_state.is_finished():
            # game_state = game_state.reset_choices()
            player_choices = {
                player: self.request_player_choice(
                    player_conn=player_conn, game_id=game_id, match_number=math_number, game_state=game_state)
                for player, player_conn in players_map.items()
            }
            game_state = game_state.updated_player_choices(player_choices=player_choices)
            game_state = game_state.get_next_state()
            if game_state.is_end_of_round():
                game_state = game_state.get_next_round()
            math_number += 1
        # Inform winner
        winner = players_map[game_state.get_winner()]
        print(f'[{game_id}] {winner.conn} a.k.a {winner.player_name} wins.')
        end_request = EndOfGameRequest(
            current_round=game_state.current_round,
            total_rounds=game_state.config.rounds,
            past_winners=[player.name for player in game_state.past_winners],
            player_choices=[
                PlayerChoiceInfo(
                    player_name=player.name,
                    shape=player_state.choice.name if player_state.choice else None
                ) for player, player_state in game_state.player_states.items()],
            winner=winner.player_name
        )
        player_conn1.conn.send(end_request.json().encode(self.FORMAT))
        player_conn2.conn.send(end_request.json().encode(self.FORMAT))
        # Close connections
        player_conn1.conn.close()
        player_conn2.conn.close()


if __name__ == '__main__':
    PORT = 40_000
    HOST = gethostbyname(gethostname())

    # Get game configurations
    config_path = Path.cwd().parent.parent.parent.joinpath('data').joinpath('gameconfig.json')
    config = GameConfig.load(path=config_path)

    server = GameServer(host=HOST, port=PORT, game_config=config)
    server.start()
