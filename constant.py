SERVER_HOST = 'localhost'
SERVER_PORT = 65432
BOARD_SIZE = 8

# Game actions
class Action:
    RELEASE = "release"
    HOLD = "hold"
    CLAIM = "claim"

# Connection operations
class CONNECTION:
    ACCEPT = "accept"
    REJECT = "reject"
    WIN = "win"

COLORS = ["red", "green", "blue", "yellow"]

MIN_PLAYERS = 2
MAX_PLAYERS = 4

def getColor(id: int):
    if id >= 0 and id < len(COLORS):
        return COLORS[id]
    return "white"
