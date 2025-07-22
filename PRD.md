# Luxtronik Logger

The goal of this project is to build a resilient, fully-automated data-logging service for a Novelan heat pump on your LAN, using the python-luxtronik library. It will:

•	Continuously poll the heat pump every configurable interval (30 s by default) and capture all sensor readings exposed by python-luxtronik.
•	Persist each timestamped reading in a crash-safe, time-series store (in-memory buffer + on-disk cache) so no data is lost if the service or container restarts.
•	Roll-up the collected data into daily and weekly CSV snapshots, generated automatically at a configurable time (07:00 AM by default).
•	Offer a configurable setup via YAML or environment variables: pump IP/port, polling interval, roll-up schedule, cache/output paths.
•	Run as a Docker container for easy deployment and lifecycle management (logging, healthcheck, graceful shutdown).
•	Be built TDD-first: every new feature begins with a failing pytest, then minimal code to pass it, ensuring ≥ 90% coverage and clear guard-rails.

## Implementation Plan

### MVP

**1.	Project scaffold**

•	Repo layout (see below)
•	Python 3.9+, pytest, python-luxtronik, SQLite or JSON cache, YAML/ENV config

```
lux-logger/
├── src/
│   ├── config.py
│   ├── client.py
│   ├── storage.py
│   ├── csvgen.py
│   └── service.py
├── tests/
│   ├── test_config.py
│   ├── test_client.py
│   ├── test_storage.py
│   ├── test_csvgen.py
│   └── test_service.py
├── Dockerfile
├── requirements.txt
└── README.md
```

**Network Resilience**
- 60s timeout for network calls with exponential back-off (retry up to 3 times)
- Detailed logging of timeout events with full context (including retry attempts and final failure)

**Crash Recovery**
- Auto-restart service loop on uncaught exceptions (with 5s delay between restarts)
- Preserve in-progress CSV generation state for crash recovery
- Retry failed CSV generation once before logging error

**File Retention**
- Auto-delete CSVs >30d old to manage disk space (configurable retention period)
- Log deletion events with file count and freed space

**Testing**
- 10s timeout requirement for CI tests (fail if exceeded)
- Include timeout details in test failure reports

**2.	Configuration**
•	Test: config.py loads defaults + overrides (YAML + ENV).
•	Fields: HOST, PORT, INTERVAL_SEC, CSV_TIME, CACHE_PATH, OUTPUT_DIRS.
•	Guard-rail: validate types/ranges; exit on invalid.

**3.	Client integration**
•	Test: mock python-luxtronik responses.
•	Code: client.py → get_all_sensors() → Dict[str, float] for all available sensors.
•	60s timeout for network calls with exponential back-off. Log timeout events with full context.

**4.	Storage layer**
•	Test: append + retrieve time-series points; simulate restart recovery.
•	Code: storage.py
•	In-memory buffer + flush to cache every N samples
•	On startup: reload cache to buffer
•	API: add(timestamp, data) & query(start, end)
•	Guard-rail: handle SIGTERM/SIGINT → flush before exit.

**5.	Continuous service**
•	Test: simulate scheduler ticks; verify client→storage.
•	Code: service.py
•	Use APScheduler or sched to run every INTERVAL_SEC
•	Signal handlers for graceful shutdown
•	Guard-rail: log uncaught exceptions, auto-restart loop. Preserve in-progress CSV generation state for crash recovery.

**6.	CSV roll-ups**
•	Test: inject sample data; assert CSV file content & naming.
•	Code: csvgen.py
•	Daily at CSV_TIME:
•	Last 24 h → YYYY-MM-DD_daily.csv
•	Last 7 d  → YYYY-MM-DD_weekly.csv
•	Guard-rail: skip if no data; log warning. Auto-delete CSVs >30d old to manage disk space.

**7.	Dockerization**
•	Test: docker build + docker run → service starts, polls, writes files.
•	Code: Dockerfile
•	Base Python image
•	Copy code + install deps
•	Entrypoint → service.py
•	ENV defaults for config
•	Optional: Docker HEALTHCHECK that hits a simple HTTP health endpoint in service.py.


### V2 Roadmap

**1.	365-day retention**
•	Migrate storage → SQLite (time-partitioned tables)
•	Tests: bulk inserts + old-data cleanup.

**2.	Selective exports**
•	Config: EXPORT_SENSORS: List[str] + date windows
•	Tests: include/exclude logic in CSV/JSON/DTA exports.

**3.	Web UI**
•	Backend: FastAPI
•	Frontend: React or Dash
•	Endpoints + unit tests (pytest + HTTPX)
•	Features: datepicker, sensor toggles, interactive graphs.

**4.	Multi-format export**
•	CSV, JSON (native), DTA (pandas.to_stata())
•	Tests: validate file schemas & sample exports.


### TDD & CI Guard-rails
•	Test first: write a failing pytest → minimal code to pass.
•	Coverage: target ≥ 90% on core modules.
•	CI pipeline: GitHub Actions with lint, pytest (10s timeout per test), Docker build.
•	One feature per PR: small, reviewable, self-documenting.


## Resources

https://github.com/Bouni/python-luxtronik.git

