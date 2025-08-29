import pytest
import os
from datetime import datetime
from src.csvgen import CSVGenerator
from unittest.mock import patch

class TestCSVHeaderReadability:
    def test_readable_headers_enabled(self, tmp_path):
        # Create a test environment with readable headers enabled
        output_dirs = {"daily": str(tmp_path / "daily"), "weekly": str(tmp_path / "weekly")}

        # Test data with raw sensor IDs
        test_data = [
            {
                "timestamp": datetime.now(),
                "data": {
                    "calculations.ID_WEB_Temperatur_TVL": 45.0,
                    "calculations.ID_WEB_Temperatur_TRL": 35.0
                }
            }
        ]

        # Test with readable headers enabled
        with patch.dict("os.environ", {"READABLE_HEADERS": "true"}):
            generator = CSVGenerator(output_dirs)
            filepath = generator.generate_daily_csv(test_data, datetime.now())

            # Verify the file exists
            assert os.path.exists(filepath)

            # Read the CSV and verify headers are readable
            with open(filepath) as f:
                first_line = f.readline().strip()
                assert "Flow Temperature" in first_line  # Mapped name
                assert "Return Temperature" in first_line  # Mapped name
                assert "calculations.ID_WEB_Temperatur_TVL" not in first_line  # Original ID not present

    def test_readable_headers_disabled(self, tmp_path):
        # Test with readable headers disabled (default behavior)
        output_dirs = {"daily": str(tmp_path / "daily"), "weekly": str(tmp_path / "weekly")}

        test_data = [
            {
                "timestamp": datetime.now(),
                "data": {
                    "calculations.ID_WEB_Temperatur_TVL": 45.0,
                    "calculations.ID_WEB_Temperatur_TRL": 35.0
                }
            }
        ]

        # Test with readable headers disabled
        with patch.dict("os.environ", {"READABLE_HEADERS": "false"}):
            generator = CSVGenerator(output_dirs)
            filepath = generator.generate_daily_csv(test_data, datetime.now())

            # Verify the file exists
            assert os.path.exists(filepath)

            # Read the CSV and verify headers are raw IDs
            with open(filepath) as f:
                first_line = f.readline().strip()
                assert "calculations.ID_WEB_Temperatur_TVL" in first_line  # Original ID present
                assert "Flow Temperature" not in first_line  # Mapped name not present

    def test_readable_headers_fallback(self, tmp_path):
        # Test fallback behavior when a sensor ID doesn't have a mapping
        output_dirs = {"daily": str(tmp_path / "daily"), "weekly": str(tmp_path / "weekly")}

        test_data = [
            {
                "timestamp": datetime.now(),
                "data": {
                    "calculations.ID_WEB_Temperatur_TVL": 45.0,  # Has mapping
                    "calculations.ID_WEB_UnknownSensor": 35.0  # No mapping
                }
            }
        ]

        # Test with readable headers enabled - unmapped sensors should be excluded
        with patch.dict("os.environ", {"READABLE_HEADERS": "true"}):
            generator = CSVGenerator(output_dirs)
            filepath = generator.generate_daily_csv(test_data, datetime.now())

            # Verify the file exists
            assert os.path.exists(filepath)

            # Read the CSV and verify behavior
            with open(filepath) as f:
                first_line = f.readline().strip()
                assert "Flow Temperature" in first_line  # Mapped name present
                assert "calculations.ID_WEB_UnknownSensor" not in first_line  # Unmapped ID excluded

        # Test with readable headers disabled - all sensors should be included
        with patch.dict("os.environ", {"READABLE_HEADERS": "false"}):
            generator = CSVGenerator(output_dirs)
            filepath = generator.generate_daily_csv(test_data, datetime.now())

            # Verify the file exists
            assert os.path.exists(filepath)

            # Read the CSV and verify all sensors included
            with open(filepath) as f:
                first_line = f.readline().strip()
                assert "calculations.ID_WEB_Temperatur_TVL" in first_line  # Raw ID present
                assert "calculations.ID_WEB_UnknownSensor" in first_line  # Raw ID present

    def test_data_values_unchanged(self, tmp_path):
        # Verify that data values remain unchanged when using readable headers
        output_dirs = {"daily": str(tmp_path / "daily"), "weekly": str(tmp_path / "weekly")}

        test_data = [
            {
                "timestamp": datetime.now(),
                "data": {
                    "calculations.ID_WEB_Temperatur_TVL": 45.0,
                    "calculations.ID_WEB_Temperatur_TRL": 35.0
                }
            }
        ]

        # Test with readable headers enabled
        with patch.dict("os.environ", {"READABLE_HEADERS": "true"}):
            generator = CSVGenerator(output_dirs)
            filepath = generator.generate_daily_csv(test_data, datetime.now())

            # Verify the file exists
            assert os.path.exists(filepath)

            # Read the CSV and verify data values are unchanged
            with open(filepath) as f:
                rows = list(f.readlines())
                # Skip header row
                data_row = rows[1].strip().split(',')
                assert "45.0" in data_row
                assert "35.0" in data_row

    def test_comprehensive_mappings(self, tmp_path):
        # Test comprehensive mappings for different sensor types
        output_dirs = {"daily": str(tmp_path / "daily"), "weekly": str(tmp_path / "weekly")}

        test_data = [
            {
                "timestamp": datetime.now(),
                "data": {
                    "calculations.ID_WEB_Temperatur_TVL": 45.0,  # Flow Temperature
                    "calculations.ID_WEB_Temperatur_TRL": 35.0,  # Return Temperature
                    "calculations.ID_WEB_Temperatur_TA": 22.0,   # Ambient Temperature
                    "calculations.ID_WEB_Zaehler_BetrZeitVD1": 3600,  # Compressor 1 Operating Time
                    "parameters.ID_Soll_BWS_akt": 50.0,  # Hot Water Setpoint Actual
                    "visibilities.ID_Visi_Heizung": 1,   # Heating
                }
            }
        ]

        # Test with readable headers enabled
        with patch.dict("os.environ", {"READABLE_HEADERS": "true"}):
            generator = CSVGenerator(output_dirs)
            filepath = generator.generate_daily_csv(test_data, datetime.now())

            # Verify the file exists
            assert os.path.exists(filepath)

            # Read the CSV and verify comprehensive mappings
            with open(filepath) as f:
                first_line = f.readline().strip()
                # Check that readable names are used
                assert "Flow Temperature" in first_line
                assert "Return Temperature" in first_line
                assert "Ambient Temperature" in first_line
                assert "Compressor 1 Operating Time" in first_line
                assert "Hot Water Setpoint Actual" in first_line
                assert "Heating" in first_line
                # Check that raw IDs are not present
                assert "ID_WEB_Temperatur_TVL" not in first_line
                assert "ID_WEB_Temperatur_TRL" not in first_line
                assert "ID_WEB_Temperatur_TA" not in first_line
                assert "ID_WEB_Zaehler_BetrZeitVD1" not in first_line
                assert "ID_Soll_BWS_akt" not in first_line
                assert "ID_Visi_Heizung" not in first_line
