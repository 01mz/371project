import socket
import sys
import faulthandler
import sys

import view as gui
from constant import CONNECTION, SERVER_HOST, SERVER_PORT

if __name__ == "__main__":
    if len(sys.argv) == 2:
        SERVER_HOST = sys.argv[1]
    faulthandler.enable()
    if len(sys.argv) == 2:
        SERVER_HOST = sys.argv[1]

    # Create a socket object and connect to the server
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((SERVER_HOST, SERVER_PORT))

    command, *rest = client.recv(1024).decode("ascii").split(" ")
    if command == CONNECTION.REJECT:
        print("Server is full")
        client.close()
        sys.exit(0)
    else: gui.run(client)
