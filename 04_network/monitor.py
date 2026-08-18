import socket

hostname = socket.gethostname()

print("=== SHAWPY NETWORK MONITOR ===")
print (f"Hostname: {hostname}")

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.connect(("8.8.8.8", 80))
local_ip = sock.getsockname()[0]
sock.close()

print(f"Local IP: {local_ip}")