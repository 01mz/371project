import socket

SERVER_HOST = socket.gethostbyname(socket.gethostname())
SERVER_PORT = 65432
BOARD_SIZE = 8


class Action:
    CHOOSE = "choose"
    RELEASE = "release"
    HOLD = "hold"
    CLAIM = "claim"


COLORS = ["red", "green", "blue", "yellow"]


def getColor(id: int):
    if id >= 0 and id < len(COLORS):
        return COLORS[id]
    return "white"
