import sqlite3
import json
from datetime import datetime
import os
import pytest

def test_read_latest_sensor_data():
    """Test reading the latest sensor data from the database"""
    db_path = "data/cache.db"

    # Check that database exists
    assert os.path.exists(db_path), f"Database file {db_path} does not exist"

    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get the latest record
    cursor.execute("SELECT timestamp, data_json FROM sensor_data ORDER BY timestamp DESC LIMIT 1")
    row = cursor.fetchone()

    # Verify we got data
    assert row is not None, "No data found in database"

    timestamp, data_json = row
    data = json.loads(data_json)

    # Verify timestamp is valid
    assert isinstance(timestamp, (int, float)), "Timestamp should be a number"
    dt = datetime.fromtimestamp(timestamp)
    assert isinstance(dt, datetime), "Timestamp should convert to datetime"

    # Verify we have sensor data
    assert isinstance(data, dict), "Data should be a dictionary"
    assert len(data) > 1000, f"Expected 1800+ sensors, got {len(data)}"

    # Verify we have some key temperature sensors
    temp_sensors = {k: v for k, v in data.items() if 'Temperatur' in k}
    assert len(temp_sensors) > 10, f"Expected 10+ temperature sensors, got {len(temp_sensors)}"

    # Verify temperature values are reasonable
    flow_temp = data.get('calculations.ID_WEB_Temperatur_TVL')
    if flow_temp is not None:
        assert isinstance(flow_temp, (int, float)), "Flow temperature should be numeric"
        assert -50 < flow_temp < 100, f"Flow temperature {flow_temp} seems unreasonable"

    conn.close()

def test_readable_sensor_names():
    """Test that we can map sensor IDs to readable names"""
    from src.csvgen import CSVGenerator

    # Check that we have mappings
    assert hasattr(CSVGenerator, 'SENSOR_NAME_MAPPINGS'), "SENSOR_NAME_MAPPINGS should exist"
    mappings = CSVGenerator.SENSOR_NAME_MAPPINGS
    assert len(mappings) > 100, f"Expected 100+ sensor mappings, got {len(mappings)}"

    # Check some specific mappings
    expected_mappings = {
        "calculations.ID_WEB_Temperatur_TVL": "Flow Temperature",
        "calculations.ID_WEB_Temperatur_TRL": "Return Temperature",
        "calculations.ID_WEB_Temperatur_TA": "Ambient Temperature"
    }

    for sensor_id, readable_name in expected_mappings.items():
        assert sensor_id in mappings, f"Missing mapping for {sensor_id}"
        assert mappings[sensor_id] == readable_name, f"Wrong mapping for {sensor_id}"

if __name__ == "__main__":
    test_read_latest_sensor_data()
    test_readable_sensor_names()
    print("All tests passed!")
