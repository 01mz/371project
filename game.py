from socket import socket
from threading import Lock
from typing import List, Optional

from constant import BOARD_SIZE, MAX_PLAYERS, MIN_PLAYERS, Action

class Player:
    def __init__(self, socket: socket, id: int):
        self.socket = socket
        self.id = id


class Box:
    def __init__(self):
        self.claim: Optional[Player] = None
        self.hold: Optional[Player] = None

    # Player can claim a box if it is hold by themself
    def canBeClaim(self, player: Player):
        if self.hold != player:
            return False
        self.claim = player
        self.hold = None
        return True

    # Player can hold a box if it is not on hold or being claimed
    def canBeHeld(self, player: Player):
        if self.hold is not None or self.claim is not None:
            return False
        self.hold = player
        return True

    # Release the box from being on hold
    def canBeReleased(self, player: Player):
        if self.hold != player:
            return False
        self.hold = None
        return True

class Game:
    def __init__(self):
        self.players: List[Player] = []
        self.lock = Lock()
        self.isPlaying = False
        self._makeBoxes()

    def _makeBoxes(self):
        self.boxes: List[List[Box]] = []
        for _ in range(BOARD_SIZE):
            row: List[Box] = []
            for _ in range(BOARD_SIZE):
                row.append(Box())
            self.boxes.append(row)

    # Add a new player to the game
    # Return None if the player cannot be added
    def addPlayer(self, client: socket):
        player = Player(client, len(self.players))
        self.players.append(player)
        return player

    # Remove player from the game
    def removePlayer(self, player: Player):
        self.players.remove(player)

    # Handle a command from a player
    def handleAction(self, player: Player, action: str, row: int, col: int):
        with self.lock:
            # Reject the action if there are not enough players
            if len(self.players) < MIN_PLAYERS or len(self.players) >= MAX_PLAYERS:
                return
            self.isPlaying = True
            box = self.boxes[row][col]
            if action == Action.HOLD and box.canBeHeld(player):
                self.broadcast(f"{Action.HOLD} {row} {col} {player.id}")
            elif action == Action.CLAIM and box.canBeClaim(player):
                self.broadcast(f"{Action.CLAIM} {row} {col} {player.id}")
            elif action == Action.RELEASE and box.canBeReleased(player):
                self.broadcast(f"{Action.RELEASE} {row} {col} {player.id}")

    # Broadcast a command to all players
    def broadcast(self, message: str):
        for player in self.players:
            player.socket.send(message.encode("ascii"))
