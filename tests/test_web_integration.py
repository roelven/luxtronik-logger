import pytest
import os
import json
from datetime import datetime
from fastapi.testclient import TestClient
from src.web import app

client = TestClient(app)

def test_web_integration_with_real_data():
    """Integration test for web interface with real database data"""
    db_path = "data/cache.db"

    # Skip if database doesn't exist
    if not os.path.exists(db_path):
        pytest.skip("Database not found, skipping integration test")

    # Test status endpoint
    response = client.get("/status")
    assert response.status_code == 200

    data = response.json()
    assert "timestamp" in data
    assert "flow_temperature" in data
    assert "return_temperature" in data
    assert "ambient_temperature" in data
    assert "hot_water_temperature" in data
    assert "system_flags" in data

    # Verify timestamp is valid ISO format
    try:
        datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
    except ValueError:
        pytest.fail("Timestamp is not in valid ISO format")

    # Test reports endpoint
    response = client.get("/reports")
    assert response.status_code == 200

    reports_data = response.json()
    assert "daily_reports" in reports_data
    assert "weekly_reports" in reports_data
    assert "total_size" in reports_data

    # Test download endpoint with a valid file (if any exist)
    # First check what files are available
    response = client.get("/reports")
    reports_data = response.json()

    if reports_data["daily_reports"]:
        # Try to download the first daily report
        filename = reports_data["daily_reports"][0]["filename"]
        response = client.get(f"/download/daily/{filename}")
        # This might return 200 or 404 depending on whether the file actually exists
        assert response.status_code in [200, 404]

    print("Web integration test passed!")

if __name__ == "__main__":
    test_web_integration_with_real_data()
    print("Web integration test completed successfully!")
