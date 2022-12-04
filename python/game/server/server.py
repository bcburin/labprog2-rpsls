import logging
from asyncio import Queue
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
from uuid import uuid1, UUID

from game.models.game_config import GameConfig
from game.models.game_state import GameState
from game.models.shape import Shape
from game.server.models import PlayerConnection
from game.server.schemas import JoinRequest, JoinResponse, \
    PlayerChoiceRequest, PlayerChoiceResponse, PlayerChoiceInfo, EndOfGameMessage
from game.utils.logging import configure_logger


class GameServer:

    FORMAT = 'utf-8'

    def __init__(self, host: str, port: int, game_config: GameConfig, verbose: bool = True):
        self.server = socket(AF_INET, SOCK_STREAM)
        self.host = host
        self.port = port
        self.server.bind((host, port))
        self.queue = Queue[PlayerConnection]()
        self.game_config = game_config
        self.active_connections = 0
        # Configure logger
        configure_logger(filename='server.log', level=logging.INFO if verbose else logging.WARNING)
        # Log start of server
        logging.info(f'[STARTING] Server is starting at {host, port}.')

    def start(self):
        self.server.listen()
        logging.info(f'[LISTENING] Server is listening on {self.host}.')
        # Handle server queue of waiting players
        queue_thread = Thread(target=self.handle_queue)
        queue_thread.start()
        try:
            while True:
                # Handle incoming requests
                conn, addr = self.server.accept()
                thread = Thread(target=self.handle_player, args=(conn, addr))
                thread.start()
        except KeyboardInterrupt:
            self.server.close()
            exit(0)

    def handle_player(self, conn: socket, addr: str):
        self.active_connections += 1
        # Read player request
        request_raw = conn.recv(1024).decode(self.FORMAT)
        request = JoinRequest.parse_raw(request_raw)
        # Log connection
        logging.info(f'[NEW_CONNECTION] {request.player_name} {addr} connected.')
        logging.info(f'[ACTIVE_CONNECTIONS] {self.active_connections}')
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
        logging.info(f'[{game_id}] New game created with {player_conn1} and {player_conn2})')
        # Generate responses
        response1 = JoinResponse(
            player_name=player_conn1.player_name,
            players=players, game_id=game_id,
            total_rounds=self.game_config.rounds)
        response2 = JoinResponse(
            player_name=player_conn2.player_name,
            players=players, game_id=game_id,
            total_rounds=self.game_config.rounds)
        # Send responses
        player_conn1.conn.send(response1.json().encode(self.FORMAT))
        player_conn2.conn.send(response2.json().encode(self.FORMAT))
        # Get initial game state
        game_state = GameState.get_initial_state(
            config=self.game_config, player_names=[player_conn1.player_name, player_conn2.player_name])
        # Map player objects to connections
        players_map = {game_state.players[0]: player_conn1, game_state.players[1]: player_conn2}
        # Run game
        match_number = 1
        while not game_state.is_finished():
            # Request clients to each choose a shape
            player_choices = {
                player: self.request_player_choice(
                    player_conn=player_conn,
                    game_id=game_id,
                    match_number=match_number,
                    game_state=game_state
                )
                for player, player_conn in players_map.items()
            }
            # Log player choices
            for player, shape in player_choices.items():
                logging.info(f'[{game_id}] {players_map[player]} chooses {shape.name}.')
            # Go to next game state with player choices
            game_state = game_state.updated_player_choices(player_choices=player_choices)
            game_state = game_state.get_next_state()
            # Handle rounds
            if game_state.is_end_of_round():
                logging.info(f'[{game_id}] '
                             f'{players_map[game_state.get_round_winner()]} wins round {game_state.current_round+1}.')
                game_state = game_state.get_next_round().updated_player_choices(player_choices)
            else:
                tied_players = (", ".join([
                    f"{players_map[player]} chose {game_state.player_states[player].choice.name}"
                    for player in game_state.get_active_players()]))
                logging.info(
                    f'[{game_id}] tie: {tied_players}')
            match_number += 1
        # Inform winner
        winner = players_map[game_state.get_winner()]
        logging.info(f'[{game_id}] {winner} wins.')
        end_request = EndOfGameMessage(
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
        self.active_connections -= 2
        logging.info(f'[ACTIVE_CONNECTIONS] {self.active_connections}')
