import pytest
import os
import csv
from datetime import datetime, timedelta
from unittest.mock import patch, mock_open
from src.csvgen import CSVGenerator

class TestCSVGenerator:
    def test_generate_daily_csv(self, tmp_path):
        output_dirs = {"daily": str(tmp_path / "daily"), "weekly": str(tmp_path / "weekly")}
        generator = CSVGenerator(output_dirs)

        test_data = [
            {"timestamp": datetime.now(), "data": {"temp": 45.0, "pressure": 2.1}},
            {"timestamp": datetime.now() - timedelta(minutes=5), "data": {"temp": 44.5, "pressure": 2.0}}
        ]

        filepath = generator.generate_daily_csv(test_data, datetime.now())
        assert os.path.exists(filepath)
        assert "_daily.csv" in filepath

        with open(filepath) as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 2
            assert float(rows[0]["temp"]) == 45.0

    def test_generate_weekly_csv(self, tmp_path):
        output_dirs = {"daily": str(tmp_path / "daily"), "weekly": str(tmp_path / "weekly")}
        generator = CSVGenerator(output_dirs)

        test_data = [
            {"timestamp": datetime.now(), "data": {"temp": 45.0}},
            {"timestamp": datetime.now() - timedelta(days=1), "data": {"temp": 44.0}}
        ]

        filepath = generator.generate_weekly_csv(test_data, datetime.now())
        assert os.path.exists(filepath)
        assert "_weekly.csv" in filepath

        with open(filepath) as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 2

    def test_empty_data(self, tmp_path):
        output_dirs = {"daily": str(tmp_path / "daily"), "weekly": str(tmp_path / "weekly")}
        generator = CSVGenerator(output_dirs)

        with patch("logging.Logger.warning") as mock_warning:
            filepath = generator.generate_daily_csv([], datetime.now())
            mock_warning.assert_called_once()
            assert not os.path.exists(filepath)

    def test_write_error(self, tmp_path):
        output_dirs = {"daily": str(tmp_path / "daily"), "weekly": str(tmp_path / "weekly")}
        generator = CSVGenerator(output_dirs)

        test_data = [{"timestamp": datetime.now(), "data": {"temp": 45.0}}]

        with patch("builtins.open", side_effect=Exception("Test error")):
            with patch("logging.Logger.error") as mock_error:
                with pytest.raises(Exception):
                    generator.generate_daily_csv(test_data, datetime.now())
                # Check that error was called twice (original error + error type)
                assert mock_error.call_count == 2

    def test_cleanup_old_csvs(self, tmp_path):
        output_dirs = {"daily": str(tmp_path / "daily"), "weekly": str(tmp_path / "weekly")}
        generator = CSVGenerator(output_dirs)

        # Create test CSV files with different dates
        import time
        daily_dir = tmp_path / "daily"
        daily_dir.mkdir(exist_ok=True)

        # Create a recent file (should not be deleted)
        recent_file = daily_dir / "recent_daily.csv"
        recent_file.write_text("test")

        # Create an old file (should be deleted)
        old_file = daily_dir / "old_daily.csv"
        old_file.write_text("test")
        # Set modification time to 31 days ago
        old_time = time.time() - (31 * 24 * 60 * 60)
        os.utime(old_file, (old_time, old_time))

        with patch("logging.Logger.info") as mock_info:
            generator.cleanup_old_csvs(30)
            # Check that old file was deleted
            assert not old_file.exists()
            # Check that recent file still exists
            assert recent_file.exists()
            # Check that info logs were called
            assert mock_info.call_count >= 1

    def test_cleanup_old_csvs_invalid_retention(self, tmp_path):
        output_dirs = {"daily": str(tmp_path / "daily"), "weekly": str(tmp_path / "weekly")}
        generator = CSVGenerator(output_dirs)

        with patch("logging.Logger.warning") as mock_warning:
            generator.cleanup_old_csvs(0)
            mock_warning.assert_called_once()
