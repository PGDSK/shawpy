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
                ["free", "-b"]
            ).decode()

            memory_line = memory.splitlines()[1]
            parts = memory_line.split()

            total = int(parts[1])
            used = int(parts[2])

            used_gb = used / (1024 ** 3)
            total_gb = total / (1024 ** 3)
            percentage = (used / total) * 100

            response = (
                f"=== SHAWPY // NOBARA ===\n"
                f"Host: {hostname}\n"
                f"RAM: {used_gb:.1f} / {total_gb:.1f} GiB ({percentage:.0f}%)\n"
            )

        else:
            response = "Unknown command\n"

        client.send(response.encode())

    client.close()