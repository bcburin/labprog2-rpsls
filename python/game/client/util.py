from pydantic import ValidationError

from game.server.schemas import PlayerChoiceRequest, EndOfGameMessage


def request_user_input(request: PlayerChoiceRequest) -> str:
    options = {i + 1: shape for i, shape in enumerate(request.options)}
    for i, shape in options.items():
        print(f'[{i}] {shape}')
    choice = int(input('[CHOICE] '))
    return options[choice]


def parse_incoming_message(request_raw) -> PlayerChoiceRequest | EndOfGameMessage:
    try:
        return PlayerChoiceRequest.parse_raw(request_raw)
    except ValidationError:
        return EndOfGameMessage.parse_raw(request_raw)
