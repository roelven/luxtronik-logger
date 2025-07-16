# Plan to Implement Luxtronik Data Logger (Python Daemon)

## Goal
Create a robust, long-running Python application that continuously collects data from a Luxtronik heat pump and, once a day, generates a CSV log file covering the last 24 hours of activity.

## Architecture: Resilient Daemon with Disk Cache
We will build a persistent Python application designed to run continuously. To prevent data loss in case of a crash or restart, the application will use a file-based cache.

**Workflow:**
1.  **Startup & Recovery:** On launch, the application checks for an existing cache file (e.g., `data/datalog.jsonl`). If found, it loads the contents into memory to resume the previous session's state.
2.  **Collect & Persist:** The application will query the heat pump at a frequent, configurable interval (e.g., every 30 seconds). Each data snapshot will be immediately appended as a new line to the `datalog.jsonl` cache file.
3.  **Generate CSV:** Once every 24 hours (e.g., at 7:00 AM), the application will read the entire cache file, process the data, and write it to the final daily CSV log (e.g., `data/2025-07-15.csv`).
4.  **Reset:** After the CSV is successfully generated, the `datalog.jsonl` cache file is deleted to start a fresh 24-hour cycle.

## Key Parameters (Configurable)
- **Logging Interval:** How often to query the heat pump. **Default: 30 seconds.**
- **File Generation Time:** The time of day to write the 24-hour log file. **Default: "07:00"**.
- **Heat Pump IP/Port:** `192.168.20.180:8889`.
- **Cache File Path:** `data/datalog.jsonl`.

## Steps

1.  **Create the Definitive Header List:**
    *   I will parse the header row from `data/320210-717_250713_1340.dta.csv` to define the exact columns and order for the output file.

2.  **Build the Data-to-CSV Mapping:**
    *   Using the live data dump we previously captured and the CSV header list, I will create a comprehensive mapping in `config/header-mapping.json`.
    *   The mapping's `key` will be the CSV header (e.g., `"Istwert_Aussent"`) and the `value` will be the corresponding `luxtronik` data key (e.g., `"ID_WEB_Temperatur_TA"`).

3.  **Implement the Python Daemon (`src/logger_daemon.py`):**
    *   The script will manage the main application loop. It will use Python's `schedule` and `time` libraries to orchestrate tasks.
    *   **Startup Logic:** Implement the cache recovery mechanism.
    *   **Data Collection Function:**
        - Connects to the heat pump.
        - Fetches data and the current timestamp.
        - Appends the data as a JSON line to the cache file.
    *   **File Generation Function:**
        - Reads all data from the cache file.
        - Uses the mapping to format each record into a CSV row.
        - Writes the header and all rows to the daily CSV file.
        - Deletes the cache file on success.

4.  **Cleanup and Documentation:**
    *   The temporary `discover_data.py` script will be removed.
    *   The `README.md` will be updated with instructions on how to run `logger_daemon.py` as a background process and how to manage it.

## Verification
I will run the daemon, then simulate a crash (`kill` command). After restarting the daemon, I will verify that it has recovered the data and can successfully generate the complete CSV at the scheduled time.

Once you approve this plan, I will begin by creating the header list and the data mapping.
