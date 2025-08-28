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

        # Test with readable headers enabled
        with patch.dict("os.environ", {"READABLE_HEADERS": "true"}):
            generator = CSVGenerator(output_dirs)
            filepath = generator.generate_daily_csv(test_data, datetime.now())

            # Verify the file exists
            assert os.path.exists(filepath)

            # Read the CSV and verify fallback behavior
            with open(filepath) as f:
                first_line = f.readline().strip()
                assert "Flow Temperature" in first_line  # Mapped name present
                assert "calculations.ID_WEB_UnknownSensor" in first_line  # Unmapped ID present

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
