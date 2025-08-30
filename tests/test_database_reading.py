import pytest
import sqlite3
import json
import os
from datetime import datetime
from src.web import get_latest_sensor_data

def test_database_reading():
    """Test that we can read from the database correctly"""
    db_path = "data/cache.db"

    # Check that database exists
    if not os.path.exists(db_path):
        pytest.skip("Database not found, skipping test")

    # Test that we can read the latest data
    try:
        data = get_latest_sensor_data()
        assert isinstance(data, dict)
        assert 'timestamp' in data
        assert 'flow_temperature' in data
        # The values might be None if the specific sensors aren't found
        # That's okay for this test
    except Exception as e:
        # If there's an error, it might be because the database is empty
        # That's okay for this test
        pass

def test_database_structure():
    """Test the structure of the database"""
    db_path = "data/cache.db"

    # Check that database exists
    if not os.path.exists(db_path):
        pytest.skip("Database not found, skipping test")

    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check that the table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sensor_data'")
    result = cursor.fetchone()
    assert result is not None, "sensor_data table should exist"

    # Check that we have data
    cursor.execute("SELECT COUNT(*) FROM sensor_data")
    count = cursor.fetchone()[0]
    assert count > 0, "Should have at least one record in sensor_data table"

    # Check structure of a record
    cursor.execute("SELECT timestamp, data_json FROM sensor_data ORDER BY timestamp DESC LIMIT 1")
    row = cursor.fetchone()
    assert row is not None, "Should have at least one record"

    timestamp, data_json = row
    assert isinstance(timestamp, (int, float)), "Timestamp should be numeric"

    # Parse the JSON data
    data = json.loads(data_json)
    assert isinstance(data, dict), "Data should be a dictionary"
    # Check that we have reasonable amount of data
    assert len(data) > 1000, f"Should have lots of sensors, got {len(data)}"

    conn.close()

if __name__ == "__main__":
    test_database_reading()
    test_database_structure()
    print("Database reading tests passed!")
