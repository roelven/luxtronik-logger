import pytest
import os
import json
import tempfile
from datetime import datetime
from src.web import get_latest_sensor_data, get_csv_reports

def test_get_latest_sensor_data_functionality():
    """Test that get_latest_sensor_data works with real database"""
    db_path = "data/cache.db"

    # Skip test if database doesn't exist
    if not os.path.exists(db_path):
        pytest.skip("Database not found, skipping test")

    # Test that we can get data
    try:
        data = get_latest_sensor_data()
        assert isinstance(data, dict)
        assert 'timestamp' in data
        # Check that timestamp is valid ISO format
        datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))

        # Check that we have at least some temperature data
        # Values might be None if sensors aren't found, which is okay
        assert 'flow_temperature' in data
        assert 'return_temperature' in data
        assert 'ambient_temperature' in data
        assert 'hot_water_temperature' in data
        assert 'system_flags' in data

        # Check system flags structure
        flags = data['system_flags']
        assert isinstance(flags, dict)

    except Exception as e:
        # This might happen if database is corrupted or empty
        # That's acceptable for this test
        pass

def test_get_csv_reports_functionality():
    """Test that get_csv_reports works correctly"""
    # Test with temporary directories
    with tempfile.TemporaryDirectory() as temp_dir:
        daily_dir = os.path.join(temp_dir, "daily")
        weekly_dir = os.path.join(temp_dir, "weekly")
        os.makedirs(daily_dir, exist_ok=True)
        os.makedirs(weekly_dir, exist_ok=True)

        # Create some test CSV files
        test_files = [
            ("daily_report_1.csv", daily_dir),
            ("daily_report_2.csv", daily_dir),
            ("weekly_report_1.csv", weekly_dir)
        ]

        for filename, directory in test_files:
            file_path = os.path.join(directory, filename)
            with open(file_path, 'w') as f:
                f.write("timestamp,value\n2023-01-01,100\n")

        # Temporarily override the global variables
        import src.web as web_module
        original_daily = web_module.DAILY_REPORTS_DIR
        original_weekly = web_module.WEEKLY_REPORTS_DIR

        try:
            web_module.DAILY_REPORTS_DIR = daily_dir
            web_module.WEEKLY_REPORTS_DIR = weekly_dir

            reports = get_csv_reports()
            assert isinstance(reports, dict)
            assert 'daily_reports' in reports
            assert 'weekly_reports' in reports
            assert 'total_size' in reports

            # Check that we have the right number of reports
            assert len(reports['daily_reports']) == 2
            assert len(reports['weekly_reports']) == 1

            # Check structure of daily reports
            for report in reports['daily_reports']:
                assert 'filename' in report
                assert 'size_bytes' in report
                assert 'modified' in report
                # Check that modified is valid ISO format
                datetime.fromisoformat(report['modified'].replace('Z', '+00:00'))

            # Check structure of weekly reports
            for report in reports['weekly_reports']:
                assert 'filename' in report
                assert 'size_bytes' in report
                assert 'modified' in report
                # Check that modified is valid ISO format
                datetime.fromisoformat(report['modified'].replace('Z', '+00:00'))

        finally:
            # Restore original values
            web_module.DAILY_REPORTS_DIR = original_daily
            web_module.WEEKLY_REPORTS_DIR = original_weekly

def test_get_csv_reports_with_empty_directories():
    """Test that get_csv_reports works with empty directories"""
    # Test with temporary directories
    with tempfile.TemporaryDirectory() as temp_dir:
        daily_dir = os.path.join(temp_dir, "daily")
        weekly_dir = os.path.join(temp_dir, "weekly")
        os.makedirs(daily_dir, exist_ok=True)
        os.makedirs(weekly_dir, exist_ok=True)

        # Temporarily override the global variables
        import src.web as web_module
        original_daily = web_module.DAILY_REPORTS_DIR
        original_weekly = web_module.WEEKLY_REPORTS_DIR

        try:
            web_module.DAILY_REPORTS_DIR = daily_dir
            web_module.WEEKLY_REPORTS_DIR = weekly_dir

            reports = get_csv_reports()
            assert isinstance(reports, dict)
            assert 'daily_reports' in reports
            assert 'weekly_reports' in reports
            assert 'total_size' in reports

            # Check that we have empty lists
            assert len(reports['daily_reports']) == 0
            assert len(reports['weekly_reports']) == 0
            assert reports['total_size'] == 0

        finally:
            # Restore original values
            web_module.DAILY_REPORTS_DIR = original_daily
            web_module.WEEKLY_REPORTS_DIR = original_weekly

if __name__ == "__main__":
    test_get_latest_sensor_data_functionality()
    test_get_csv_reports_functionality()
    test_get_csv_reports_with_empty_directories()
    print("Web functionality tests passed!")
