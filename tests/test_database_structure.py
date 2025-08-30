import sqlite3
import json
from datetime import datetime
import os

def test_database_structure():
    """Test to examine the database structure and sample data"""
    db_path = "data/cache.db"

    if not os.path.exists(db_path):
        print(f"Database file {db_path} does not exist")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get the latest record
    cursor.execute("SELECT timestamp, data_json FROM sensor_data ORDER BY timestamp DESC LIMIT 1")
    row = cursor.fetchone()

    if row:
        timestamp, data_json = row
        data = json.loads(data_json)

        print(f"Latest timestamp: {datetime.fromtimestamp(timestamp)}")
        print(f"Number of sensors: {len(data)}")
        print("First 10 sensors:")
        for i, (key, value) in enumerate(list(data.items())[:10]):
            print(f"  {key}: {value}")

        # Look for temperature sensors specifically
        temp_sensors = {k: v for k, v in data.items() if 'Temperatur' in k}
        print(f"\nTemperature sensors found: {len(temp_sensors)}")
        for i, (key, value) in enumerate(list(temp_sensors.items())[:5]):
            print(f"  {key}: {value}")
    else:
        print("No data found in database")

    conn.close()

if __name__ == "__main__":
    test_database_structure()
