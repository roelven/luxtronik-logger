#!/usr/bin/env python3
"""
Test script to validate CSV generation with a live heat pump.

This script:
1. Connects to the live heat pump at 192.168.20.180:8889
2. Collects sensor data for a specified duration
3. Generates on-demand CSV reports
4. Validates the generated CSV files
"""

import os
import sys
import time
import csv
import json
import tempfile
import shutil
from datetime import datetime, timedelta
import sqlite3

# Add src to path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from client import HeatPumpClient
from storage import DataStorage
from csvgen import CSVGenerator
from service import LuxLoggerService
from config import Config

def collect_heatpump_data(duration=61):
    """Collect data from the live heat pump for specified duration"""
    print(f"Collecting data from heat pump for {duration} seconds...")

    # Create temporary directory for test data
    data_dir = tempfile.mkdtemp(prefix="lux_logger_live_test_")
    cache_path = os.path.join(data_dir, "cache.db")

    # Create directories for CSV output
    os.makedirs(os.path.join(data_dir, "daily"), exist_ok=True)
    os.makedirs(os.path.join(data_dir, "weekly"), exist_ok=True)

    try:
        # Create config for live heat pump
        config = Config()
        config.host = "192.168.20.180"
        config.port = 8889
        config.cache_path = cache_path
        config.output_dirs = {
            "daily": os.path.join(data_dir, "daily"),
            "weekly": os.path.join(data_dir, "weekly")
        }
        config.csv_retention_days = 30
        config.interval_sec = 30  # Default interval

        # Create storage
        storage = DataStorage(cache_path)

        # Create client and connect to heat pump
        client = HeatPumpClient(config.host, config.port)

        # Collect data points
        start_time = time.time()
        data_points_collected = 0

        while (time.time() - start_time) < duration:
            try:
                print(f"Collecting data point {data_points_collected + 1}...")
                sensor_data = client.get_all_sensors()
                timestamp = datetime.now()
                storage.add(timestamp, sensor_data)
                storage.flush()  # Immediately flush to cache
                data_points_collected += 1
                print(f"  ✓ Collected {len(sensor_data)} sensor readings")

                # Wait for next collection (or until duration expires)
                if (time.time() - start_time + config.interval_sec) < duration:
                    print(f"  Waiting {config.interval_sec} seconds...")
                    time.sleep(config.interval_sec)
                else:
                    break

            except Exception as e:
                print(f"  ✗ Error collecting data: {e}")
                # Continue with next attempt
                if (time.time() - start_time + 5) < duration:
                    print("  Waiting 5 seconds before retry...")
                    time.sleep(5)
                else:
                    break

        print(f"Collected {data_points_collected} data points in {time.time() - start_time:.1f} seconds")
        return data_dir, cache_path, data_points_collected

    except Exception as e:
        print(f"Error during data collection: {e}")
        shutil.rmtree(data_dir)
        return None, None, 0

def generate_reports(data_dir, cache_path):
    """Generate CSV reports from collected data"""
    print("Generating CSV reports...")

    try:
        # Create config with test paths
        config = Config()
        config.host = "192.168.20.180"  # Dummy for service
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

        return True
    except Exception as e:
        print(f"Error generating reports: {e}")
        return False

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

                # Check for reasonable data (not all empty values)
                if row_count <= 3:  # Check first few rows
                    non_empty_count = sum(1 for cell in row if cell.strip())
                    if non_empty_count == 0:
                        print(f"  ⚠️  WARNING: Row {row_count} has no data values")

            print(f"  Total rows: {row_count}")

            if row_count == 0:
                print(f"  ⚠️  WARNING: No data rows in {file_path}")
            else:
                print(f"  ✅ SUCCESS: Validated {file_path}")

            return True

    except Exception as e:
        print(f"  ❌ ERROR: Failed to validate {file_path}: {str(e)}")
        return False

def check_cache_data(cache_path):
    """Check the SQLite cache for data"""
    if not os.path.exists(cache_path):
        print("No cache database found")
        return False

    try:
        conn = sqlite3.connect(cache_path)
        cursor = conn.cursor()

        # Get count of data points
        cursor.execute("SELECT COUNT(*) FROM sensor_data")
        count = cursor.fetchone()[0]
        print(f"Cache contains {count} data points")

        if count > 0:
            # Get sample data
            cursor.execute("SELECT timestamp, data_json FROM sensor_data ORDER BY timestamp DESC LIMIT 3")
            rows = cursor.fetchall()

            print("Recent data samples:")
            for i, (timestamp, data_json) in enumerate(rows):
                data = json.loads(data_json)
                dt = datetime.fromtimestamp(timestamp)
                print(f"  Sample {i+1}: {dt} - {len(data)} sensor readings")
                # Print first few key-value pairs
                sample_data = dict(list(data.items())[:3])
                print(f"    Sample data: {sample_data}")

        conn.close()
        return count > 0

    except Exception as e:
        print(f"Failed to check cache data: {str(e)}")
        return False

def test_live_heatpump():
    """Test CSV generation with live heat pump"""
    print("Starting live heat pump CSV generation test...")
    print("Connecting to heat pump at 192.168.20.180:8889")

    data_dir = None
    try:
        # Collect data from live heat pump
        data_dir, cache_path, data_points = collect_heatpump_data(duration=61)

        if data_dir is None:
            print("❌ Failed to collect data from heat pump")
            return False

        if data_points == 0:
            print("❌ No data points collected from heat pump")
            return False

        print(f"✅ Successfully collected {data_points} data points")

        # Check cache data
        print("\nChecking cache data...")
        has_cache_data = check_cache_data(cache_path)

        # Generate reports
        print("\nGenerating reports...")
        if not generate_reports(data_dir, cache_path):
            print("❌ Failed to generate reports")
            return False

        print("✅ Reports generated successfully")

        # Validate CSV files
        print("\nValidating CSV files...")
        success = validate_csv_files(data_dir)

        if success:
            print("\n✅ Live heat pump CSV generation test PASSED")
            print("✅ CSV files were generated successfully with live heat pump data")

            # Show what files were created
            daily_dir = os.path.join(data_dir, "daily")
            weekly_dir = os.path.join(data_dir, "weekly")

            daily_files = [f for f in os.listdir(daily_dir) if f.endswith("_daily.csv")]
            weekly_files = [f for f in os.listdir(weekly_dir) if f.endswith("_weekly.csv")]

            if daily_files:
                print(f"Daily CSV files created: {daily_files}")
            if weekly_files:
                print(f"Weekly CSV files created: {weekly_files}")

        else:
            print("\n❌ Live heat pump CSV generation test FAILED")

        return success

    except Exception as e:
        print(f"Test failed with exception: {str(e)}")
        return False

    finally:
        # Cleanup temporary directory
        if data_dir and os.path.exists(data_dir):
            try:
                shutil.rmtree(data_dir)
                print(f"Cleaned up temporary directory: {data_dir}")
            except Exception as e:
                print(f"Failed to cleanup temporary directory: {str(e)}")

if __name__ == "__main__":
    success = test_live_heatpump()
    sys.exit(0 if success else 1)
