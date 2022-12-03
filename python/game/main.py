from _socket import gethostbyname, gethostname
from argparse import ArgumentParser
from pathlib import Path

from game.client.client import GameClient
from game.models.game_config import GameConfig
from game.server.server import GameServer


DEFAULT_SERVER_PORT = 40_000
DEFAULT_SERVER_HOST = gethostbyname(gethostname())

DEFAULT_CLIENT_NAME = 'PythonClient'


if __name__ == '__main__':
    # Create parser
    parser = ArgumentParser()
    # Server configuration options
    parser.add_argument('--server', action='store_true')
    parser.add_argument('--port')
    parser.add_argument('--host')
    # Client configuration options
    parser.add_argument('--client', action='store_true')  # Default
    parser.add_argument('--bot', action='store_true')
    parser.add_argument('--name', '-n')
    # Parse arguments
    args = parser.parse_args()
    port = int(args.port or DEFAULT_SERVER_PORT)
    host = args.host or DEFAULT_SERVER_HOST
    # Program must be run as either client or server
    if args.server == args.client:
        raise ValueError('Program must be executed as either client or server')
    # Server
    if args.server:
        # Read game configurations
        config_path = Path.cwd().parent.joinpath('data').joinpath('gameconfig.json')
        config = GameConfig.load(path=config_path)
        # Create server
        server = GameServer(host=host, port=port, game_config=config)
        # Run server
        server.start()
    # Client
    if args.client:
        client = GameClient(player_name=args.name or DEFAULT_CLIENT_NAME, is_bot=args.bot)
        client.request_join_game(server_host=host, server_port=port)
