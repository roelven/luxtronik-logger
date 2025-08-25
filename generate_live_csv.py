#!/usr/bin/env python3
"""
Script to generate and save CSV files from live heat pump data.

This script:
1. Connects to the live heat pump at 192.168.20.180:8889
2. Collects sensor data
3. Generates CSV reports and saves them to a specified directory
"""

import os
import sys
import time
import csv
from datetime import datetime
import argparse

# Add src to path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from client import HeatPumpClient
from storage import DataStorage
from csvgen import CSVGenerator
from service import LuxLoggerService
from config import Config

def collect_and_generate_csv(output_dir="output", duration=61):
    """Collect data from live heat pump and generate CSV files"""
    print(f"Generating CSV files from live heat pump data...")
    print(f"Output directory: {output_dir}")
    print(f"Collection duration: {duration} seconds")

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Create data subdirectories
    daily_dir = os.path.join(output_dir, "daily")
    weekly_dir = os.path.join(output_dir, "weekly")
    os.makedirs(daily_dir, exist_ok=True)
    os.makedirs(weekly_dir, exist_ok=True)

    # Create cache file path
    cache_path = os.path.join(output_dir, "cache.db")

    try:
        # Create config for live heat pump
        config = Config()
        config.host = "192.168.20.180"
        config.port = 8889
        config.cache_path = cache_path
        config.output_dirs = {
            "daily": daily_dir,
            "weekly": weekly_dir
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

        print("Collecting data from heat pump...")
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

        if data_points_collected == 0:
            print("❌ No data points collected from heat pump")
            return False

        # Generate reports using the service
        print("\nGenerating CSV reports...")
        service = LuxLoggerService(config)
        service.generate_reports_on_demand()

        # List generated files
        print(f"\nGenerated files in {output_dir}:")
        print("Daily CSV files:")
        for f in os.listdir(daily_dir):
            if f.endswith(".csv"):
                file_path = os.path.join(daily_dir, f)
                size = os.path.getsize(file_path)
                print(f"  {f} ({size} bytes)")

        print("Weekly CSV files:")
        for f in os.listdir(weekly_dir):
            if f.endswith(".csv"):
                file_path = os.path.join(weekly_dir, f)
                size = os.path.getsize(file_path)
                print(f"  {f} ({size} bytes)")

        # Show sample content
        print("\nSample content from daily CSV:")
        daily_files = [f for f in os.listdir(daily_dir) if f.endswith(".csv")]
        if daily_files:
            daily_file = os.path.join(daily_dir, daily_files[0])
            with open(daily_file, 'r') as f:
                lines = f.readlines()
                for i, line in enumerate(lines[:5]):  # Show first 5 lines
                    print(f"  {line.rstrip()}")
                    if i >= 4:
                        print("  ...")
                        break

        print("\n✅ CSV files generated successfully!")
        print(f"📁 Files saved to: {os.path.abspath(output_dir)}")
        return True

    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Generate CSV files from live heat pump data')
    parser.add_argument(
        '--output', '-o',
        default='output',
        help='Output directory for CSV files (default: output)'
    )
    parser.add_argument(
        '--duration', '-d',
        type=int,
        default=61,
        help='Data collection duration in seconds (default: 61)'
    )

    args = parser.parse_args()

    success = collect_and_generate_csv(args.output, args.duration)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
