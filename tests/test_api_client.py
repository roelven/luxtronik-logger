#!/usr/bin/env python3
"""
Simple test client for the Luxtronik Logger API
"""
import requests
import json

def test_api():
    """Test the API endpoints"""
    base_url = "http://localhost:8080"

    print("Testing Luxtronik Logger API...")

    # Test root endpoint
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✓ Root endpoint working")
            print(f"  Response: {response.json()}")
        else:
            print(f"✗ Root endpoint failed with status {response.status_code}")
    except Exception as e:
        print(f"✗ Root endpoint error: {e}")

    # Test status endpoint
    try:
        response = requests.get(f"{base_url}/status", timeout=5)
        if response.status_code == 200:
            print("✓ Status endpoint working")
            data = response.json()
            print(f"  Timestamp: {data.get('timestamp', 'N/A')}")
            print(f"  Flow temp: {data.get('flow_temperature', 'N/A')} °C")
        else:
            print(f"✗ Status endpoint failed with status {response.status_code}")
    except Exception as e:
        print(f"✗ Status endpoint error: {e}")

    # Test reports endpoint
    try:
        response = requests.get(f"{base_url}/reports", timeout=5)
        if response.status_code == 200:
            print("✓ Reports endpoint working")
            data = response.json()
            print(f"  Daily reports: {len(data.get('daily_reports', []))}")
            print(f"  Weekly reports: {len(data.get('weekly_reports', []))}")
        else:
            print(f"✗ Reports endpoint failed with status {response.status_code}")
    except Exception as e:
        print(f"✗ Reports endpoint error: {e}")

if __name__ == "__main__":
    test_api()
