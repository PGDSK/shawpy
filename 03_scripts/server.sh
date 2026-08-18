#!/bin/bash

echo "=== SHAWPY SERVER MODE ==="

# Set low-power mode
powerprofilesctl set power-saver

# Prevent the PC from sleeping
systemd-inhibit --what=sleep --why="Shawpy server mode" sleep infinity &
INHIBIT_PID=$!

echo "Power profile: power-saver"
echo "Sleep inhibited"
echo "SSH: $(systemctl is-active sshd)"
echo "Tailscale: $(systemctl is-active tailscaled)"
echo
echo "Server mode active."
echo "Press Ctrl+C to exit."

# Remove sleep inhibition when the script exits
trap 'kill "$INHIBIT_PID" 2>/dev/null' EXIT

# Keep the script running
wait
