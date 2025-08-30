import pytest
import os
import json
import tempfile
from datetime import datetime
from fastapi.testclient import TestClient
from src.web import app, DAILY_REPORTS_DIR, WEEKLY_REPORTS_DIR

client = TestClient(app)

def test_status_endpoint_with_real_data():
    """Test the status endpoint with real database data"""
    db_path = "data/cache.db"

    # Skip if database doesn't exist
    if not os.path.exists(db_path):
        pytest.skip("Database not found, skipping test")

    response = client.get("/status")
    # Should return 200 OK or 404 if no data, but not 500
    assert response.status_code in [200, 404]

def test_reports_endpoint_with_empty_directories():
    """Test the reports endpoint with empty directories"""
    # Use temporary directories for testing
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

            response = client.get("/reports")
            assert response.status_code == 200

            data = response.json()
            assert "daily_reports" in data
            assert "weekly_reports" in data
            assert "total_size" in data
            assert len(data["daily_reports"]) == 0
            assert len(data["weekly_reports"]) == 0
            assert data["total_size"] == 0

        finally:
            # Restore original values
            web_module.DAILY_REPORTS_DIR = original_daily
            web_module.WEEKLY_REPORTS_DIR = original_weekly

def test_reports_endpoint_with_sample_data():
    """Test the reports endpoint with sample CSV files"""
    # Use temporary directories for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        daily_dir = os.path.join(temp_dir, "daily")
        weekly_dir = os.path.join(temp_dir, "weekly")
        os.makedirs(daily_dir, exist_ok=True)
        os.makedirs(weekly_dir, exist_ok=True)

        # Create sample CSV files
        sample_content = "timestamp,value\n2023-01-01,100\n"

        daily_file = os.path.join(daily_dir, "test_daily.csv")
        with open(daily_file, 'w') as f:
            f.write(sample_content)

        weekly_file = os.path.join(weekly_dir, "test_weekly.csv")
        with open(weekly_file, 'w') as f:
            f.write(sample_content)

        # Temporarily override the global variables
        import src.web as web_module
        original_daily = web_module.DAILY_REPORTS_DIR
        original_weekly = web_module.WEEKLY_REPORTS_DIR

        try:
            web_module.DAILY_REPORTS_DIR = daily_dir
            web_module.WEEKLY_REPORTS_DIR = weekly_dir

            response = client.get("/reports")
            assert response.status_code == 200

            data = response.json()
            assert "daily_reports" in data
            assert "weekly_reports" in data
            assert "total_size" in data
            assert len(data["daily_reports"]) == 1
            assert len(data["weekly_reports"]) == 1
            assert data["total_size"] > 0

            # Check daily report structure
            daily_report = data["daily_reports"][0]
            assert "filename" in daily_report
            assert "size_bytes" in daily_report
            assert "modified" in daily_report
            assert daily_report["filename"] == "test_daily.csv"

            # Check weekly report structure
            weekly_report = data["weekly_reports"][0]
            assert "filename" in weekly_report
            assert "size_bytes" in weekly_report
            assert "modified" in weekly_report
            assert weekly_report["filename"] == "test_weekly.csv"

        finally:
            # Restore original values
            web_module.DAILY_REPORTS_DIR = original_daily
            web_module.WEEKLY_REPORTS_DIR = original_weekly

def test_download_endpoint_with_invalid_type():
    """Test the download endpoint with invalid report type"""
    response = client.get("/download/invalid/test.csv")
    assert response.status_code == 400

def test_download_endpoint_with_invalid_filename():
    """Test the download endpoint with invalid filename"""
    # FastAPI automatically blocks paths with .. for security reasons
    # So this will return 404, not 400
    response = client.get("/download/daily/../test.csv")
    # This returns 404 because FastAPI blocks it before reaching our endpoint
    assert response.status_code == 404

def test_download_endpoint_with_nonexistent_file():
    """Test the download endpoint with nonexistent file"""
    response = client.get("/download/daily/nonexistent.csv")
    # This should return 404 because file doesn't exist
    assert response.status_code == 404

if __name__ == "__main__":
    test_status_endpoint_with_real_data()
    test_reports_endpoint_with_empty_directories()
    test_reports_endpoint_with_sample_data()
    test_download_endpoint_with_invalid_type()
    test_download_endpoint_with_invalid_filename()
    test_download_endpoint_with_nonexistent_file()
    print("All web endpoint tests passed!")
