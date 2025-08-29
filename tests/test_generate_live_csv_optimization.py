import pytest
import os
import sys
import tempfile
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Add src to path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from storage import DataStorage
from client import HeatPumpClient

class TestGenerateLiveCsvOptimization:
    def setup_method(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.cache_path = os.path.join(self.test_dir, "cache.db")
        self.output_dir = os.path.join(self.test_dir, "output")
        os.makedirs(self.output_dir, exist_ok=True)

    def teardown_method(self):
        """Clean up test environment"""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_cache_query_for_recent_data(self):
        """Test that we can query recent data from cache"""
        # Create storage with some test data
        storage = DataStorage(self.cache_path, enable_validation=False)

        # Create realistic sensor data (mock the full set)
        test_data = {}
        # Add enough entries to pass validation
        for i in range(200):  # More than minimum 100 required
            test_data[f"calculations.{i}"] = float(i)

        # Add some specific temperature sensors to pass validation
        test_data["calculations.ID_WEB_Temperatur_TVL"] = 45.0
        test_data["calculations.ID_WEB_Temperatur_TRL"] = 40.0
        test_data["calculations.ID_WEB_Temperatur_TA"] = 22.0

        test_time = datetime.now()
        storage.add(test_time, test_data)
        storage.flush()

        # Query recent data (within last hour)
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=1)
        recent_data = storage.query(start_time, end_time)

        assert len(recent_data) == 1
        assert recent_data[0]["data"]["calculations.ID_WEB_Temperatur_TVL"] == 45.0

    def test_cache_has_sufficient_data(self):
        """Test checking if cache has sufficient recent data"""
        from datetime import datetime, timedelta

        # Create storage with recent data
        storage = DataStorage(self.cache_path, enable_validation=False)

        # Create realistic sensor data
        test_data = {}
        # Add enough entries to pass validation
        for i in range(200):  # More than minimum 100 required
            test_data[f"calculations.{i}"] = float(i)

        # Add some specific temperature sensors to pass validation
        test_data["calculations.ID_WEB_Temperatur_TVL"] = 45.0

        # Add data from 10 minutes ago (should be sufficient)
        recent_time = datetime.now() - timedelta(minutes=10)
        storage.add(recent_time, test_data)
        storage.flush()

        # Check if we have data within last 30 minutes
        thirty_minutes_ago = datetime.now() - timedelta(minutes=30)
        end_time = datetime.now()

        recent_data = storage.query(thirty_minutes_ago, end_time)
        assert len(recent_data) > 0

    def test_cache_lacks_sufficient_data(self):
        """Test checking if cache lacks sufficient recent data"""
        from datetime import datetime, timedelta

        # Create storage
        storage = DataStorage(self.cache_path)

        # Add data from 2 hours ago (should be insufficient)
        old_time = datetime.now() - timedelta(hours=2)
        test_data = {"calculations.ID_WEB_Temperatur_TVL": 45.0}

        storage.add(old_time, test_data)
        storage.flush()

        # Check if we have data within last 30 minutes
        thirty_minutes_ago = datetime.now() - timedelta(minutes=30)
        end_time = datetime.now()

        recent_data = storage.query(thirty_minutes_ago, end_time)
        assert len(recent_data) == 0
