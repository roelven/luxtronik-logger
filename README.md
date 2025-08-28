# Luxtronik Logger

A resilient, fully-automated data-logging service for Novelan heat pumps using `python-luxtronik`. Continuously polls the heat pump, stores time-series data safely, and generates daily/weekly CSV roll-ups with comprehensive sensor data.

## Overview

This application is designed for users who want to monitor and analyze their Novelan/Luxtronik heat pump performance over time. It provides detailed operational data collection that enables:

- Performance monitoring and optimization
- Energy consumption analysis
- Fault detection and preventive maintenance
- Historical data analysis for system efficiency

The system collects over 1,800 sensor readings every 30 seconds, providing granular insights into heat pump operation that are not available through the standard web interface.

## Features

**Note**: When running tests, ensure the `PYTHONPATH` environment variable is set to the root directory of the project. This can be done by running `export PYTHONPATH=.` before executing the tests.
- **Continuous Polling**: Default 30-second interval for real-time data collection.
- **Crash-Safe Storage**: Buffers and caches data to prevent loss.
- **Comprehensive Data Collection**: Collects 1860+ sensor readings per poll
- **CSV Roll-Ups**: Generates daily and weekly CSV files for analysis with detailed heat pump data.
- **Dockerized Deployment**: Easy containerization for seamless operation.
- **TDD-First**: High test coverage (≥90%) ensures reliability.
- **On-Demand Reports**: Generate daily/weekly CSV reports at any time.

## CSV Generation
- **Daily**: `YYYY-MM-DD_daily.csv` (last 24 hours of data).
- **Weekly**: `YYYY-MM-DD_weekly.csv` (last 7 days of data).
- **Auto-Cleanup**: Deletes CSVs older than 30 days (configurable).
- **Readable Headers**: Set `READABLE_HEADERS=true` in `.env` to use human-readable sensor names in CSV headers (e.g., "Flow Temperature" instead of "calculations.ID_WEB_Temperatur_TVL").

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

## Configuration
Copy `.env.sample` to `.env` and configure:
- `HOST`: Heat pump IP address.
- `PORT`: Heat pump port (default: `8889`).
- `INTERVAL_SEC`: Polling interval (default: `30`).
- `CSV_TIME`: Daily CSV generation time (default: `07:00`).
- `CACHE_PATH`: SQLite cache file path.
- `OUTPUT_DIRS`: Paths for daily/weekly CSVs.
- `READABLE_HEADERS`: Set to `true` to use human-readable sensor names in CSV headers (default: `false`).

## Development
- **Tests**:
  ```bash
  export PYTHONPATH=.
  pytest --timeout=10
  ```

- **Script Execution**:
  When running scripts directly (e.g., `python main.py`), ensure the `PYTHONPATH` environment variable is set to the root directory:
  ```bash
  export PYTHONPATH=.
  python main.py --mode generate-reports
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
python tests/test_csv_generation.py
```

This test:
1. Creates realistic sensor data in SQLite cache
2. Generates daily and weekly CSV files
3. Validates the structure and content of generated CSV files

### Live Heat Pump Test
To test CSV generation with your actual heat pump:

```bash
# Run the live heat pump test (connects to 192.168.20.180:8889)
python tests/test_live_heatpump.py
```

This test:
1. Connects to your live heat pump at 192.168.20.180:8889
2. Collects real sensor data for 61 seconds (2+ data points)
3. Generates daily and weekly CSV reports
4. Validates the structure and content of generated CSV files

### Generate and Save CSV Files
To generate CSV files from your live heat pump and save them permanently:

```bash
# Generate CSV files and save to ./output directory
python generate_live_csv.py --output ./output

# Generate CSV files with custom duration (e.g., 120 seconds)
python generate_live_csv.py --output ./output --duration 120
```

This script:
1. Connects to your live heat pump at 192.168.20.180:8889
2. Collects real sensor data for the specified duration
3. Generates daily and weekly CSV reports
4. Saves the CSV files to the specified output directory
5. Shows a sample of the generated CSV content

### Docker-Based Test (Advanced)
To test the full workflow with a mock heat pump:

```bash
# Run the comprehensive test with mock heat pump
python tests/comprehensive_test.py
```

This test will:
1. Start a mock heat pump server
2. Build and run the Docker container
3. Wait for data collection (70 seconds for multiple data points)
4. Execute on-demand report generation
5. Validate the generated CSV files

## Data Collection Details

The system collects comprehensive data from your heat pump with over 1,800 sensor readings per collection cycle:

- **Temperature Sensors**: Flow, return, ambient, water, source, and solar temperatures
- **System Parameters**: Operation modes, pump status, and error codes
- **Visibility Settings**: Status information and configuration settings
- **Performance Metrics**: Flow rates, pressures, and energy consumption values
- **Status Information**: Operation modes, timers, setpoints, and error histories

Each data point contains over 1,800 sensor readings collected every 30 seconds by default, providing detailed operational insights.

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

## Troubleshooting

If you encounter issues with data collection or CSV generation:

1. **Check Connection**: Ensure your heat pump is accessible at the configured IP and port
2. **Enable Debug Logging**: Run `python debug_heatpump.py` for comprehensive diagnostics
3. **Test Data Collection**: Use `python tests/test_data_improvements.py` for complete validation

### Common Issues
- **Small CSV Files**: Verify that the system is collecting the full dataset (should be 1800+ sensor readings)
- **Empty Data**: Check that data validation is passing (minimum 100 sensors required)

## Future Roadmap
- 365-day retention (SQLite).
- Selective exports (sensor filtering).
- Web UI (FastAPI + React/Dash).
- Multi-format exports (JSON, DTA).
