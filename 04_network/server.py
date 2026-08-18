import socket
import os

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

hostname = socket.gethostname() 

server.bind(("0.0.0.0", 8000))
server.listen()

print("Server listening on port 8000")

while True:
    client, address = server.accept()

    print(f"Connection from {address}")
###Eveything above this line is the inital setup 

    while True:
        data = client.recv(1024)

        message = data.decode().strip()

        print(f"Received: {message} from {address}")

        if message == "quit":
            client.send(b"goodbye!")
            break

        if message == "STATUS":
            response = f"Server is running!\nfrom host: {hostname}"
        else:
            response = "Unknown command\n"

        client.send(response.encode())

client.close()