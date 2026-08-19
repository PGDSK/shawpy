import socket
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

        print(f"Received: {message}")

        if message == "quit":
            client.send(b"goodbye!")
            print(f"client {address} disconnecting...")
            break

        if message == "STATUS":

            # RAM
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

            # GPU
            gpu = subprocess.check_output(
                [
                    "nvidia-smi",
                    "--query-gpu=name,temperature.gpu,utilization.gpu,memory.used,memory.total",
                    "--format=csv,noheader,nounits"
                ]
            ).decode().strip()

            gpu_parts = [x.strip() for x in gpu.split(",")]

            gpu_name = gpu_parts[0]
            gpu_temp = gpu_parts[1]
            gpu_usage = gpu_parts[2]
            vram_used = gpu_parts[3]
            vram_total = gpu_parts[4]

            # Uptime
            uptime = subprocess.check_output(
                ["uptime", "-p"]
            ).decode().strip()

            response = (
                f"\n"
                f"╔══════════════════════════════════════╗\n"
                f"║          SHAWPY // NOBARA            ║\n"
                f"╠══════════════════════════════════════╣\n"
                f"║  HOST       {hostname:<25}║\n"
                f"║                                      ║\n"
                f"║  CPU        Ryzen 5 7600             ║\n"
                f"║  RAM        {used_gb:.1f} / {total_gb:.1f} GiB"
                f" ({percentage:.0f}%)       ║\n"
                f"║  GPU        {gpu_name:<25}║\n"
                f"║  GPU LOAD   {gpu_usage:>3}%   TEMP {gpu_temp:>3}°C            ║\n"
                f"║  VRAM       {vram_used} / {vram_total} MiB              ║\n"
                f"║  UPTIME     {uptime:<25}║\n"
                f"║                                      ║\n"
                f"║  ◉ NETWORK     TAILSCALE / TCP       ║\n"
                f"║  ◉ SSH         ONLINE                 ║\n"
                f"║  ◉ SERVER      ONLINE                 ║\n"
                f"╚══════════════════════════════════════╝\n"
            )

        else:
            response = "Unknown command\n"

        client.send(response.encode())

    client.close()