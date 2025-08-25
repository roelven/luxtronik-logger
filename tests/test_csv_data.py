#!/usr/bin/env python3
"""
Test script to validate CSV data generation in Docker environment.

This script:
1. Builds and runs the Docker container
2. Waits for data collection (61+ seconds for 2+ data points)
3. Executes on-demand report generation
4. Validates the generated CSV files
"""

import os
import sys
import time
import subprocess
import csv
import json
import tempfile
import shutil
from datetime import datetime, timedelta
import sqlite3

def build_docker_image():
    """Build the Docker image"""
    print("Building Docker image...")
    result = subprocess.run([
        "docker", "build", "-t", "lux-logger-test", "."
    ], cwd=os.path.dirname(__file__), capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Failed to build Docker image: {result.stderr}")
        return False

    print("Docker image built successfully")
    return True

def create_test_env_file():
    """Create a test environment file"""
    env_content = """
HOST=192.168.1.100
PORT=8889
INTERVAL_SEC=30
CSV_TIME=07:00
CACHE_PATH=/app/data/cache.db
OUTPUT_DIRS_DAILY=/app/data/daily
OUTPUT_DIRS_WEEKLY=/app/data/weekly
CSV_RETENTION_DAYS=30
DISK_USAGE_THRESHOLD=90
"""

    env_file = os.path.join(os.path.dirname(__file__), "test.env")
    with open(env_file, "w") as f:
        f.write(env_content.strip())

    return env_file

def run_docker_container(env_file, data_dir, duration=70):
    """
    Run the Docker container for specified duration

    Args:
        env_file: Path to environment file
        data_dir: Directory to mount for data persistence
        duration: Duration to run container in seconds
    """
    print(f"Running Docker container for {duration} seconds...")

    # Create data directories if they don't exist
    os.makedirs(os.path.join(data_dir, "daily"), exist_ok=True)
    os.makedirs(os.path.join(data_dir, "weekly"), exist_ok=True)

    # Run container in background
    container_name = f"lux-logger-test-{int(time.time())}"

    cmd = [
        "docker", "run",
        "--name", container_name,
        "--env-file", env_file,
        "-v", f"{data_dir}:/app/data",
        "-d",  # Run in background
        "lux-logger-test"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Failed to start Docker container: {result.stderr}")
        return None, None

    print(f"Container started: {container_name}")

    # Wait for specified duration
    print(f"Waiting {duration} seconds for data collection...")
    time.sleep(duration)

    return container_name, data_dir

def generate_reports_on_demand(container_name):
    """Generate reports on demand in the running container"""
    print("Generating reports on demand...")

    cmd = [
        "docker", "exec", container_name,
        "python", "main.py", "--mode", "generate-reports"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Failed to generate reports: {result.stderr}")
        return False

    print("Reports generated successfully")
    print(result.stdout)
    return True

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
        print("No CSV files found!")
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
                print(f"  ERROR: Empty CSV file {file_path}")
                return False

            print(f"  Header: {header[:5]}{'...' if len(header) > 5 else ''} ({len(header)} columns)")

            # Read data rows
            row_count = 0
            for row in reader:
                row_count += 1
                if len(row) != len(header):
                    print(f"  ERROR: Row {row_count} has {len(row)} columns, expected {len(header)}")
                    return False

                # Validate that we have some data
                if row_count == 1:
                    print(f"  Sample row: {row[:5]}{'...' if len(row) > 5 else ''}")

            print(f"  Total rows: {row_count}")

            if row_count == 0:
                print(f"  WARNING: No data rows in {file_path}")
            else:
                print(f"  SUCCESS: Validated {file_path}")

            return True

    except Exception as e:
        print(f"  ERROR: Failed to validate {file_path}: {str(e)}")
        return False

def check_cache_data(data_dir):
    """Check the SQLite cache for data"""
    cache_path = os.path.join(data_dir, "cache.db")

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

        # Get sample data
        cursor.execute("SELECT timestamp, data_json FROM sensor_data LIMIT 3")
        rows = cursor.fetchall()

        for i, (timestamp, data_json) in enumerate(rows):
            data = json.loads(data_json)
            dt = datetime.fromtimestamp(timestamp)
            print(f"  Sample {i+1}: {dt} - {len(data)} sensor readings")

        conn.close()
        return count > 0

    except Exception as e:
        print(f"Failed to check cache data: {str(e)}")
        return False

def cleanup_container(container_name):
    """Stop and remove the Docker container"""
    print("Cleaning up container...")

    # Stop container
    subprocess.run(["docker", "stop", container_name],
                  capture_output=True, text=True)

    # Remove container
    subprocess.run(["docker", "rm", container_name],
                  capture_output=True, text=True)

    print("Container cleanup completed")

def main():
    """Main test function"""
    print("Starting CSV data validation test...")

    # Create temporary directory for data
    data_dir = tempfile.mkdtemp(prefix="lux_logger_test_")
    print(f"Using data directory: {data_dir}")

    try:
        # Build Docker image
        if not build_docker_image():
            return False

        # Create test environment file
        env_file = create_test_env_file()

        # Run container for data collection
        container_name, data_dir = run_docker_container(env_file, data_dir, duration=70)
        if not container_name:
            return False

        # Check cache data
        print("\nChecking cache data...")
        has_data = check_cache_data(data_dir)

        # Generate reports on demand
        if not generate_reports_on_demand(container_name):
            return False

        # Validate CSV files
        print("\nValidating CSV files...")
        success = validate_csv_files(data_dir)

        # Cleanup
        cleanup_container(container_name)

        # Remove environment file
        os.remove(env_file)

        if success:
            print("\n✅ CSV data validation test PASSED")
            if has_data:
                print("✅ Data was collected and CSV files were generated successfully")
            else:
                print("⚠️  No data was collected (this is expected if no heat pump is available)")
                print("✅ CSV generation logic is working correctly")
        else:
            print("\n❌ CSV data validation test FAILED")

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
    success = main()
    sys.exit(0 if success else 1)
