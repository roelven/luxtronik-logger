# Luxtronik Logger

A resilient, fully-automated data-logging service for Novelan heat pumps using `python-luxtronik`. Continuously polls the heat pump, stores time-series data safely, and generates daily/weekly CSV roll-ups.

## Features
- **Continuous Polling**: Default 30-second interval for real-time data collection.
- **Crash-Safe Storage**: Buffers and caches data to prevent loss.
- **CSV Roll-Ups**: Generates daily and weekly CSV files for analysis.
- **Dockerized Deployment**: Easy containerization for seamless operation.
- **TDD-First**: High test coverage (≥90%) ensures reliability.

## CSV Generation
- **Daily**: `YYYY-MM-DD_daily.csv` (last 24 hours of data).
- **Weekly**: `YYYY-MM-DD_weekly.csv` (last 7 days of data).
- **Auto-Cleanup**: Deletes CSVs older than 30 days (configurable).

## Docker Usage
1. **Build**:
   ```bash
   docker build -t lux-logger .
   ```
2. **Run**:
   ```bash
   docker run --env-file .env -v ./logs:/app/logs lux-logger
   ```
   - Mount a volume for persistent logs (`./logs:/app/logs`).
   - Use `--env-file .env` to pass configuration (refer to `.env.sample` for required variables).

   **Important Networking Note**: If your heat pump is on a different subnet (e.g., 192.168.20.0/24) than your Docker host (e.g., 10.0.0.0/24):
   ```bash
   # Add route on the host before running
   sudo ip route add 192.168.20.0/24 via 10.0.0.1 dev ens18
   
   # For virtualized environments (LXD/LXC), you may also need:
   sudo sysctl -w net.ipv4.conf.all.rp_filter=0
   sudo sysctl -w net.ipv4.conf.ens18.rp_filter=0
   sudo sysctl -w net.ipv4.ip_forward=1
   
   # Run with host networking mode
   docker run --network=host --env-file .env -v ./logs:/app/logs lux-logger
   ```

## Configuration
Copy `.env.sample` to `.env` and configure:
- `HOST`: Heat pump IP address.
- `PORT`: Heat pump port (default: `8889`).
- `INTERVAL_SEC`: Polling interval (default: `30`).
- `CSV_TIME`: Daily CSV generation time (default: `07:00`).
- `CACHE_PATH`: SQLite cache file path.
- `OUTPUT_DIRS`: Paths for daily/weekly CSVs.

## Development
- **Tests**:
  ```bash
  pytest --timeout=10
  ```
- **Modules**:
  - `config.py`: YAML/ENV config validation.
  - `client.py`: Heat pump interface.
  - `storage.py`: Buffer + cache management.
  - `csvgen.py`: CSV generation.
  - `service.py`: Main scheduler.

## Resilience
- **Network**: 60s timeout with exponential backoff (3 retries).
- **Crash Recovery**: Auto-restarts service loop (5s delay).
- **Disk Space**: Monitors utilization (<90%) and logs deletions.

## Future Roadmap
- 365-day retention (SQLite).
- Selective exports (sensor filtering).
- Web UI (FastAPI + React/Dash).
- Multi-format exports (JSON, DTA).