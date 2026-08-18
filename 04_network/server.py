import socket

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind(("0.0.0.0", 8000))
server.listen()

print("Server listening on port 8000")

while True:
    client, address = server.accept()

    print(f"Connection from {address}")

    client.send(b"Hello nigga!\n")

    data = client.recv(1024)

    print(f"Recieved: {data.decode()}")

    client.send(b"got your message\nprocessing...")

    client.close()