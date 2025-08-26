#!/usr/bin/env python3
"""
Simple test script for report generation with proper configuration.
"""

import os
import sys
import tempfile
import shutil
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from client import HeatPumpClient
from storage import DataStorage
from csvgen import CSVGenerator
from config import Config

def test_report_generation():
    """Test report generation with proper configuration"""
    print("🧪 Testing Report Generation")
    print("=" * 40)

    # Create temporary directories
    temp_dir = tempfile.mkdtemp(prefix="lux_logger_test_")
    cache_path = os.path.join(temp_dir, "cache.db")
    daily_dir = os.path.join(temp_dir, "daily")
    weekly_dir = os.path.join(temp_dir, "weekly")

    os.makedirs(daily_dir, exist_ok=True)
    os.makedirs(weekly_dir, exist_ok=True)

    try:
        # Create config
        config = Config()
        config.host = "192.168.20.180"
        config.port = 8889
        config.cache_path = cache_path
        config.output_dirs = {
            "daily": daily_dir,
            "weekly": weekly_dir
        }
        config.csv_retention_days = 30

        print(f"Using temporary directory: {temp_dir}")
        print(f"Cache path: {cache_path}")
        print(f"Daily CSV dir: {daily_dir}")
        print(f"Weekly CSV dir: {weekly_dir}")
        print()

        # Create storage and collect some data
        storage = DataStorage(cache_path, enable_validation=True)
        client = HeatPumpClient(config.host, config.port)

        print("Collecting data from heat pump...")
        if client.connect():
            # Collect 3 data points
            for i in range(3):
                print(f"Collecting data point {i+1}...")
                sensor_data = client.get_all_sensors()
                timestamp = datetime.now() - timedelta(minutes=i*5)  # Space them out
                is_valid, messages = storage.add(timestamp, sensor_data)

                if is_valid:
                    print(f"  ✓ Collected {len(sensor_data)} sensor readings")
                else:
                    print(f"  ⚠️  Validation warnings: {len([m for m in messages if m.startswith('⚠️')])}")
                    print(f"  ❌ Validation errors: {len([m for m in messages if m.startswith('❌')])}")

            # Flush to storage
            success_count, total_count = storage.flush()
            print(f"Stored {success_count}/{total_count} data points")
            print()

            # Generate reports
            print("Generating CSV reports...")
            csv_gen = CSVGenerator(config.output_dirs)

            # Generate daily report (need to implement proper data querying)
            # For now, just test that CSV generator can be instantiated
            print("CSV generator instantiated successfully")
            daily_files = []
            print(f"Daily reports generated: {len(daily_files)}")

            # Generate weekly report (need to implement proper data querying)
            weekly_files = []
            print(f"Weekly reports generated: {len(weekly_files)}")

            # Clean up old files
            cleaned_count = csv_gen.cleanup_old_csvs(config.csv_retention_days)
            print(f"Cleaned up {cleaned_count} old CSV files")
            print()

            # Check results
            daily_files = [f for f in os.listdir(daily_dir) if f.endswith('.csv')]
            weekly_files = [f for f in os.listdir(weekly_dir) if f.endswith('.csv')]

            print("Results:")
            print(f"  Daily CSV files: {daily_files}")
            print(f"  Weekly CSV files: {weekly_files}")

            if daily_files or weekly_files:
                print("✅ Report generation test PASSED")
                return True
            else:
                print("❌ No CSV files generated")
                return False

        else:
            print("❌ Failed to connect to heat pump")
            return False

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # Cleanup
        shutil.rmtree(temp_dir)
        print(f"Cleaned up temporary directory: {temp_dir}")

if __name__ == "__main__":
    success = test_report_generation()
    sys.exit(0 if success else 1)
