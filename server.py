import socket
from concurrent.futures import ThreadPoolExecutor

from constant import SERVER_HOST, SERVER_PORT
from game import Game, Player

game = Game()

# Listen and handle the incoming commands from the player
def handlePlayer(player: Player):
    while True:
        client, _ = player
        try:
            # Handle game command from the client
            command = client.recv(1024).decode("ascii")
            action, row, col = command.split(" ")
            game.handleAction(player, action, int(row), int(col))
        except:
            # Removing player from the game
            game.removePlayer(player)
            client.close()
            print(f"Player {player[1]} is disconnected")
            break


def main():
    # Set up the server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((SERVER_HOST, SERVER_PORT))
    server.listen(4)

    with ThreadPoolExecutor() as executor:
        while game.isPlaying():
            # Connect the client
            client, _ = server.accept()

            # Add new player to the game
            player = game.addPlayer(client)
            print(f"Player {player[1]} is connected")

            # Create a thread to handle incoming commands for each player
            # and add it to the thread pool
            executor.submit(handlePlayer, player)
        server.close()


if __name__ == "__main__":
    main()
