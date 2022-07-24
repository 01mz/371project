from socket import *
# from datetime import *

serverName = 'localhost'
serverPort = 65432

clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName, serverPort))

# start = datetime.now()
clientSocket.send("hello".encode('utf-8'))
print(clientSocket.recv(1024).decode('utf-8'))
# end = datetime.now()

# print(f"RTT = {end-start}")

clientSocket.close()







