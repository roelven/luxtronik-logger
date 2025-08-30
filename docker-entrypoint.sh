#!/bin/bash
set -e

# With --network=host, the container shares the host's network namespace
# The route should already be configured on the host:
# ip route add 192.168.20.0/24 via 10.0.0.1 dev ens18

# Note: Network connectivity issues may occur in virtualized environments
# The route is configured on the host and should be accessible
# Connection will be attempted by the application directly

# Common fixes if connection fails:
# sudo sysctl -w net.ipv4.conf.all.rp_filter=0
# sudo sysctl -w net.ipv4.conf.ens18.rp_filter=0
# sudo sysctl -w net.ipv4.ip_forward=1

# Print routing table for debugging
echo "Current routing table:"
ip route show

# Start the application with passed arguments
echo "Starting Luxtronik Logger..."
exec "$@"
