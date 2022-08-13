from socket import socket
from threading import Lock
from typing import List, Optional

from constant import BOARD_SIZE, MAX_PLAYERS, MIN_PLAYERS, Action
from collections import Counter


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
        self.isGameFinished = False
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
            if len(self.players) < MIN_PLAYERS or len(self.players) >= MAX_PLAYERS or self.isGameFinished is True:
                return
            self.isPlaying = True
            box = self.boxes[row][col]
            if action == Action.HOLD and box.canBeHeld(player):
                self.broadcast(f"{Action.HOLD} {row} {col} {player.id}")
            elif action == Action.CLAIM and box.canBeClaim(player):
                winner_index = self.checkWinners()
                self.broadcast(f"{Action.CLAIM} {row} {col} {player.id} {winner_index}")
                if winner_index != -1: 
                    self.isGameFinished = True
            elif action == Action.RELEASE and box.canBeReleased(player):
                self.broadcast(f"{Action.RELEASE} {row} {col} {player.id}")

    # Broadcast a command to all players
    def broadcast(self, message: str):      
        for player in self.players:
            action, *_ = message.split(" ")
            new_message = message + f" {player.id}"
            if action == Action.CLAIM:
                player.socket.send(new_message.encode("ascii"))
            else:
                player.socket.send(message.encode("ascii"))

    def checkWinners(self):
        claimed_list = []         #Get claimed boxes array
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if(self.boxes[row][col].claim is not None):
                    claimed_list.append(self.boxes[row][col].claim.id)

        #Get the most repetitive number of claimed boxes
        c = Counter(claimed_list)
        highest_score = c.most_common(1) #return [(player index, # of boxes claim)]
        temp = int((BOARD_SIZE*BOARD_SIZE)/len(self.players)) 

        if(len(claimed_list) >= temp+1): #If a player claimed more than 1/n boxes, he is the winner
            winner_index_ = highest_score[0][0]
            winner_score_ = highest_score[0][1]
            if(winner_score_ == temp+1):
                print("Winner is player number", winner_index_," with highest score: ", winner_score_)
                return winner_index_
            return -1
        elif(len(claimed_list) == BOARD_SIZE*BOARD_SIZE): #If every boxes are filled, we have a winner
            winner_index = highest_score[0][0]
            winner_score = highest_score[0][1]
            print("Winner is player number", winner_index," with highest score: ", winner_score)
            return winner_index
        else:
            return -1
