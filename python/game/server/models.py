from dataclasses import dataclass
from socket import socket


@dataclass(frozen=True)
class PlayerConnection:
    player_name: str
    conn: socket
    addr: str
