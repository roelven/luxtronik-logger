#!/bin/bash
set -e

# With --network=host, the container shares the host's network namespace
# The route should already be configured on the host:
# ip route add 192.168.20.0/24 via 10.0.0.1 dev ens18

# Verify the route exists for the heat pump
if ! ip route show | grep -q "192.168.20"; then
    echo "WARNING: Route to heat pump network not found, but continuing anyway"
    echo "Suggest running on the host:"
    echo "sudo ip route add 192.168.20.0/24 via 10.0.0.1 dev ens18"
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