# CLAUDE.md

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

### CSV Generation
- Daily: YYYY-MM-DD_daily.csv (last 24h)
- Weekly: YYYY-MM-DD_weekly.csv (last 7d)
- Skip if no data (log warning)

## Future Roadmap
- 365-day retention (SQLite)
- Selective exports (sensor filtering)
- Web UI (FastAPI + React/Dash)
- Multi-format exports (JSON, DTA)

## Resources
- python-luxtronik: https://github.com/Bouni/python-luxtronik.git