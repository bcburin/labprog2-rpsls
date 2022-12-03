from socket import socket, AF_INET, SOCK_STREAM

from pydantic import ValidationError

from game.server.schemas import JoinRequest, JoinResponse, PlayerChoiceRequest, PlayerChoiceResponse, EndOfGameRequest

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
        self.play_game()

    def play_game(self):
        while True:
            # Receive request to decide shape or end game
            request_raw = self.client.recv(1024).decode(self.FORMAT)
            request = self.parse_incoming_request(request_raw)
            # Check for end of game
            if isinstance(request, EndOfGameRequest):
                print(f'[END] {request}')
                break
            # Choose
            print(f'[REQUEST] {request}')
            options = {i+1: shape for i, shape in enumerate(request.options)}
            for i, shape in options.items():
                print(f'[{i}] {shape}')
            chosen_shape = int(input('[CHOICE] '))
            # Send Response
            response = PlayerChoiceResponse(
                player_name=request.player_name,
                game_id=request.game_id,
                match_number=request.match_number,
                shape=options[chosen_shape]
            )
            self.client.send(response.json().encode(self.FORMAT))

    @staticmethod
    def parse_incoming_request(request_raw) -> PlayerChoiceRequest | EndOfGameRequest:
        try:
            return PlayerChoiceRequest.parse_raw(request_raw)
        except ValidationError:
            return EndOfGameRequest.parse_raw(request_raw)


if __name__ == '__main__':
    client = GameClient()

    name = input('Name: ')

    client.request_connection()
    client.request_join_game(player_name=name)

