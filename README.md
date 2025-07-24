# Luxtronik Logger

A resilient data-logging service for Novelan heat pumps using python-luxtronik.

## Docker Usage

This service requires special networking configuration to access the heat pump on a different subnet.

### Prerequisites

1. **Add route on the host**: The heat pump is typically on a different subnet than your Docker host. Add a route:

```bash
# On your Docker host
sudo ip route add 192.168.20.0/24 via 10.0.0.1 dev ens18
```

2. **Make the route persistent** (optional):

```bash
# For Ubuntu/Debian
echo "post-up ip route add 192.168.20.0/24 via 10.0.0.1 dev ens18" | sudo tee -a /etc/network/interfaces.d/heatpump-route
```

### Running the Container

```bash
# Build the image
docker build -t lux-logger .

# Run with host networking (essential for cross-subnet access)
docker run --network=host --env-file .env -v ./logs:/app/logs lux-logger
```

## Configuration

- Configure settings in `.env` or via environment variables
- See CLAUDE.md for full configuration options

## Development

- See CLAUDE.md for development setup and testing instructions