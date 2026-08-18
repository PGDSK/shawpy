import socket
import os
import subprocess

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

hostname = socket.gethostname()

server.bind(("0.0.0.0", 8000))
server.listen()

print("Server listening on port 8000")

while True:
    client, address = server.accept()

    print(f"Connection from {address}")

    while True:
        data = client.recv(1024)

        if not data:
            break

        message = data.decode().strip()

        print(f"Received: {message} from {address}")

        if message == "quit":
            client.send(b"goodbye!")
            break

        if message == "STATUS":
            memory = subprocess.check_output(
                ["free", "-h"]
            ).decode()

            response = (
                f"=== SHAWPY // NOBARA ===\n"
                f"Host: {hostname}\n"
                f"RAM:\n{memory}"
            )
        else:
            response = "Unknown command\n"

        client.send(response.encode())

    client.close()
