# Luxtronik Logger

A resilient, fully-automated data-logging service for Novelan heat pumps using `python-luxtronik`. Continuously polls the heat pump, stores time-series data safely, and generates daily/weekly CSV roll-ups.

## Features

**Note**: When running tests, ensure the `PYTHONPATH` environment variable is set to the root directory of the project. This can be done by running `export PYTHONPATH=.` before executing the tests.
- **Continuous Polling**: Default 30-second interval for real-time data collection.
- **Crash-Safe Storage**: Buffers and caches data to prevent loss.
- **CSV Roll-Ups**: Generates daily and weekly CSV files for analysis.
- **Dockerized Deployment**: Easy containerization for seamless operation.
- **TDD-First**: High test coverage (≥90%) ensures reliability.
- **On-Demand Reports**: Generate daily/weekly CSV reports at any time.

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
   docker run --env-file .env -v ./data:/app/data lux-logger
   ```
   - Mount a volume for persistent logs (`./data:/app/data`).
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
  - `main.py`: Command-line interface with on-demand report generation support.

## Resilience
- **Network**: 60s timeout with exponential backoff (3 retries).
- **Crash Recovery**: Auto-restarts service loop (5s delay).
- **Disk Space**: Monitors utilization (<90%) and logs deletions.

## Debugging and Testing
- **Timeout for Debugging**: Add a timeout parameter to the service to run for a specified duration (e.g., 63 seconds) and exit. This allows for quick debugging sessions where the output can be observed in the terminal. The existing 10-second timeouts for unit tests remain unchanged.

## Testing CSV Data Generation

### Simple CSV Generation Test
To test CSV generation with pre-populated data:

```bash
# Run the CSV generation test with test data
python test_csv_generation.py
```

This test:
1. Creates realistic sensor data in SQLite cache
2. Generates daily and weekly CSV files
3. Validates the structure and content of generated CSV files

### Live Heat Pump Test
To test CSV generation with your actual heat pump:

```bash
# Run the live heat pump test (connects to 192.168.20.180:8889)
python test_live_heatpump.py
```

This test:
1. Connects to your live heat pump at 192.168.20.180:8889
2. Collects real sensor data for 61 seconds (2+ data points)
3. Generates daily and weekly CSV reports
4. Validates the structure and content of generated CSV files

### Docker-Based Test (Advanced)
To test the full workflow with a mock heat pump:

```bash
# Run the comprehensive test with mock heat pump
python comprehensive_test.py
```

This test will:
1. Start a mock heat pump server
2. Build and run the Docker container
3. Wait for data collection (70 seconds for multiple data points)
4. Execute on-demand report generation
5. Validate the generated CSV files

## On-Demand Report Generation
To generate reports on-demand (outside of the scheduled daily generation), use the command-line interface:

```bash
# Generate daily and weekly reports on-demand
python main.py --mode generate-reports
```

This will create the same daily and weekly CSV files as the scheduled job, using the last 24 hours and 7 days of data respectively. The command will:
- Query data from the SQLite cache
- Generate daily CSV with the last 24 hours of data
- Generate weekly CSV with the last 7 days of data
- Clean up old CSV files according to retention settings
- Exit after completion

This is useful for generating reports at specific times or for debugging purposes.

## Future Roadmap
- 365-day retention (SQLite).
- Selective exports (sensor filtering).
- Web UI (FastAPI + React/Dash).
- Multi-format exports (JSON, DTA).
