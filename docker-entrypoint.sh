#!/bin/bash
set -e

# With --network=host, the container shares the host's network namespace
# The route should already be configured on the host:
# ip route add 192.168.20.0/24 via 10.0.0.1 dev ens18

# Verify the route exists
if ! ip route show | grep -q "192.168.20.0/24"; then
    echo "ERROR: Route to heat pump network not found!"
    echo "Please run on the host:"
    echo "sudo ip route add 192.168.20.0/24 via 10.0.0.1 dev ens18"
    exit 1
fi

# Verify we can reach the heat pump
if ! nc -z 192.168.20.180 8889; then
    echo "WARNING: Cannot connect to heat pump at 192.168.20.180:8889"
    echo "Please verify the heat pump is powered on and accessible"
fi

# Print routing table for debugging
echo "Current routing table:"
ip route show

# Start the application
echo "Starting Luxtronik Logger..."
exec python main.py