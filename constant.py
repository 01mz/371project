import socket

SERVER_HOST = socket.gethostbyname(socket.gethostname())
SERVER_PORT = 65432
BOARD_SIZE = 8

# Game actions used by both server and client
class Action:
    RELEASE = "release"
    HOLD = "hold"
    CLAIM = "claim"

# Connection operations sent by the server
class Connection:
    ACCEPT = "accept"
    REJECT = "reject"
    WIN = "win"

COLORS = ["red", "green", "blue", "yellow"]
LABELS = ["RED", "GREEN", "BLUE", "YELLOW"]


MIN_PLAYERS = 2
MAX_PLAYERS = 4

def getColor(id: int):
    if id >= 0 and id < len(COLORS):
        return COLORS[id]
    return "white"

def getLabel(id: int):
    return LABELS[id]
