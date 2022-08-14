import socket
from concurrent.futures import ThreadPoolExecutor

from constant import MAX_PLAYERS, SERVER_HOST, SERVER_PORT, Connection
from game import Game, Player

# Listen and handle the incoming commands from the player
def handlePlayer(game: Game, player: Player):
    while True:
        try:
            # Handle game command from the client
            commands = player.socket.recv(1024).decode("ascii").strip('|').split('|')
            for command in commands:
                action, row, col = command.split(" ")
                game.handleAction(player, action, int(row), int(col))
        except:
            # Removing player from the game
            game.removePlayer(player)
            player.socket.close()
            print(f"Player {player.id} is disconnected")
            break

def main():
    # Create a new game
    game = Game()
    # Set up the server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((SERVER_HOST, SERVER_PORT))
    server.listen(4)
    print(f"Server is running on port {SERVER_PORT}")

    with ThreadPoolExecutor() as executor:
        while True:
            # Connect the client
            client, _ = server.accept()

            # If all players have disconnected and then a new player joins, reset the game for the new player
            if len(game.players) == 0 and game.isPlaying:
                print("creating a new game")
                game = Game()

            # Reject player if the game is full of players or the game is playing
            if len(game.players) >= MAX_PLAYERS or game.isPlaying:
                client.send(Connection.REJECT.encode("ascii"))
                client.close()
                continue

            # Notify the player which ID they are playing
            else:
                # Add new player to the game
                player = game.addPlayer(client)
                client.send(f"{Connection.ACCEPT} {player.id}".encode("ascii"))
                
                # Create a thread to handle incoming commands for each player
                # and add it to the thread pool
                executor.submit(handlePlayer, game, player)
                print(f"Player {player.id} is connected")


if __name__ == "__main__":
    main()
