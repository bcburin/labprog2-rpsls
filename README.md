# Rock, Paper, Scissors, Lizard, Spock

This project implements the Rock-Scissors-Paper-Lizard-Spock game through the use of a client-server architecture. The server was implemented in python and can be found in python/game/server. Two clients were implemented, one in java and one in python. The server handles the game for any combination of clients.

## Client-Server Communication

Each client communicates to the server with a JSON based protocol. First, the client request a connection and then the server waits for an opponent and sends a response when it finds one. After that, a series of matches occurr, consisting of requests sent by the server to each client to choose a shape and client responses containing the chosen shape. Finally, the server sends a message informing both clients when the game ends.

### Opening Connection

The server expects a client to initiate communication. The client can do so by sending a `JoinRequest` in json format containing its name

```json
{
  "name_name": "PlayerName"
}
```

Then the server places places that client in a waiting queue. When another client sends a join request and is placed in the queue, the server removes both from the queue and starts a new game, sending each of them a `JoinResponse`

```json
{
  "player_name": "PlayerName",
  "players": ["playerName", "otherPlayerName"],
  "game_id": "219c7762-738d-11ed-97f6-c16c4df8ffda",
  "total_rounds": 15
}
```

### Playing the Game

The server then sends each player a `PlayerChoiceRequest`, asking them to choose a shape for the game

```json
{
  "player_name": "PlayerName",
  "game_id": "219c7762-738d-11ed-97f6-c16c4df8ffda",
  "match_number": 3,
  "current_round": 2,
  "total_rounds": 15,
  "past_winners": ["OtherPlayerName"],
  "player_choices": [
    {
      "player_name": "PlayerName",
      "shape": "Rock"
    },
    {
      "player_name": "OtherPlayerName",
      "shape": "Paper"
    }
  ],
  "options": ["Rock", "Paper", "Scissors", "Lizard", "Spock"]
}
```

The client then chooses one of the available options, either manually or via bot, and sends a `PlayerChoiceResponse`

```json
{
  "player_name": "PlayerName",
  "game_id": "219c7762-738d-11ed-97f6-c16c4df8ffda",
  "match_number": 3,
  "shape": "Scissors"
}
```

### Ending the Game

When the game terminates, the server sends each player an `EndOfGameMessage`, instead of a `PlayerChoiceRequest`

```json
{
  "current_round": 15,
  "total_rounds": 15,
  "past_winners": ["OtherPlayerName", "PlayerName", ..., "PlayerName"],
  "player_choices": [
    {
      "player_name": "PlayerName",
      "shape": "Paper"
    },
    {
      "player_name": "OtherPlayerName",
      "shape": "Rock"
    }
  ],
  "winner": "PlayerName"
}
```

Sequentially, the server ends the connection to both clients.

## Bots

Each client (Python and Java) implements a bot that automates the decision of choosing a shape

### Python Bot

The Python bot stores the whole history of the game, and choses the shape that would defeat the shape the opponent chose last.

```python
def decide(self) -> str:
    # Find result of last match
    last_match = self.history[-1]
    # Find choice of opponent
    op_choice = None
    for player_choice in last_match.player_choices:
        if player_choice.player_name != self.player_name:
            op_choice = player_choice.shape
            break
    # If there is no information, chose random shape
    if op_choice is None:
        return choice(self.game_config.get_shapes()).name
    op_shape = Shape(name=op_choice)
    # Find shape that defeats opponent choice
    for shape in self.game_config.get_shapes():
        if op_shape in self.game_config.get_defeated_shapes(shape=shape):
            return shape.name
```

### Java Bot

The Java bot simply mirrors the opponent's last action.

```java
public String decideShape(PlayerChoiceRequest request) {
    // Find last decision of the opponent
    String shape = null;
    for(PlayerChoiceInfo playerChoice : request.player_choices) {
        if (!Objects.equals(playerChoice.player_name, request.player_name)) {
            shape = playerChoice.shape;
        }
    }
    // If none was found, set it to the first option
    if (shape == null) {
        shape = request.options.get(0);
    }
    return shape;
}
```

## Runnig

### Server

The server can be started by running the following command inside the `python` folder

```bash
python3 -m game.main --server --verbose
```

_Note: use python instead of python3 if using windows_

- The `--server` option instructs the interpreter to intialize a server, and not a client
- The `--verbose` option allows the server to log the optput to console and to _server.log_

The server can receive two other options: `--host`, that takes the IP address of the server, and `--port` that takes the port the server is running on. If none are given, the host address and port 40 000 are used.

### Python Client

The python client can be started by running the following command inside the `python` folder

```bash
python3 -m game.main --client --bot -n "PythonBot"
```

_Note: use python instead of python3 if using windows_

- The `--client` option instructs the interpreter to intialize a client, and not a server
- The `--bot` option creates a bot client
- The optional `-n` takes the name the client will use when opening connection with the server

The client can also receive two other options: `--host`, that takes the IP address of the server, and `--port` that takes the port the server is running on. If none are given, the host address and port 40 000 are used.

### Java client

The Java client can be run with Maven using the following CLI parameters

```bash
JavaBot 127.0.1.1 40000
```

The first is the name the client will use when requesting a connection, the second is the IP address of the server, and the third is the port the server is running in.
