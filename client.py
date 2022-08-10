import socket
import sys
import faulthandler
import sys
from game import Player

import view as gui
from constant import Connection, SERVER_HOST, SERVER_PORT

def run(host, port):
    # Create a socket object and connect to the server
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))

    # Recieve the first welcome messages
    command, *rest = client.recv(1024).decode("ascii").split(" ")
    if command == Connection.ACCEPT:
        gui.run(Player(client, int(rest[0])))
    else:
        if command == Connection.REJECT:
            print("Sorry. Unable to join the game right now")
        socket.close()
    

if __name__ == "__main__":
    faulthandler.enable()
    if len(sys.argv) == 2:
        SERVER_HOST = sys.argv[1]
    run(SERVER_HOST, SERVER_PORT)
