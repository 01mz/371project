from socket import socket
from threading import Lock
from typing import List, Optional, Tuple

from constant import BOARD_SIZE, Action

Player = Tuple[socket, int]


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
    def release(self):
        self.hold = None


class Game:
    def __init__(self):
        self.new = True
        self.players = []
        self.boxes: List[List[Box]] = []
        self.lock = Lock()
        for _ in range(BOARD_SIZE):
            row: List[Box] = []
            for _ in range(BOARD_SIZE):
                row.append(Box())
            self.boxes.append(row)

    # Add a new player to the game
    def addPlayer(self, client: socket) -> Player:
        self.new = False
        player = (client, len(self.players))
        self.players.append(player)
        return player

    # Remove player from the game
    def removePlayer(self, player: Player):
        self.players.remove(player)

    # Check if the game is over
    def isPlaying(self):
        return self.new or len(self.players) > 0

    # Handle a command from a player
    def handleAction(self, player: Player, action: str, row: int, col: int):
        with self.lock:
            box = self.boxes[row][col]
            if action == Action.CHOOSE and box.canBeHeld(player):
                self.broadcast(f"{Action.CHOOSE} {row} {col} {player[1]}")
            elif action == Action.CLAIM and box.canBeClaim(player):
                self.broadcast(f"{Action.CLAIM} {row} {col} {player[1]}")
            elif action == Action.RELEASE:
                box.release()
                self.broadcast(f"{Action.RELEASE} {row} {col} {player[1]}")

    # Broadcast a command to all players
    def broadcast(self, message: str):
        for player in self.players:
            client, _ = player
            client.send(message.encode("ascii"))
