from socket import socket, AF_INET, SOCK_STREAM

from game.client.bot import GameBot
from game.client.util import request_user_input, parse_incoming_message
from game.server.schemas import JoinRequest, JoinResponse, PlayerChoiceRequest, PlayerChoiceResponse, EndOfGameMessage
from game.utils.protocol import encode


class GameClient:
    FORMAT = 'utf-8'

    def __init__(self, player_name: str, is_bot: bool = False):
        self.client = socket(AF_INET, SOCK_STREAM)
        self.player_name = player_name
        self.is_bot = is_bot
        self.bot: GameBot | None = None

    def request_join_game(self, server_host: str, server_port: int):
        # Connect to server
        self.client.connect((server_host, server_port))
        # Send join request
        request = JoinRequest(player_name=self.player_name)
        self.client.send(encode(request))
        # Receive response
        response_raw = self.client.recv(1024).decode(self.FORMAT)
        response = JoinResponse.parse_raw(response_raw)
        # Create bot
        if self.is_bot:
            self.bot = GameBot(player_name=self.player_name, total_rounds=response.total_rounds)
        # Play game for successful join response
        self.play_game()

    def play_game(self):
        while True:
            # Receive message to decide shape or end game
            message_raw = self.client.recv(1024).decode(self.FORMAT)
            message = parse_incoming_message(message_raw)
            # Check for end of game
            if isinstance(message, EndOfGameMessage):
                print(f'[END] {message}')
                break
            # Check for player choice request
            if isinstance(message, PlayerChoiceRequest):
                chosen_shape = None
                if self.is_bot:
                    self.bot.add_request_content(request=message)
                    chosen_shape = self.bot.decide()
                else:
                    print(f'[REQUEST] {message}')
                    chosen_shape = request_user_input(request=message)
                # Send Response
                response = PlayerChoiceResponse(
                    player_name=message.player_name,
                    game_id=message.game_id,
                    match_number=message.match_number,
                    shape=chosen_shape
                )
                self.client.send(encode(response))
