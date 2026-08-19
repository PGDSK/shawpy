import socket
import os
import time

SERVER = "100.124.10.41"
PORT = 8000

while True:
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((SERVER, PORT))

        client.send(b"STATUS\n")

        data = client.recv(4096).decode()

        client.close()

        os.system("clear")

        print(data)

        print("Refreshing every 2 seconds...")

        time.sleep(2)

    except Exception as e:
        os.system("clear")

        print("╔══════════════════════════════════════╗")
        print("║          SHAWPY // NOBARA            ║")
        print("╠══════════════════════════════════════╣")
        print("║                                      ║")
        print("║  ◉ NETWORK     OFFLINE               ║")
        print("║  ◉ SERVER      UNREACHABLE           ║")
        print("║                                      ║")
        print(f"║  Error: {str(e)[:25]:<25} ║")
        print("║                                      ║")
        print("╚══════════════════════════════════════╝")

        time.sleep(2)
