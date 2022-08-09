import socket
from concurrent.futures import ThreadPoolExecutor

from constant import CONNECTION, SERVER_HOST, SERVER_PORT
from game import Game, Player

game = Game()

# Listen and handle the incoming commands from the player
def handlePlayer(player: Player):
    while True:
        try:
            # Handle game command from the client
            command = player.socket.recv(1024).decode("ascii")
            action, row, col = command.split(" ")
            game.handleAction(player, action, int(row), int(col))
        except:
            # Removing player from the game
            game.removePlayer(player)
            player.socket.close()
            print(f"Player {player.id} is disconnected")
            break

def main():
    # Set up the server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((SERVER_HOST, SERVER_PORT))
    server.listen(4)
    print(f"Server is running on port {SERVER_PORT}")

    with ThreadPoolExecutor() as executor:
        while game.isPlaying():
            # Connect the client
            client, _ = server.accept()

            # Add new player to the game
            player = game.addPlayer(client)

            # Notify the player which ID they are playing
            # or reject the player if the game is full
            if player is not None:
                client.send(f"{CONNECTION.ACCEPT} {player.id}".encode("ascii"))
                
                # Create a thread to handle incoming commands for each player
                # and add it to the thread pool
                executor.submit(handlePlayer, player)
                print(f"Player {player.id} is connected")
            else:
                client.send(f"{CONNECTION.REJECT}".encode("ascii"))
                client.close()
                print(f"New player is rejected")
        server.close()


if __name__ == "__main__":
    main()
