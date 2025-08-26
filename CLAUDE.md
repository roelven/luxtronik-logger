# CLAUDE.md

## Data Collection Improvement Plan

### Problem Analysis
The current data collection from the live heat pump test generates CSV files that are too small, indicating potential issues with:
1. **Data Access Method**: Using `__dict__` on luxtronik objects may not properly access all available sensor data
2. **Data Filtering**: Important sensor data might be excluded by current filtering logic
3. **Debug Information**: Insufficient logging to diagnose what data is actually being collected

### Immediate Action Plan

#### 1. Enhanced Debugging and Diagnostics
Create comprehensive debug scripts to:
- Inspect all available sensor data
- Validate data completeness before CSV generation

#### 2. Improved Data Collection Methods
Update `client.py` to use proper luxtronik API methods instead of `__dict__`:
- Use `connection.calculations.get_all()` for structured access
- Use `connection.parameters.get_all()` for parameter values
- Use `connection.visibilities.get_all()` for visibility data

#### 3. Comprehensive Data Validation
Implement validation scripts to:
- Check data completeness and quality
- Verify critical sensor presence

#### 4. Production-Ready Improvements
- Implement data validation checks before storage
- Add fallback mechanisms for missing sensor data
- Enhance error reporting with specific sensor availability information

### Implementation Steps

#### Step 1: Enhanced Client Debugging
Modify `client.py` to include:
- Detailed logging of all available sensor names and values
- Connection diagnostics and heat pump capability reporting
- Data completeness validation before storage

#### Step 2: Proper Data Access
Replace current `__dict__` approach with proper luxtronik API methods for structured data access

#### Step 3: Data Quality Assurance
Add validation to ensure:
- Minimum number of sensors are available
- Critical temperature sensors are present
- Data values are within reasonable ranges
- Timestamps are consistent and sequential

#### Step 4: Comprehensive Testing
Create diagnostic test scripts for:
- Detailed data inspection
- Data quality validation

### Expected Sensor Data
A properly functioning heat pump should provide:
- **Temperature Sensors**: TVL, TRL, TA, TWA, TWE, TSK, TSS, etc.
- **System Parameters**: Heating modes, pump status, error codes
- **Performance Metrics**: Flow rates, pressures, energy consumption
- **Status Information**: Operation modes, timers, setpoints

### Troubleshooting Guide

#### If CSV files are empty or small:
2. **Enable Debug Logging**: Run with `--log-level DEBUG` to see detailed data
3. **Test Data Collection**: Use debug scripts to see what data is available
4. **Validate Sensor Access**: Ensure proper luxtronik API methods are used

### Production Deployment Checklist
- [ ] Data collection produces >50 sensor readings per poll
- [ ] CSV files contain multiple rows with complete data
- [ ] All critical temperature sensors are present
- [ ] Data validation passes before storage
- [ ] Connection diagnostics show healthy communication

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

The goal is to build a resilient, fully-automated data-logging service for a Novelan heat pump using python-luxtronik. Key features:
- Continuous polling (30s default interval)
- Crash-safe time-series storage (buffer + cache)
- Daily/weekly CSV roll-ups
- Dockerized deployment
- TDD-first development (≥90% coverage)

## Common Commands

- Run tests: `pytest --timeout=10`
- Run specific test: `pytest tests/test_<module>.py --timeout=10`
- Build Docker: `docker build -t lux-logger .`
- Run container: `docker run --env-file .env -v ./logs:/app/logs lux-logger`

## Core Architecture

### Modules
- `config.py`: YAML/ENV config with validation
- `client.py`: Heat pump interface (python-luxtronik)
- `storage.py`: Buffer + cache management
- `csvgen.py`: CSV roll-up generation
- `service.py`: Main scheduler

### Data Flow
1. Poll heat pump (60s timeout, 3 retries)
2. Store in buffer → flush to cache
3. Generate CSVs (daily @ 07:00, weekly)
4. Auto-delete CSVs >30d old

### Key Dependencies
- python-luxtronik
- APScheduler/sched
- SQLite/JSON

## Resilience Specifications

### Network
- 60s timeout with exponential back-off (3 retries)
- Detailed timeout logging (attempts + final failure)

### Crash Recovery
- Auto-restart service loop (5s delay)
- Preserve CSV generation state
- One retry on CSV failures

### File Management
- Auto-delete CSVs >30d (configurable)
- Log deletions (count + freed space)
- Disk space monitoring (<90% utilization)

### Testing
- 10s timeout enforcement in CI
- Detailed timeout reports

### Job Execution
- Ensure polling jobs do not skip due to max_instances limit
- Add timeout handling for long-running jobs

## Implementation Details

### Configuration
- Fields: HOST, PORT, INTERVAL_SEC, CSV_TIME, CACHE_PATH, OUTPUT_DIRS
- Validation: types/ranges, exit on invalid

### Client
- get_all_sensors() → Dict[str, float]
- Timeout logging with full context

### Storage
- API: add(timestamp, data) & query(start, end)
- SIGTERM/SIGINT handling (flush before exit)

### Service
- APScheduler/sched for intervals
- Graceful shutdown handlers
- Uncaught exception logging
- On-demand report generation support

### CSV Generation
- Daily: YYYY-MM-DD_daily.csv (last 24h)
- Weekly: YYYY-MM-DD_weekly.csv (last 7d)
- Skip if no data (log warning)

## Future Roadmap
- 365-day retention (SQLite)
- Selective exports (sensor filtering)
- Web UI (FastAPI + React/Dash)
- Multi-format exports (JSON, DTA)

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

## Resources
- python-luxtronik: https://github.com/Bouni/python-luxtronik.git
