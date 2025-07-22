# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Commands

- Run tests: `pytest --timeout=10`
- Run a specific test: `pytest tests/test_<module>.py --timeout=10`
- Build Docker image: `docker build -t lux-logger .`
- Run Docker container: `docker run --env-file .env -v ./logs:/app/logs lux-logger`

## High-Level Architecture

- **Core Modules**:
  - `config.py`: Loads YAML/ENV config with validation
  - `client.py`: Interfaces with python-luxtronik for sensor data
  - `storage.py`: Manages in-memory buffer + on-disk cache
  - `csvgen.py`: Generates daily/weekly CSV roll-ups
  - `service.py`: Main scheduler and service loop

- **Data Flow**:
  - Poll heat pump (60s timeout + auto-retry) → Store in buffer → Flush to cache → Generate CSVs (with crash recovery)
  - Automatic deletion of CSVs >30d old

- **Key Dependencies**:
  - `python-luxtronik` for heat pump communication
  - `APScheduler` or `sched` for polling intervals
  - SQLite/JSON for data persistence

## Resilience Rules
- **Crash Recovery**: Auto-restart service loop on uncaught exceptions
- **Network Timeouts**: 60s timeout for heat pump communication with exponential backoff
- **Disk Management**: Auto-delete CSVs >30d old, ensure disk space never exceeds 90% utilization