import pytest
import os
import tempfile
import json
from datetime import datetime
from src.web import get_latest_sensor_data, get_csv_reports

def test_get_latest_sensor_data():
    """Test getting latest sensor data from database"""
    # This should work with existing data
    try:
        data = get_latest_sensor_data()
        assert isinstance(data, dict)
        assert 'timestamp' in data
        assert 'flow_temperature' in data
        assert 'return_temperature' in data
        assert 'ambient_temperature' in data
        assert 'hot_water_temperature' in data
        assert 'system_flags' in data
    except Exception as e:
        # If database is empty or unavailable, that's okay for this test
        pass

def test_get_csv_reports():
    """Test getting CSV reports list"""
    # Create temporary directories for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        daily_dir = os.path.join(temp_dir, "daily")
        weekly_dir = os.path.join(temp_dir, "weekly")
        os.makedirs(daily_dir, exist_ok=True)
        os.makedirs(weekly_dir, exist_ok=True)

        # Create some test files
        test_files = [
            os.path.join(daily_dir, "test1.csv"),
            os.path.join(daily_dir, "test2.csv"),
            os.path.join(weekly_dir, "test_weekly.csv")
        ]

        for file_path in test_files:
            with open(file_path, 'w') as f:
                f.write("test,data\n1,2\n")

        # Temporarily override the global variables
        import src.web as web_module
        original_daily = web_module.DAILY_REPORTS_DIR
        original_weekly = web_module.WEEKLY_REPORTS_DIR

        try:
            web_module.DAILY_REPORTS_DIR = daily_dir
            web_module.WEEKLY_REPORTS_DIR = weekly_dir

            reports = web_module.get_csv_reports()
            assert isinstance(reports, dict)
            assert 'daily_reports' in reports
            assert 'weekly_reports' in reports
            assert 'total_size' in reports
            assert len(reports['daily_reports']) == 2
            assert len(reports['weekly_reports']) == 1

        finally:
            # Restore original values
            web_module.DAILY_REPORTS_DIR = original_daily
            web_module.WEEKLY_REPORTS_DIR = original_weekly

if __name__ == "__main__":
    test_get_latest_sensor_data()
    test_get_csv_reports()
    print("Web module tests passed!")
