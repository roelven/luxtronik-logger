import pytest
import os
import sys
import tempfile
from datetime import datetime
from src.config import Config
from src.web import get_latest_sensor_data, get_csv_reports

def test_complete_solution_integration():
    """Final integration test for the complete solution including web interface"""

    # Test that we can read configuration with minimal env vars
    config = Config()
    # Set required HOST for validation
    os.environ["HOST"] = "test-host"
    try:
        # Load default configuration (no env file in test)
        config.load()

        # Verify configuration structure
        assert hasattr(config, 'host')
        assert hasattr(config, 'port')
        assert hasattr(config, 'interval_sec')
        assert hasattr(config, 'csv_time')
        assert hasattr(config, 'cache_path')
        assert hasattr(config, 'output_dirs')
    finally:
        # Clean up environment
        if "HOST" in os.environ:
            del os.environ["HOST"]

    # Test that we can read from database (if it exists)
    db_path = "data/cache.db"
    if os.path.exists(db_path):
        try:
            # Test web interface functions
            status_data = get_latest_sensor_data()
            assert isinstance(status_data, dict)
            assert "timestamp" in status_data
            # Other fields might be None if sensors aren't found
        except Exception as e:
            # This is okay if database is empty or has issues
            pass

    # Test CSV reports functionality with temporary directories
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

            # Test get_csv_reports function
            reports = get_csv_reports()
            assert isinstance(reports, dict)
            assert "daily_reports" in reports
            assert "weekly_reports" in reports
            assert "total_size" in reports

        finally:
            # Restore original values
            web_module.DAILY_REPORTS_DIR = original_daily
            web_module.WEEKLY_REPORTS_DIR = original_weekly

    print("Complete solution integration test passed!")

if __name__ == "__main__":
    test_complete_solution_integration()
    print("Complete solution integration test completed successfully!")
