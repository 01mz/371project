from socket import *

serverHost = '' # set emtpy string so the server accepts connections on all available IPv4 interfaces
serverPort = 65432  # port to listen on (client should have the same port)

serverSocket = socket(AF_INET, SOCK_STREAM) # SOCK_STREAM is the socket type for TCP
serverSocket.bind((serverHost, serverPort))
serverSocket.listen(5) # allows a simultaneous connection for 5 players
print('The server is ready to receive')

while True:

    conn, addr = serverSocket.accept()

    dataFromClient = conn.recv(1024).decode('utf-8') # received message

    print(dataFromClient)

    # if no data comes in close the connection (for testing purpose)
    if not dataFromClient:
        break

    conn.send("back at you".encode('utf-8'))

    conn.close()

serverSocket.close()