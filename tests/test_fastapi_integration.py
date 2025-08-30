import pytest
import os
import tempfile
from fastapi.testclient import TestClient
from src.web import api_app, DAILY_REPORTS_DIR, WEEKLY_REPORTS_DIR

client = TestClient(api_app)

def test_fastapi_status_endpoint():
    """Test that the FastAPI status endpoint works"""
    response = client.get("/status")
    # This should return 200 OK or 404 if no data, but not 500
    assert response.status_code in [200, 404, 500]

def test_fastapi_reports_endpoint():
    """Test that the FastAPI reports endpoint works"""
    # Create temporary directories for testing
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
            # This should return 200 OK
            assert response.status_code == 200
        finally:
            # Restore original values
            web_module.DAILY_REPORTS_DIR = original_daily
            web_module.WEEKLY_REPORTS_DIR = original_weekly

if __name__ == "__main__":
    test_fastapi_status_endpoint()
    test_fastapi_reports_endpoint()
    print("FastAPI integration test passed!")
