# src/logger_daemon.py

import json
import logging
import os
import schedule
import sys
import os
import sys
import time
from datetime import datetime
from dotenv import load_dotenv
from luxtronik import Luxtronik

load_dotenv()

# --- Configuration ---
HOST = os.getenv("HOST")
PORT = int(os.getenv("PORT", 8889))
LOG_INTERVAL_SECONDS = int(os.getenv("LOG_INTERVAL_SECONDS", 30))
CSV_GENERATION_TIME = os.getenv("CSV_GENERATION_TIME", "07:00")
DATA_DIR = "data"
LOG_FILE = os.path.join(DATA_DIR, "daemon.log")
CACHE_FILE = os.path.join(DATA_DIR, "datalog.jsonl")
HEADER_FILE = "config/header.json"
MAPPING_FILE = "config/final-mapping.json"

# --- Data Transformation ---

def transform_value(value, data_type):
    """Transforms a value based on its data type."""
    if data_type == "celsius":
        return float(value) / 10.0
    elif data_type == "bivalence_level":
        return {
            0: "no request",
            1: "one compressor allowed to run",
            2: "two compressors allowed to run",
            3: "reheat",
            4: "reheat & 1 compressor",
            5: "reheat & 2 compressors"
        }.get(value, "unknown")
    elif data_type == "operation_mode":
        return {
            0: "heating",
            1: "hot water",
            2: "swimming pool/solar",
            3: "evu",
            4: "defrost",
            5: "cooling"
        }.get(value, "unknown")
    return value

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
# Quieten the verbose luxtronik library logger
logging.getLogger("luxtronik").setLevel(logging.WARNING)

# In-memory cache, loaded on startup
data_cache = []

def load_cache():
    """Loads existing data from the cache file into memory."""
    if os.path.exists(CACHE_FILE):
        logging.info(f"Found existing cache file. Loading data from {CACHE_FILE}")
        with open(CACHE_FILE, 'r') as f:
            for line in f:
                try:
                    data_cache.append(json.loads(line))
                except json.JSONDecodeError:
                    logging.warning(f"Could not decode line in cache file: {line}")
        logging.info(f"Successfully loaded {len(data_cache)} records from cache.")

def collect_data():
    """Connects to the heat pump, fetches data, and appends it to the cache file."""
    try:
        logging.info(f"Collecting data from {HOST}:{PORT}...")
        pump = Luxtronik(HOST, PORT)
        pump.read()

        # Combine all data into a single record
        record = {
            "timestamp": datetime.now().isoformat(),
            "calculations": pump.calculations.calculations,
            "parameters": pump.parameters.parameters
        }

        # Append to the in-memory cache and the on-disk cache
        data_cache.append(record)
        with open(CACHE_FILE, 'a') as f:
            f.write(json.dumps(record, default=str) + '\n')
        
        logging.info(f"Successfully collected data. Cache size: {len(data_cache)}")

    except Exception as e:
        logging.error(f"Error during data collection: {e}")

def generate_csv():
    """Generates the daily CSV file from the cached data."""
    if not data_cache:
        logging.info("No data in cache, skipping CSV generation.")
        return

    logging.info(f"Generating CSV file for the last 24 hours...")

    try:
        # Load headers and mapping
        with open(HEADER_FILE, 'r') as f:
            headers = json.load(f)
        with open(MAPPING_FILE, 'r') as f:
            mapping = json.load(f)

        # Generate filename for today
        today_str = datetime.now().strftime('%Y-%m-%d')
        csv_filename = os.path.join(DATA_DIR, f"{today_str}.csv")

        # Create a list of rows
        rows = []
        for record in data_cache:
            row_data = {}
            dt = datetime.fromisoformat(record['timestamp'])
            row_data['Datum'] = dt.strftime('%d.%m.%Y')
            row_data['Uhrzeit'] = dt.strftime('%H:%M:%S')

            for header in headers:
                if header in ['Datum', 'Uhrzeit']:
                    continue
                
                mapping_info = mapping.get(header)
                if mapping_info:
                    key = mapping_info.get("key")
                    data_type = mapping_info.get("type")

                    # Find the value in either calculations or parameters
                    value = record['calculations'].get(str(key))
                    if value is None:
                        value = record['parameters'].get(str(key))
                    
                    if value is not None:
                        row_data[header] = transform_value(value, data_type)
                    else:
                        row_data[header] = ''
                else:
                    row_data[header] = '' # Leave blank if no mapping exists
            
            rows.append(row_data)

        # Write to CSV
        import csv
        with open(csv_filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=headers, delimiter=';')
            writer.writeheader()
            writer.writerows(rows)

        logging.info(f"Successfully wrote {len(rows)} records to {csv_filename}")

        # Clear caches
        data_cache.clear()
        if os.path.exists(CACHE_FILE):
            os.remove(CACHE_FILE)
        logging.info("Cleared in-memory and on-disk caches.")

    except Exception as e:
        logging.error(f"Error during CSV generation: {e}")


def main():
    """Main application loop."""
    logging.info("Starting Luxtronik Logger Daemon...")

    if not HOST:
        logging.error("HOST environment variable not set. Please configure it in your .env file.")
        sys.exit(1)
    
    # Ensure data directory exists
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    # Load any existing data from cache
    load_cache()

    # --- Schedule Tasks ---
    schedule.every(LOG_INTERVAL_SECONDS).seconds.do(collect_data)
    schedule.every().day.at(CSV_GENERATION_TIME).do(generate_csv)

    logging.info("Scheduler started. Waiting for next job...")

    # --- Main Loop ---
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'generate':
        load_cache()
        generate_csv()
    else:
        main()
