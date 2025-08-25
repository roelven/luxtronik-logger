#!/usr/bin/env python3
"""
Simple test script to validate CSV generation with pre-populated data.

This script:
1. Creates test data in the SQLite cache
2. Runs the on-demand report generation
3. Validates the generated CSV files
"""

import os
import sys
import tempfile
import shutil
import sqlite3
import json
import csv
from datetime import datetime, timedelta

# Add src to path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from csvgen import CSVGenerator
from service import LuxLoggerService
from config import Config

def create_test_data(data_dir):
    """Create test data in SQLite cache"""
    cache_path = os.path.join(data_dir, "cache.db")

    # Create directories
    os.makedirs(os.path.join(data_dir, "daily"), exist_ok=True)
    os.makedirs(os.path.join(data_dir, "weekly"), exist_ok=True)

    # Create test database with sample data
    conn = sqlite3.connect(cache_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sensor_data (
            timestamp REAL PRIMARY KEY,
            data_json TEXT NOT NULL
        )
    """)

    # Insert sample data points for the last 8 days
    base_time = datetime.now() - timedelta(days=8)
    for i in range(200):  # 200 data points
        timestamp = (base_time + timedelta(minutes=i*30)).timestamp()
        data = {
            "calculations.Temperatur_TVL": 35.0 + (i % 10) * 0.5,  # Flow temperature
            "calculations.Temperatur_TRL": 32.0 + (i % 8) * 0.3,   # Return temperature
            "calculations.Speicheristtemp": 45.0 + (i % 12) * 0.4, # Storage temperature
            "calculations.Temperatur_TA": 15.0 + (i % 20) * 0.2,   # Outside temperature
            "parameters.Heizungstemp_Max": 60.0,                   # Max heating temperature
            "parameters.Heizungstemp_Min": 20.0,                   # Min heating temperature
        }
        conn.execute(
            "INSERT OR REPLACE INTO sensor_data VALUES (?, ?)",
            (timestamp, json.dumps(data))
        )

    # Also insert some recent data for daily CSV (last 24 hours)
    recent_base_time = datetime.now() - timedelta(hours=25)  # Slightly more than 24 hours to ensure we have data
    for i in range(50):  # 50 recent data points
        timestamp = (recent_base_time + timedelta(minutes=i*30)).timestamp()
        data = {
            "calculations.Temperatur_TVL": 36.0 + (i % 8) * 0.4,   # Flow temperature
            "calculations.Temperatur_TRL": 33.0 + (i % 6) * 0.3,   # Return temperature
            "calculations.Speicheristtemp": 46.0 + (i % 10) * 0.3, # Storage temperature
            "calculations.Temperatur_TA": 16.0 + (i % 15) * 0.2,   # Outside temperature
            "parameters.Heizungstemp_Max": 60.0,                   # Max heating temperature
            "parameters.Heizungstemp_Min": 20.0,                   # Min heating temperature
        }
        conn.execute(
            "INSERT OR REPLACE INTO sensor_data VALUES (?, ?)",
            (timestamp, json.dumps(data))
        )

    conn.commit()
    conn.close()

    print(f"Created test data with 200 data points in {cache_path}")
    return cache_path

def validate_csv_files(data_dir):
    """Validate the generated CSV files"""
    print("Validating CSV files...")

    daily_dir = os.path.join(data_dir, "daily")
    weekly_dir = os.path.join(data_dir, "weekly")

    # Check for CSV files
    daily_files = [f for f in os.listdir(daily_dir) if f.endswith("_daily.csv")]
    weekly_files = [f for f in os.listdir(weekly_dir) if f.endswith("_weekly.csv")]

    print(f"Found {len(daily_files)} daily CSV files")
    print(f"Found {len(weekly_files)} weekly CSV files")

    if not daily_files and not weekly_files:
        print("❌ No CSV files found!")
        return False

    # Validate daily CSV files
    for csv_file in daily_files:
        file_path = os.path.join(daily_dir, csv_file)
        print(f"Validating {csv_file}...")
        if not validate_csv_file(file_path):
            return False

    # Validate weekly CSV files
    for csv_file in weekly_files:
        file_path = os.path.join(weekly_dir, csv_file)
        print(f"Validating {csv_file}...")
        if not validate_csv_file(file_path):
            return False

    return True

def validate_csv_file(file_path):
    """Validate a single CSV file"""
    try:
        with open(file_path, 'r') as f:
            reader = csv.reader(f)

            # Read header
            header = next(reader, None)
            if header is None:
                print(f"  ❌ ERROR: Empty CSV file {file_path}")
                return False

            print(f"  Header: {header[:5]}{'...' if len(header) > 5 else ''} ({len(header)} columns)")

            # Read data rows
            row_count = 0
            for row in reader:
                row_count += 1
                if len(row) != len(header):
                    print(f"  ❌ ERROR: Row {row_count} has {len(row)} columns, expected {len(header)}")
                    return False

                # Validate that we have some data
                if row_count == 1:
                    print(f"  Sample row: {row[:5]}{'...' if len(row) > 5 else ''}")

            print(f"  Total rows: {row_count}")

            if row_count == 0:
                print(f"  ⚠️  WARNING: No data rows in {file_path}")
            else:
                print(f"  ✅ SUCCESS: Validated {file_path}")

            return True

    except Exception as e:
        print(f"  ❌ ERROR: Failed to validate {file_path}: {str(e)}")
        return False

def test_csv_generation():
    """Test CSV generation with pre-populated data"""
    print("Starting CSV generation test with pre-populated data...")

    # Create temporary directory for test data
    data_dir = tempfile.mkdtemp(prefix="lux_logger_csv_test_")
    print(f"Using data directory: {data_dir}")

    try:
        # Create test data
        cache_path = create_test_data(data_dir)

        # Create config with test paths
        config = Config()
        config.host = "localhost"  # Dummy host for testing
        config.port = 8889
        config.cache_path = cache_path
        config.output_dirs = {
            "daily": os.path.join(data_dir, "daily"),
            "weekly": os.path.join(data_dir, "weekly")
        }
        config.csv_retention_days = 30

        # Create service and generate reports on demand
        service = LuxLoggerService(config)
        service.generate_reports_on_demand()

        # Validate CSV files
        success = validate_csv_files(data_dir)

        if success:
            print("\n✅ CSV generation test PASSED")
            print("✅ CSV files were generated successfully with test data")
        else:
            print("\n❌ CSV generation test FAILED")

        return success

    except Exception as e:
        print(f"Test failed with exception: {str(e)}")
        return False

    finally:
        # Cleanup temporary directory
        try:
            shutil.rmtree(data_dir)
            print(f"Cleaned up temporary directory: {data_dir}")
        except Exception as e:
            print(f"Failed to cleanup temporary directory: {str(e)}")

if __name__ == "__main__":
    success = test_csv_generation()
    sys.exit(0 if success else 1)
