#!/bin/bash
set -e

# Add route to heat pump network inside the container
echo "Adding route to heat pump network..."
ip route add 192.168.20.0/24 via 10.0.0.1 dev eth0 2>/dev/null || echo "Route already exists or failed to add"

# Print routing table for debugging
echo "Current routing table:"
ip route show

# Start the application
echo "Starting Luxtronik Logger..."
exec python main.py