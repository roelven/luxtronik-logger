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
                mock_error.assert_called_once()