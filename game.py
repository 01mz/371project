from socket import socket
from threading import Lock
from typing import List, Optional, Tuple

from constant import BOARD_SIZE, Action

Player = Tuple[socket, int]


class Box:
    def __init__(self):
        self.claim: Optional[Player] = None
        self.hold: Optional[Player] = None
        self.lock = Lock()

    def canBeClaim(self, player: Player):
        with self.lock:
            if self.hold != player: return False
            self.claim = player
            self.hold = None
            return True

    def canBeHeld(self, player: Player):
        with self.lock:
            if self.hold is not None: return False
            self.hold = player
            return True

    def release(self):
        with self.lock:
            self.hold = None


class Game:
    def __init__(self):
        self.new = True
        self.players = []
        self.boxes: List[List[Box]] = []
        for _ in range(BOARD_SIZE):
            row: List[Box] = []
            for _ in range(BOARD_SIZE):
                row.append(Box())
            self.boxes.append(row)

    def addPlayer(self, client: socket) -> Player:
        self.new = False
        player = (client, len(self.players))
        self.players.append(player)
        return player

    def removePlayer(self, player: Player):
        self.players.remove(player)

    def isPlaying(self):
        return self.new or len(self.players) > 0

    def handleAction(self, player: Player, action: str, row: int, col: int):
        box = self.boxes[row][col]
        if action == Action.CHOOSE:
            if box.canBeHeld(player):
                self.broadcast(f"{Action.CHOOSE} {row} {col} {player[1]}")
        elif action == Action.CLAIM:
            if box.canBeClaim(player):
                self.broadcast(f"{Action.CLAIM} {row} {col} {player[1]}")
        elif action == Action.RELEASE:
            box.release()
            self.broadcast(f"{Action.RELEASE} {row} {col} {player[1]}")

    def broadcast(self, message: str):
        for player in self.players:
            client, _ = player
            client.send(message.encode("ascii"))
