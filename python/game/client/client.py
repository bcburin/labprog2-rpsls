from socket import socket, AF_INET, SOCK_STREAM

from game.client.util import request_user_input, parse_incoming_message
from game.server.schemas import JoinRequest, JoinResponse, PlayerChoiceRequest, PlayerChoiceResponse, EndOfGameMessage

PORT = 40_000
HOST = '127.0.1.1'


class GameClient:
    FORMAT = 'utf-8'

    def __init__(self):
        self.client = socket(AF_INET, SOCK_STREAM)

    def request_connection(self):
        self.client.connect((HOST, PORT))

    def request_join_game(self, player_name: str):
        # Send join request
        request = JoinRequest(player_name=player_name)
        self.client.send(request.json().encode(self.FORMAT))
        # Receive response
        response_raw = self.client.recv(1024).decode(self.FORMAT)
        response = JoinResponse.parse_raw(response_raw)
        print(response)
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
                print(f'[REQUEST] {message}')
                chosen_shape = request_user_input(request=message)
                # Send Response
                response = PlayerChoiceResponse(
                    player_name=message.player_name,
                    game_id=message.game_id,
                    match_number=message.match_number,
                    shape=chosen_shape
                )
                self.client.send(response.json().encode(self.FORMAT))


if __name__ == '__main__':
    client = GameClient()

    name = input('Name: ')

    client.request_connection()
    client.request_join_game(player_name=name)
