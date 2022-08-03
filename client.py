import socket
import faulthandler

import view as gui
from constant import SERVER_HOST, SERVER_PORT

if __name__ == "__main__":
    faulthandler.enable()
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((SERVER_HOST, SERVER_PORT))
    gui.run(client)
