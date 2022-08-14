SERVER_HOST = 'localhost'
SERVER_PORT = 65432
BOARD_SIZE = 8
TIME_TO_HOLD = 3000

# Game actions used by both server and client
class Action:
    RELEASE = "release"
    HOLD = "hold"
    CLAIM = "claim"
    WIN = "win"

# Connection operations sent by the server
class Connection:
    ACCEPT = "accept"
    REJECT = "reject"


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
