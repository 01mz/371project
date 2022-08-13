from socket import socket
from threading import Lock
from typing import List, Optional, Tuple

from constant import BOARD_SIZE, Action
from collections import Counter

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
    def canBeReleased(self, player: Player):
        if self.hold != player is None:
            return False
        self.hold = None
        return True


class Game:
    def __init__(self):
        self.new = True
        self.players = []
        self.boxes: List[List[Box]] = []
        self.lock = Lock()
        self.gameFinished = False
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
            if self.gameFinished is True: return
            if action == Action.CHOOSE and box.canBeHeld(player):
                self.broadcast(f"{Action.CHOOSE} {row} {col} {player[1]}")
            elif action == Action.CLAIM and box.canBeClaim(player):
                winner_index = self.checkWinners()
                self.broadcast(f"{Action.CLAIM} {row} {col} {player[1]} {winner_index}")
                if winner_index != -1: 
                    self.gameFinished = True
            elif action == Action.RELEASE and box.canBeReleased(player):
                self.broadcast(f"{Action.RELEASE} {row} {col} {player[1]}")

    # Broadcast a command to all players
    def broadcast(self, message: str):      
        for player in self.players:
            client, player_index = player
            action, *_ = message.split(" ")
            new_message = message + f" {player_index}"
            if action == Action.CLAIM:
                client.send(new_message.encode("ascii"))
            else:
                client.send(message.encode("ascii"))

    def checkWinners(self):
        claimed_list = []         #Get claimed boxes array
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if(self.boxes[row][col].claim is not None):
                    claimed_list.append(self.boxes[row][col].claim[1]) #Get the 2nd value in the player tuple 

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