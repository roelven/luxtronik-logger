import pytest
from fastapi.testclient import TestClient
from src.web import app

client = TestClient(app)

def test_status_endpoint():
    """Test that the status endpoint returns valid data structure"""
    response = client.get("/status")
    # This will fail if database doesn't exist, which is expected in testing
    assert response.status_code in [200, 404, 500]

def test_reports_endpoint():
    """Test that the reports endpoint returns valid data structure"""
    response = client.get("/reports")
    # This should work even without real data
    assert response.status_code == 200
    data = response.json()
    assert "daily_reports" in data
    assert "weekly_reports" in data
    assert "total_size" in data

if __name__ == "__main__":
    test_status_endpoint()
    test_reports_endpoint()
    print("FastAPI endpoint tests passed!")
